"""
Gmail service singleton accessor for MailMaestro.

This module provides a singleton getter for the GmailService class, ensuring only one instance is created and reused throughout the application. The GmailService is initialized using environment variables for token and credentials paths.

Functions:
    get_gmail_service(): Returns a singleton instance of GmailService, initializing it if necessary.

Environment Variables:
    GMAIL_TOKEN_PATH: Path to the Gmail OAuth token file.
    GMAIL_CREDENTIALS_PATH: Path to the Gmail client credentials JSON file.
"""

import os
import logging
from mail_maestro.services.email_client import GmailService

# PEP 282 logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger("mailmaestro.services")

_gmail_service = None

def get_gmail_service():
    """
    Get a singleton instance of GmailService.

    Returns:
        GmailService: The singleton GmailService instance, initialized if not already created.
    """
    global _gmail_service
    if _gmail_service is None:
        logger.info("Initializing GmailService singleton instance.")
        _gmail_service = GmailService(
            token_path=os.getenv("GMAIL_TOKEN_PATH"),
            creds_path=os.getenv("GMAIL_CREDENTIALS_PATH"),
        )
    else:
        logger.debug("Returning existing GmailService singleton instance.")
    return _gmail_service