"""
Calendar plugin tasks for MailMaestro.

This module provides a function to create and send calendar invites for concert events. It parses event details, constructs an ICS calendar event, and sends it as an email attachment.

Functions:
    create_calendar_invite(ctx): Parses concert details, creates an ICS invite, and sends it via Gmail.

Dependencies:
    - ics.Calendar, ics.Event: For ICS file creation.
    - dateutil.parser: For parsing event dates.
    - datetime.timedelta: For event duration.
"""

import json
from ics import Calendar, Event
from dateutil import parser
from datetime import timedelta
import logging

from mail_maestro.services.gmail_service import get_gmail_service

logger = logging.getLogger("mailmaestro.plugins")

def create_calendar_invite(ctx: str) -> str:
    """
    Creates a calendar invite for a concert event and sends it as an email attachment.

    Args:
        ctx (dict): Context dictionary containing:
            - 'concert' (dict): Concert details, including 'details' (str) with date/time information and optionally 'event_name' (str).
            - 'email' (str): Recipient's email address (not directly used in this function).
            - 'gmail' (object): Gmail client instance with a 'send_email' method.

    Returns:
        dict: The original context dictionary (ctx) after sending the invite email.

    Raises:
        ValueError: If the date cannot be parsed from the concert details.
        Exception: If sending the email fails.

    Side Effects:
        Sends an email with a calendar invite (.ics file) attached to the specified recipient.
    """
    logger.debug(f"create_calendar_invite called with ctx: {ctx}")
    context = json.loads(ctx)
    c = context['concert']
    email = context['email']
    gmail = get_gmail_service()

    try:
        dt = parser.parse(c['details'])
        logger.info(f"Parsed datetime for event: {dt}")
    except Exception as e:
        logger.error(f"Failed to parse datetime from details '{c['details']}': {e}")
        raise

    cal = Calendar()
    ev = Event()
    ev.name = c.get('event_name', 'Concert')
    ev.begin = dt
    ev.duration = timedelta(hours=3)
    cal.events.add(ev)
    ics_content = str(cal)
    logger.debug(f"ICS content generated for event '{ev.name}'")

    try:
        gmail.send_email(
            to="me@example.com",
            subject=f"\U0001F4C5 Invite: {ev.name}",
            body="Your calendar invite is attached.",
            attachments=[("invite.ics", ics_content, "text/calendar")]
        )
        logger.info(f"Calendar invite sent for event '{ev.name}' to 'me@example.com'")
    except Exception as e:
        logger.error(f"Failed to send calendar invite: {e}")
        raise
    return json.dumps(context)
