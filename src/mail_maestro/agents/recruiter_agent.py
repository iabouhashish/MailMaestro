"""
Agent for handling recruiter-related tasks using the AnyAgent framework.
Loads prompts and tools for recruiter extraction, composition, and finalization.
"""

from any_agent import AnyAgent, AgentConfig
from mail_maestro.plugins.recruiter import tasks as recruiter_tasks
from mail_maestro.core.prompts import load_agent_prompt
from mail_maestro.logging_config import LangChainLoggingCallbackHandler

handler = LangChainLoggingCallbackHandler()

async def get_recruiter_agent(prompts_dir, lang="en"):
    """
    Asynchronously creates and returns a configured recruiter agent.

    This function loads the agent's instructions and description from prompt files,
    sets up the recruiter-specific tools, and initializes an agent instance using
    the specified model and configuration.

    Args:
        prompts_dir (str): The directory path containing prompt files for the agent.
        lang (str, optional): The language code for the prompts. Defaults to "en".

    Returns:
        AnyAgent: An asynchronously created recruiter agent instance.

    Raises:
        Exception: If loading prompts or agent creation fails.
    """
    instructions, description = load_agent_prompt(prompts_dir, "recruiter_agent", lang)

    recruiter_tools = [
        recruiter_tasks.extract_recruiter,
        recruiter_tasks.compose_recruiter,
        recruiter_tasks.finalize_recruiter,
    ]

    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="RecruiterAgent",
            instructions=instructions,
            description=description,
            tools=recruiter_tools,
        ),
    )
