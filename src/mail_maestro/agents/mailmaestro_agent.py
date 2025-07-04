"""
Agent for orchestrating transactional, recruiter, and concert agents using the AnyAgent framework.
Loads prompts and tools for transactional labeling and delegates to recruiter and concert agents.
"""

from any_agent import AnyAgent, AgentConfig
from mail_maestro.logging_config import LangChainLoggingCallbackHandler
from mail_maestro.plugins.transactional import tasks as transactional_tasks
from mail_maestro.core.prompts import load_agent_prompt

handler = LangChainLoggingCallbackHandler()

async def get_mailmaestro_agent(prompts_dir, lang="en", recruiter_agent=None, concert_agent=None):
    """
    Asynchronously creates and returns a MailMaestro agent instance configured with the specified prompts, language, and optional recruiter and concert agents.

    Args:
        prompts_dir (str): The directory path containing agent prompt templates.
        lang (str, optional): The language code for the agent's prompts. Defaults to "en".
        recruiter_agent (Optional[AnyAgent], optional): An optional recruiter agent to be included as a tool. Defaults to None.
        concert_agent (Optional[AnyAgent], optional): An optional concert agent to be included as a tool. Defaults to None.

    Returns:
        AnyAgent: An asynchronously created MailMaestro agent instance configured with the provided parameters.

    Raises:
        Exception: Propagates any exceptions raised during agent creation or prompt loading.
    """
    instructions, description = load_agent_prompt(prompts_dir, "mailmaestro_agent", lang)
    tools = [
        # transactional_tasks.label_transactional,
        recruiter_agent.run_async,
        concert_agent.run_async,
    ]
    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="MailMaestroAgent",
            instructions=instructions,
            description=description,
            tools=tools,
        ),
    )
