"""
Recruiter plugin tasks for MailMaestro.

This module provides functions to extract recruiter information from emails, compose recruiter summaries, and finalize recruiter-related drafts. It uses language models and prompt templates for dynamic content extraction and generation.

Functions:
    extract_recruiter(ctx): Extracts recruiter name, company, and role from an email using a language model and prompt template.
    compose_recruiter(ctx): Composes a recruiter summary using extracted information and a prompt template.
    finalize_recruiter(ctx): Drafts a recruiter summary email and marks the email as read.

Dependencies:
    - langchain_openai.OpenAI: For LLM-based extraction and composition.
    - langdetect: For language detection.
"""

import json
from langchain_openai import OpenAI
from langdetect import detect
import logging

from mail_maestro.logging_config import LangChainLoggingCallbackHandler
from mail_maestro.services.gmail_service import get_gmail_service
from mail_maestro.prompts.prompts import TEMPLATES, get_env

llm = OpenAI(model_name="gpt-4o-mini", temperature=0)
logger = logging.getLogger("mailmaestro.plugins")
handler = LangChainLoggingCallbackHandler()

def extract_recruiter(ctx: str) -> str:
    """
    Extracts recruiter information from an email and updates the context dictionary.

    This function detects the language of the email body, loads the appropriate prompt environment,
    renders a prompt using a Jinja2 template, and uses a language model to extract the recruiter's
    name, company, and role from the email content. The extracted information is then stored in the
    'ctx' dictionary under the 'recruiter_info' key.

    Args:
        ctx (dict): A context dictionary containing at least the following keys:
            - 'email': A dictionary with an email body under the 'body' key.
            - 'prompt_env_fn': A function that takes a language code and returns a Jinja2 environment.

    Returns:
        dict: The updated context dictionary with the extracted recruiter information added under
        the 'recruiter_info' key.
    """
    logger.debug(f"extract_recruiter called with ctx: {ctx}")
    context = json.loads(ctx)
    try:
        lang = detect(context['body'])
        logger.debug(f"Detected language: {lang}")
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        lang = 'en'
    tpl = TEMPLATES.get(
        (lang, "extract_recruiter"),
        TEMPLATES[("en", "extract_recruiter")]
    )
    raw = tpl.render(body=context["body"])
    prompt = raw.encode("ascii", errors="ignore").decode("ascii")
    try:
        name, company, role = [s.strip() for s in llm.invoke(prompt, config={"callbacks": [handler]}).split('|')]
        logger.info(f"Extracted recruiter info: name={name}, company={company}, role={role}")
        context['recruiter_info'] = {'name': name, 'company': company, 'role': role}
    except Exception as e:
        logger.error(f"Failed to extract recruiter info: {e}")
        raise
    return json.dumps(context)

def compose_recruiter(ctx: str) -> str:
    """
    Composes a recruiter summary using context information and a template.

    Args:
        ctx (dict): A context dictionary containing:
            - 'recruiter_info' (dict): Information about the recruiter.
            - 'email' (dict): Email data with at least a 'subject' and 'body'.
            - 'prompt_env_fn' (callable): Function to create a template environment.
            - Any other context needed for processing.

    Returns:
        dict: The updated context dictionary with a new 'summary' key containing the generated summary.
    """
    logger.debug(f"compose_recruiter called with ctx: {ctx}")
    context = json.loads(ctx)
    info = context['recruiter_info']
    try:
        lang = detect(context['body'])
        logger.debug(f"Detected language: {lang}")
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        lang = 'en'
    tpl = TEMPLATES.get(
        (lang, "extract_recruiter"),
        TEMPLATES[("en", "extract_recruiter")]
    )
    raw = tpl.render(subject=context["subject"], **info)
    prompt = raw.encode("ascii", errors="ignore").decode("ascii")
    try:
        summary = llm.invoke(prompt, config={"callbacks": [handler]})
        logger.info(f"Generated recruiter summary for company: {info.get('company')}")
        context['summary'] = summary
    except Exception as e:
        logger.error(f"Failed to generate recruiter summary: {e}")
        raise
    return json.dumps(context)

def finalize_recruiter(ctx: str) -> None:
    """
    Finalizes the recruiter processing by creating a draft email and marking the original email as read.

    Args:
        ctx (dict): Context dictionary containing:
            - 'email' (dict): The original email information, including 'id' and 'thread_id'.
            - 'summary' (str): The summary to include in the draft email body.
            - 'recruiter_info' (dict): Information about the recruiter, including 'company'.

    Returns:
        None
    """
    logger.debug(f"finalize_recruiter called with ctx: {ctx}")
    context = json.loads(ctx)
    gmail = get_gmail_service()
    summary = context['summary']
    try:
        gmail.create_draft(
            to="me@example.com",
            subject=f"\U0001F50D Recruiter: {context['recruiter_info']['company']}",
            body=summary,
            thread_id=context['thread_id']
        )
        logger.info(f"Draft created for recruiter: {context['recruiter_info']['company']}")
    except Exception as e:
        logger.error(f"Failed to create recruiter draft: {e}")
        raise
    # gmail.mark_as_read(email['id'])
    return None
