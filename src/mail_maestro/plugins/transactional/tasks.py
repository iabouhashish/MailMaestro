"""
Transactional plugin tasks for MailMaestro.

This module provides a function to label emails as transactional and mark them as read using Gmail integration.

Functions:
    label_transactional(ctx): Adds a 'Transactional' label to an email and marks it as read.
"""

import json
import logging
from mail_maestro.services.gmail_service import get_gmail_service

logger = logging.getLogger("mailmaestro.plugins")


def label_transactional(ctx: str) -> None:
    """
    Adds a "Transactional" label to an email and marks it as read using the Gmail API.

    Args:
        ctx (str): A JSON string containing an 'email' dictionary with at least an 'id' key.

    Returns:
        None

    Side Effects:
        - Updates the label and read status of the specified email in the user's Gmail account.

    Raises:
        KeyError: If the 'email' key is missing from the context.

    Example:
        ctx = json.dumps({'email': {'id': '12345'}})
        label_transactional(ctx)
    """
    logger.debug(f"label_transactional called with ctx: {ctx}")
    context = json.loads(ctx)
    try:
        email = context['email']
        gmail = get_gmail_service()
        gmail.add_label(email['id'], label_name="Transactional")
        logger.info(f"Added 'Transactional' label to email id: {email['id']}")
        # gmail.mark_as_read(email['id'])
    except KeyError as e:
        logger.error(f"Missing key in context: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to label email as transactional: {e}")
        raise
    return None
