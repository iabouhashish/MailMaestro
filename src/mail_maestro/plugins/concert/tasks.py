"""
Concert plugin tasks for MailMaestro.

This module provides functions to extract concert details from emails, compose concert summaries, schedule concert reminders, and interact with Gmail and scheduling services. It leverages language models for information extraction and uses prompt templates for dynamic content generation.

Functions:
    extract_concert(ctx): Extracts concert details from an email using a language model and prompt template.
    compose_concert(ctx): Composes a concert summary using extracted details and a prompt template.
    schedule_concert(ctx): Drafts a concert summary email, schedules an on-sale reminder, and marks the email as read.

Dependencies:
    - langchain_openai.OpenAI: For LLM-based extraction and composition.
    - langdetect: For language detection.
    - mail_maestro.core.parsers.parse_datetime: For parsing event dates.
"""

import json
import logging
from langchain_openai import OpenAI
from langdetect import detect
from datetime import timedelta
import datetime

from mail_maestro.core.parsers import parse_datetime
from mail_maestro.logging_config import LangChainLoggingCallbackHandler
from mail_maestro.scheduler import Scheduler
from mail_maestro.services.gmail_service import get_gmail_service
from mail_maestro.prompts.prompts import TEMPLATES, get_env

# Setup intense logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger("mailmaestro.plugins")

llm = OpenAI(model_name="gpt-4o-mini", temperature=0)
handler = LangChainLoggingCallbackHandler()


def extract_concert(ctx: str) -> dict:
    """
    Extracts concert details from an email context using a language model and a Jinja2 template.

    Args:
        ctx (str): A JSON-encoded context dictionary containing at least the following keys:
            - 'id': The email's unique identifier.
            - 'sender': The email sender's address
            - 'subject': The parsed subject of the email.
            - 'body': The parsed body content of the email.
            - 'thread_id': The email thread's unique identifier.
            - 'current_time': The current timestamp in ISO format.
            - 'deployment_env': The deployment environment (e.g., 'development', 'production').

        Example structure:
            ctx = {
                "id": email.get("id"),
                "sender": email.get("sender"),
                "subject": parser.parse(email["subject"]),
                "body": parsed_body,
                "thread_id": email.get("thread_id"),
                "current_time": datetime.now().astimezone().isoformat(),
                "deployment_env": os.getenv("ENVIRONMENT", "development"),
            }

    Returns:
        dict: The updated context dictionary with an added 'concert' key containing extracted concert details.

        Example return structure:
            ctx = {
                "id": email.get("id"),
                "subject": parser.parse(email["subject"]),
                "body": parsed_body,
                "thread_id": email.get("thread_id"),
                "current_time": datetime.now().astimezone().isoformat(),
                "deployment_env": os.getenv("ENVIRONMENT", "development"),
                "concert": {
                    "event_name": str,         # Event Name
                    "date_time": str,          # Date & Time
                    "venue_address": str,      # Venue & Address
                    "presale_info": str,       # Presale Information
                    "ticket_link": str,        # Ticket Purchase Link
                    "additional_notes": str    # Additional Notes
                }
            }
            

    Side Effects:
        Modifies the input context dictionary by adding a 'concert' entry.

    Raises:
        KeyError: If required keys are missing from the context dictionary.
    """
    logger.debug(f"[extract_concert] extract_concert called with ctx: {ctx}")
    context = json.loads(ctx)
    logger.info(f"[extract_concert] Parsed context: {context}")
    try:
        lang = detect(context['body'])
        logger.debug(f"[extract_concert] Detected language: {lang}")
    except Exception as e:
        logger.error(f"[extract_concert] Language detection failed: {e}")
        lang = 'en'
    tpl = TEMPLATES.get(
        (lang, "extract_concert"),
        TEMPLATES[("en", "extract_concert")]
    )
    logger.debug(f"[extract_concert] Using template for lang '{lang}': {tpl}")
    raw = tpl.render(body=context["body"], current_year=datetime.datetime.now().year, sender=context.get("sender", ""))
    logger.debug(f"[extract_concert] Rendered template: {raw}")
    prompt = raw.encode("ascii", errors="ignore").decode("ascii")
    logger.debug(f"[extract_concert] Prompt for LLM: {prompt}")
    try:
        details = llm.invoke(prompt, config={"callbacks": [handler]})
        logger.info(f"[extract_concert] LLM returned details: {details}")
        context["concert"] = json.loads(details)
    except Exception as e:
        logger.error(f"[extract_concert] Error extracting concert details: {e}")
    logger.debug(f"[extract_concert] Returning context: {context}")
    return json.dumps(context)


def compose_concert(ctx: str) -> str:
    """
    Composes a concert summary email using a language model and a Jinja2 template.

    Args:
        ctx (str): A JSON-encoded context dictionary containing at least the following keys:
            - 'id': The email's unique identifier.
            - 'subject': The parsed subject of the email.
            - 'body': The parsed body content of the email.
            - 'thread_id': The email thread's unique identifier.
            - 'current_time': The current timestamp in ISO format.
            - 'deployment_env': The deployment environment (e.g., 'development', 'production').
            - 'concert': A dictionary with concert details:
                - 'event_name': The official name or title of the concert event (e.g., "Taylor Swift: The Eras Tour")
                - 'date_time': The scheduled date and start time of the concert (ISO 8601 or human-readable)
                - 'venue_address': The full name and address of the concert venue (e.g., "Madison Square Garden, New York, NY")
                - 'presale_info': Details about presale access, codes, or timing (e.g., "Presale starts July 1st at 10am for Amex cardholders")
                - 'ticket_link': Direct URL to purchase tickets online (e.g., "https://tickets.example.com/concert123")
                - 'additional_notes': Any extra information, restrictions, or special instructions (e.g., "VIP packages available; All ages show")


    Returns:
        ctx (str): A JSON-encoded context dictionary containing at least the following keys:
            - 'id': The email's unique identifier.
            - 'subject': The parsed subject of the email.
            - 'body': The parsed body content of the email.
            - 'thread_id': The email thread's unique identifier.
            - 'current_time': The current timestamp in ISO format.
            - 'deployment_env': The deployment environment (e.g., 'development', 'production').
            - 'concert': A dictionary with concert details:
                - 'event_name': The official name or title of the concert event (e.g., "Taylor Swift: The Eras Tour")
                - 'date_time': The scheduled date and start time of the concert (ISO 8601 or human-readable)
                - 'venue_address': The full name and address of the concert venue (e.g., "Madison Square Garden, New York, NY")
                - 'presale_info': Details about presale access, codes, or timing (e.g., "Presale starts July 1st at 10am for Amex cardholders")
                - 'ticket_link': Direct URL to purchase tickets online (e.g., "https://tickets.example.com/concert123")
                - 'additional_notes': Any extra information, restrictions, or special instructions (e.g., "VIP packages available; All ages show")
                - 'summary': A brief summary of the concert event (e.g., "Taylor Swift's latest tour featuring all her hits")

    Raises:
        KeyError: If required keys are missing in the context dictionary.
        Exception: Propagates exceptions from template rendering or the language model.
    """
    logger.debug(f"[compose_concert] compose_concert called with ctx: {ctx}")
    context = json.loads(ctx)
    logger.info(f"[compose_concert] Parsed context: {context}")
    c = context['concert']
    try:
        lang = detect(context['body'])
        logger.debug(f"[compose_concert] Detected language: {lang}")
    except Exception as e:
        logger.error(f"[compose_concert] Language detection failed: {e}")
        lang = 'en'
    tmpl = TEMPLATES.get((lang, "compose_concert"), TEMPLATES[("en","compose_concert")])
    logger.debug(f"[compose_concert] Using template for lang '{lang}': {tmpl}")
    raw = tmpl.render(event_details=c['body'])
    logger.debug(f"[compose_concert] Rendered template: {raw}")
    prompt = raw.encode("ascii", errors="ignore").decode("ascii")
    logger.debug(f"[compose_concert] Prompt for LLM: {prompt}")
    try:
        summary = llm.invoke(prompt, config={"callbacks": [handler]})
        logger.info(f"[compose_concert] LLM returned summary: {summary}")
        c['summary'] = summary
    except Exception as e:
        logger.error(f"[compose_concert] Error extracting concert summary: {e}")
    logger.debug(f"[compose_concert] Returning context: {context}")
    return json.dumps(context)


def schedule_concert(ctx: str) -> None:
    """
    Schedules a concert-related workflow by drafting a summary email, scheduling an on-sale reminder, and marking the original email as read.

    Args:
        ctx (str): A JSON-encoded context dictionary containing at least the following keys:
            - 'id': The email's unique identifier.
            - 'subject': The parsed subject of the email.
            - 'body': The parsed body content of the email.
            - 'thread_id': The email thread's unique identifier.
            - 'current_time': The current timestamp in ISO format.
            - 'deployment_env': The deployment environment (e.g., 'development', 'production').
            - 'concert' (dict): Concert details, including 'summary' and 'details'.
                - 'event_name': The official name or title of the concert event (e.g., "Taylor Swift: The Eras Tour")
                - 'summary': A brief summary of the concert event (e.g., "Taylor Swift's latest tour featuring all her hits")
                - 'date_time': The scheduled date and start time of the concert (ISO 8601 or human-readable)
                - 'venue_address': The full name and address of the concert venue (e.g., "Madison Square Garden, New York, NY")
                - 'presale_info': Details about presale access, codes, or timing (e.g., "Presale starts July 1st at 10am for Amex cardholders")
                - 'ticket_link': Direct URL to purchase tickets online (e.g., "https://tickets.example.com/concert123")
                - 'additional_notes': Any extra information, restrictions, or special instructions (e.g., "VIP packages available; All ages show")

        Example structure:
            ctx = {
                "id": email.get("id"),
                "subject": parser.parse(email["subject"]),
                "body": parsed_body,
                "thread_id": email.get("thread_id"),
                "current_time": datetime.now().astimezone().isoformat(),
                "deployment_env": os.getenv("ENVIRONMENT", "development"),
                "concert": {
                    "event_name": str,         # Event Name
                    "summary": str,            # Concert Summary
                    "date_time": str,          # Date & Time
                    "venue_address": str,      # Venue & Address
                    "presale_info": str,       # Presale Information
                    "ticket_link": str,        # Ticket Purchase Link
                    "additional_notes": str    # Additional Notes
                }
            }

    Returns:
        None
    """
    logger.debug(f"[schedule_concert] schedule_concert called with ctx: {ctx}")
    context = json.loads(ctx)
    logger.info(f"[schedule_concert] Parsed context: {context}")
    c = context['concert']
    scheduler = Scheduler()

    # Parse and schedule on-sale reminder
    try:
        scheduler.schedule(
            concert=c
        )
        logger.info(f"[schedule_concert] Scheduled on-sale reminder for {c['event_name']}")
    except Exception as e:
        logger.error(f"[schedule_concert] Failed to schedule on-sale reminder: {e}")

    logger.debug("[schedule_concert] schedule_concert completed.")
    return None

def validate_concert_fields(ctx: str) -> str:
    """
    Validates that all required fields for a concert are present in the context.
    If any required field is missing, attempts to re-extract those fields using the LLM.

    Args:
       ctx (str): A JSON-encoded context dictionary containing at least the following keys:
            - 'id': The email's unique identifier.
            - 'subject': The parsed subject of the email.
            - 'body': The parsed body content of the email.
            - 'thread_id': The email thread's unique identifier.
            - 'current_time': The current timestamp in ISO format.
            - 'deployment_env': The deployment environment (e.g., 'development', 'production').
            - 'concert' (dict): Concert details, including 'summary' and 'details'.
                - 'event_name': The official name or title of the concert event (e.g., "Rock Legends Reunion Tour")
                - 'summary': A brief summary of the concert event (e.g., "A night of classic rock hits and special guests")
                - 'date_time': The scheduled date and start time of the concert (ISO 8601 or human-readable)
                - 'venue_address': The full name and address of the concert venue (e.g., "Madison Square Garden, New York, NY")
                - 'presale_info': Details about presale access, codes, or timing (e.g., "Presale starts July 1st at 10am for Amex cardholders")
                - 'ticket_link': Direct URL to purchase tickets online (e.g., "https://tickets.example.com/concert123")
                - 'additional_notes': Any extra information, restrictions, or special instructions (e.g., "VIP packages available; All ages show")
        
        Example structure:
            ctx = {
                "id": email.get("id"),
                "subject": parser.parse(email["subject"]),
                "body": parsed_body,
                "thread_id": email.get("thread_id"),
                "current_time": datetime.now().astimezone().isoformat(),
                "deployment_env": os.getenv("ENVIRONMENT", "development"),
                "concert": {
                    "event_name": str,         # Event Name
                    "summary": str,            # Concert Summary
                    "date_time": str,          # Date & Time
                    "venue_address": str,      # Venue & Address
                    "presale_info": str,       # Presale Information
                    "ticket_link": str,        # Ticket Purchase Link
                    "additional_notes": str    # Additional Notes
                }
            }
    Returns:
        dict: A JSON-encoded context dictionary containing at least the following keys:
            - 'id': The email's unique identifier.
            - 'subject': The parsed subject of the email.
            - 'body': The parsed body content of the email.
            - 'thread_id': The email thread's unique identifier.
            - 'current_time': The current timestamp in ISO format.
            - 'deployment_env': The deployment environment (e.g., 'development', 'production').
            - 'concert': A dictionary with concert details:
                - 'event_name': The official name or title of the concert event (e.g., "Rock Legends Reunion Tour")
                - 'date_time': The scheduled date and start time of the concert (ISO 8601 or human-readable)
                - 'venue_address': The full name and address of the concert venue (e.g., "Madison Square Garden, New York, NY")
                - 'presale_info': Details about presale access, codes, or timing (e.g., "Presale starts July 1st at 10am for Amex cardholders")
                - 'ticket_link': Direct URL to purchase tickets online (e.g., "https://tickets.example.com/concert123")
                - 'additional_notes': Any extra information, restrictions, or special instructions (e.g., "VIP packages available; All ages show")
                - 'summary': A brief summary of the concert event (e.g., "A night of classic rock hits and special guests")
    """
    return ctx