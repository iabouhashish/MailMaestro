"""
GmailService module for MailMaestro.

This module provides a class for interacting with the Gmail API, including authentication, fetching unread messages, extracting and OCR'ing images, creating drafts, and managing labels. It is designed to support email automation workflows and integrates with OCR and image extraction utilities.

Classes:
    GmailService: Handles Gmail API authentication and provides methods for email body extraction, unread message retrieval, draft creation, label management, and marking messages as read.

Dependencies:
    - google.oauth2.credentials.Credentials
    - google_auth_oauthlib.flow.InstalledAppFlow
    - googleapiclient.discovery.build
    - mail_maestro.services.ocr.extract_images, ocr_images
    - base64, os, json

Example:
    service = GmailService(token_path, creds_path)
    unread = service.fetch_unread_messages()
    service.create_draft(to, subject, body, thread_id)
    service.add_label(message_id, label_name)
    service.mark_as_read(message_id)
"""

import os
import json
import base64
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from mail_maestro.services.ocr import extract_images, ocr_images

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# PEP 282 logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger("mailmaestro.services.email_client")

class GmailService:
    """
    Service class for interacting with Gmail API and handling email automation tasks.

    Args:
        token_path (str): Path to the OAuth token file.
        creds_path (str): Path to the client credentials JSON file.

    Attributes:
        token_path (str): Path to the OAuth token file.
        creds_path (str): Path to the client credentials JSON file.
        service: Authenticated Gmail API service instance.

    Methods:
        get_preferred_body(payload): Extracts the preferred email body (HTML or plain text).
        fetch_unread_messages(): Retrieves unread messages, extracts bodies and OCR text.
        create_draft(to, subject, body, thread_id): Creates a draft email in Gmail.
        add_label(message_id, label_name): Adds a label to a Gmail message.
        mark_as_read(message_id): Marks a Gmail message as read.
    """
    def __init__(self, token_path, creds_path):
        """
        Initialize the GmailService with authentication.

        Args:
            token_path (str): Path to the OAuth token file.
            creds_path (str): Path to the client credentials JSON file.
        """
        self.token_path = token_path
        self.creds_path = creds_path
        logger.info(f"Initializing GmailService with token_path={token_path}, creds_path={creds_path}")
        self.service = self._init_service()

    def _init_service(self):
        """
        Authenticate and build the Gmail API service.

        Returns:
            googleapiclient.discovery.Resource: Authenticated Gmail API service instance.
        """
        logger.debug("Authenticating Gmail API service.")
        creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        if not creds.valid:
            logger.warning("Credentials not valid, running OAuth flow.")
            flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())
        logger.info("Gmail API service authenticated.")
        return build('gmail', 'v1', credentials=creds)

    def get_preferred_body(self, payload):
        """
        Extract the preferred email body: HTML if present, else plain text.
        Recurses through nested multipart structures as needed.

        Args:
            payload (dict): The email payload from Gmail API.

        Returns:
            str: The decoded email body (HTML or plain text).
        """
        def decode(data):
            return base64.urlsafe_b64decode(data + '=' * (-len(data) % 4)).decode('utf-8', errors='replace')
        # Single part: just get the body
        if 'data' in payload.get('body', {}):
            return decode(payload['body']['data'])

        # Multipart: search for 'text/html', else 'text/plain'
        html = None
        plain = None
        if 'parts' in payload:
            for part in payload['parts']:
                mime = part.get('mimeType', '')
                # Recurse if part is also multipart/*
                if mime.startswith('multipart/'):
                    res = self.get_preferred_body(part)
                    if res:  # Prefer HTML if found in subpart
                        if '<html' in res.lower():
                            return res
                        plain = plain or res
                elif mime == 'text/html' and 'data' in part.get('body', {}):
                    html = decode(part['body']['data'])
                elif mime == 'text/plain' and 'data' in part.get('body', {}):
                    plain = decode(part['body']['data'])
            return html or plain or ''
        return ''  # fallback

    def fetch_unread_messages(self):
        """
        Fetch unread messages from Gmail, extract bodies, images, and OCR text.

        Returns:
            list: List of dictionaries with message details, including OCR text and base64 image URLs.
        """
        logger.info("Fetching unread messages from Gmail.")
        resp = self.service.users().messages().list(userId='me', q='is:unread').execute()
        msgs = resp.get('messages', [])
        logger.info(f"Found {len(msgs)} unread messages.")
        full = []

        for m in msgs:
            try:
                msg = self.service.users().messages().get(userId='me', id=m['id'], format='full').execute()
                payload = msg['payload']
                body = self.get_preferred_body(payload)
                logger.debug(f"Fetched message {m['id']} with subject extraction in progress.")

                # Extract and OCR images
                images = extract_images(msg)
                logger.debug(f"Extracted {len(images)} images from message {m['id']}.")
                ocr_text = ocr_images(images)
                logger.debug(f"OCR text length for message {m['id']}: {len(ocr_text)}")

                # Append OCR to body (for text-only LLM fallback)
                if ocr_text:
                    body += "\n\n[Image OCR Text]\n" + ocr_text

                # Prepare base64 image URLs (for GPT-4o vision input)
                image_data_urls = [
                    f"data:image/png;base64,{base64.b64encode(img).decode('utf-8')}"
                    for img in images
                ]

                subject = next((h['value'] for h in payload['headers'] if h['name'] == 'Subject'), None)
                sender = next((h['value'] for h in payload['headers'] if h['name'] == 'From'), None)

                full.append({
                    'id': m['id'],
                    'sender': sender,
                    'thread_id': msg['threadId'],
                    'subject': subject,
                    'snippet': msg.get('snippet', ''),
                    'body': body,
                    'ocr_text': ocr_text,
                    'image_data_urls': image_data_urls,  # used by LLM vision model
                })

                logger.info(f"Processed message {m['id']} (subject: {subject})")
            except Exception as e:
                logger.error(f"Failed to process message {m.get('id', 'unknown')}: {e}")

        return full
    
    def create_draft(self, to, subject, body, thread_id):
        """
        Create a draft email in Gmail.

        Args:
            to (str): Recipient email address.
            subject (str): Email subject.
            body (str): Email body content.
            thread_id (str): Gmail thread ID to associate the draft with.

        Returns:
            dict: The created draft resource from Gmail API.
        """
        from email.message import EmailMessage
        logger.info(f"Creating draft: to={to}, subject={subject}, thread_id={thread_id}")
        msg = EmailMessage()
        msg['To'] = to
        msg['Subject'] = subject
        msg.set_content(body)
        msg['threadId'] = thread_id
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        try:
            draft = self.service.users().drafts().create(userId='me', body={'message':{'raw':raw,'threadId':thread_id}}).execute()
            logger.info(f"Draft created successfully for thread_id={thread_id}")
            return draft
        except Exception as e:
            logger.error(f"Failed to create draft for thread_id={thread_id}: {e}")
            raise

    def add_label(self, message_id, label_name):
        """
        Add a label to a Gmail message.

        Args:
            message_id (str): The Gmail message ID.
            label_name (str): The name of the label to add.
        """
        logger.info(f"Adding label '{label_name}' to message {message_id}")
        try:
            labels = self.service.users().labels().list(userId='me').execute().get('labels',[])
            lbl = next((l for l in labels if l['name']==label_name), None)
            if lbl:
                self.service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds':[lbl['id']]}).execute()
                logger.info(f"Label '{label_name}' added to message {message_id}")
            else:
                logger.warning(f"Label '{label_name}' not found for message {message_id}")
        except Exception as e:
            logger.error(f"Failed to add label '{label_name}' to message {message_id}: {e}")

    def mark_as_read(self, message_id):
        """
        Mark a Gmail message as read by removing the 'UNREAD' label.

        Args:
            message_id (str): The Gmail message ID.
        """
        logger.info(f"Marking message {message_id} as read.")
        try:
            self.service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds':['UNREAD']}).execute()
            logger.info(f"Message {message_id} marked as read.")
        except Exception as e:
            logger.error(f"Failed to mark message {message_id} as read: {e}")