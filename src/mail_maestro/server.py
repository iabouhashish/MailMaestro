"""
MailMaestro FastAPI server module.

This module defines the FastAPI application for the MailMaestro MCP server. It loads configuration, initializes shared services (Gmail, Scheduler, EventStore), and exposes an endpoint to trigger the MailMaestro pipeline asynchronously.

Endpoints:
    POST /run: Triggers the MailMaestro pipeline as a background task and returns immediately with a 202 Accepted status.

Usage:
    Run this module directly to start a local development server with Uvicorn.
"""

# src/mail_maestro/server.py
from fastapi import FastAPI, BackgroundTasks
import uvicorn
import os, yaml

from mail_maestro.runner import Runner
from mail_maestro.services.email_client import GmailService
from mail_maestro.scheduler import Scheduler
from mail_maestro.core.event_store import EventStore
from mail_maestro.services.notion_client import NotionService

app = FastAPI(title="MailMaestro MCP Server")

# Load config once
BASE        = os.path.dirname(__file__)
SPEC_PATH   = os.path.abspath(os.path.join(BASE, "..", "..", "config", "pipeline.yml"))
with open(SPEC_PATH) as f:
    PIPELINE_SPEC = yaml.safe_load(f)
TEMPLATE_VERSION = os.getenv("TEMPLATE_VERSION", "v1")
PROMPTS_DIR      = os.path.abspath(os.path.join(BASE, "prompts", TEMPLATE_VERSION))

# Instantiate shared services
gmail       = GmailService(
    token_path=os.getenv("GMAIL_TOKEN_PATH"),
    creds_path=os.getenv("GMAIL_CREDENTIALS_PATH")
)
scheduler   = Scheduler()
event_store = EventStore()

# Factory for Runner
def make_runner():
    return Runner(
        gmail=gmail,
        scheduler=scheduler,
        event_store=event_store,
        prompts_base=PROMPTS_DIR,
        pipeline_spec=PIPELINE_SPEC
    )

@app.post("/run")
async def run_pipeline(background: BackgroundTasks):
    """
    Trigger the MailMaestro pipeline asynchronously.
    Returns immediately with a 202 Accepted.
    """
    background.add_task(make_runner().run)
    return {"status": "accepted"}

if __name__ == "__main__":
    # local dev server
    uvicorn.run("mail_maestro.server:app", host="0.0.0.0", port=8000, reload=True)
