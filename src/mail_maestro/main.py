import os
import asyncio
import click
from dotenv import find_dotenv, load_dotenv
import yaml

# Activate logging setup before any other imports that use logging
import mail_maestro.logging_config

from mail_maestro.runner import run_mailmaestro_pipeline, run_mailmaestro_server

# # Load .env variables
dotenv_path = find_dotenv()

# Force override of any existing env vars
load_dotenv(dotenv_path=dotenv_path, override=True, verbose=True)

@click.group()
def cli():
    """MailMaestro CLI"""
    pass

@cli.command("run")
@click.option('--lang', default="en", help="Prompt language (default: en)")
@click.option('--prompts-dir', default=None, help="Prompt templates directory")
def run_pipeline(lang, prompts_dir):
    """Run the MailMaestro pipeline asynchronously for all unread emails."""
    asyncio.run(_run_pipeline_async(lang, prompts_dir))

async def _run_pipeline_async(lang, prompts_dir):
    # Default prompts_dir logic
    if not prompts_dir:
        base = os.path.dirname(__file__)
        prompts_dir = os.path.abspath(os.path.join(base, "prompts", os.getenv("TEMPLATE_VERSION", "v1")))
    await run_mailmaestro_pipeline(prompts_dir=prompts_dir, lang=lang)

@cli.command("serve")
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8000)
@click.option('--lang', default="en", help="Prompt language (default: en)")
@click.option('--prompts-dir', default=None, help="Prompt templates directory")
def serve_server(host, port, lang, prompts_dir):
    """Serve MailMaestro as an async HTTP (FastAPI) server for MCP."""
    asyncio.run(_run_server_async(host, port, lang, prompts_dir))

async def _run_server_async(host, port, lang, prompts_dir):
    if not prompts_dir:
        base = os.path.dirname(__file__)
        prompts_dir = os.path.abspath(os.path.join(base, "prompts", os.getenv("TEMPLATE_VERSION", "v1")))
    await run_mailmaestro_server(host=host, port=port, prompts_dir=prompts_dir, lang=lang)

@cli.command("test")
def run_tests():
    """Run the test suite (pytest)"""
    import subprocess
    subprocess.run(["pytest"], check=True)

if __name__ == "__main__":
    cli()
