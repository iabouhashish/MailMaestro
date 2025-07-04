import json
import os

from datetime import datetime, timedelta
from mail_maestro.agents.recruiter_agent import get_recruiter_agent
from mail_maestro.agents.concert_agent import get_concert_agent
from mail_maestro.agents.mailmaestro_agent import get_mailmaestro_agent
from mail_maestro.core.parsers import EmailParser
from mail_maestro.services.email_client import GmailService

# For HTTP serving (optional)
from fastapi import FastAPI, BackgroundTasks
import uvicorn

from mail_maestro.services.gmail_service import get_gmail_service

async def run_mailmaestro_pipeline(prompts_dir, lang):
    # Set up sub-agents and main agent
    recruiter_agent = await get_recruiter_agent(prompts_dir, lang)
    concert_agent = await get_concert_agent(prompts_dir, lang)
    mailmaestro_agent = await get_mailmaestro_agent(prompts_dir, lang, recruiter_agent, concert_agent)
    
    
    gmail = get_gmail_service()

    # Compute cutoff date for last 2 months
    cutoff = datetime.now().astimezone() - timedelta(days=60)

    # Fetch messages since cutoff (ensure your GmailService supports this)
    # try:
    #     emails = gmail.fetch_messages_since(cutoff)
    # except AttributeError:
    #     # Fallback to using search query if method is not implemented
    #     date_str = cutoff.strftime("%Y/%m/%d")
    #     emails = gmail.search_messages(query=f"after:{date_str}")
    emails = gmail.fetch_unread_messages()
    parser = EmailParser()

    for email in emails[:1]:
        # Enrich context
        # thread_history = gmail.fetch_thread(email.thread_id)
        # attachments = gmail.download_attachments(
        #     email.id,
        #     download_dir=os.getenv("ATTACHMENT_DOWNLOAD_DIR", "./attachments")
        # )
        parsed_body = parser.parse(email["body"])
        ctx = {
            "id": email.get("id"),
            "subject": parser.parse(email["subject"]),
            "sender": email.get("sender", ""),
            "body": parsed_body,
            "thread_id": email.get("thread_id"),
            "email_id": email.get("id"),
            "image_data_urls": email.get("image_data_urls", []),
            "current_time": datetime.now().astimezone().isoformat(),
            "deployment_env": os.getenv("ENVIRONMENT", "development"),
        }
        llm_context = json.dumps(ctx, indent=2, ensure_ascii=False)
        # Run the main pipeline
        await mailmaestro_agent.run_async(llm_context)
    

# Optional: Async FastAPI server for MCP/K8s deployment
def build_fastapi_app(prompts_dir, lang):
    app = FastAPI(title="MailMaestro Server")

    @app.post("/run")
    async def run_pipeline_endpoint(background: BackgroundTasks):
        background.add_task(run_mailmaestro_pipeline, prompts_dir, lang)
        return {"status": "accepted"}
    return app

async def run_mailmaestro_server(host, port, prompts_dir, lang):
    app = build_fastapi_app(prompts_dir, lang)
    uvicorn.run(app, host=host, port=port)
