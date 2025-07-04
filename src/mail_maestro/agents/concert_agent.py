"""
Agent for handling concert-related tasks using the AnyAgent framework.

This module defines the ConcertAgent, which loads prompts and tools for concert extraction, composition, scheduling, and calendar integration. It provides an asynchronous factory function to create a configured agent instance.

Functions:
    get_concert_agent(prompts_dir, lang="en"): Asynchronously creates and returns a configured ConcertAgent instance.
"""

from any_agent import AnyAgent, AgentConfig
from mail_maestro.logging_config import LangChainLoggingCallbackHandler
from mail_maestro.plugins.concert import tasks as concert_tasks
from mail_maestro.plugins.calendar import tasks as calendar_tasks
from mail_maestro.core.prompts import load_agent_prompt

handler = LangChainLoggingCallbackHandler()
    
async def get_concert_agent(prompts_dir, lang="en"):
    """
    Asynchronously creates and returns a configured ConcertAgent instance.

    This function loads the agent's instructions and description from prompt files,
    sets up the necessary tools for concert-related tasks, and initializes the agent
    with the specified configuration.

    Args:
        prompts_dir (str): The directory path containing prompt templates for the agent.
        lang (str, optional): The language code for the prompts. Defaults to "en".

    Returns:
        Any: An asynchronously created ConcertAgent instance configured with the specified prompts and tools.
    """
    instructions, description = load_agent_prompt(prompts_dir, "concert_agent", lang)

    concert_tools = [
        concert_tasks.extract_concert,
        concert_tasks.validate_concert_fields,
        concert_tasks.compose_concert,
        concert_tasks.schedule_concert,
    ]

    return await AnyAgent.create_async(
        "langchain",
        AgentConfig(
            model_id="gpt-4o-mini",
            name="ConcertAgent",
            instructions=instructions,
            description=description,
            tools=concert_tools,
        ),
    )