"""
Pydantic models for MailMaestro application context.

This module defines data models for representing email and application context using Pydantic BaseModel classes.

Classes:
    EmailContext: Represents the structure of an email, including id, thread_id, subject, snippet, and body.
    AppContext: Represents the application context, including the email, labels, recruiter info, and concert info.
"""

from pydantic import BaseModel, Field
from typing import List, Dict

class EmailContext(BaseModel):
    """
    Model representing the structure of an email.

    Attributes:
        id (str): Unique identifier for the email.
        thread_id (str): Identifier for the email thread.
        subject (str): Subject line of the email.
        snippet (str): Short snippet or preview of the email.
        body (str): Full body content of the email.
    """
    id: str
    thread_id: str
    subject: str
    snippet: str
    body: str

class AppContext(BaseModel):
    """
    Model representing the application context for MailMaestro.

    Attributes:
        email (EmailContext): The email context object.
        labels (Dict[str, str]): Dictionary of labels associated with the email.
        recruiter_info (Dict[str, str]): Information about a recruiter, if present.
        concert (Dict[str, str]): Information about a concert, if present.
    """
    email: EmailContext
    labels: Dict[str,str] = Field(default_factory=dict)
    recruiter_info: Dict[str,str] = {}
    concert: Dict[str,str] = {}