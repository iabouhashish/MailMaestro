"""
Prompt loading utilities for MailMaestro agents.

This module provides functions to load agent instructions and descriptions from Jinja2 templates, supporting multi-language prompt directories.

Functions:
    load_agent_prompt(prompts_dir, agent_name, lang="en"): Loads instructions and description for an agent from Jinja2 templates in the specified language directory.
"""

from jinja2 import Environment, FileSystemLoader

def load_agent_prompt(prompts_dir, agent_name, lang="en"):
    """
    Load instructions and description for an agent from Jinja2 templates.

    Looks for templates named '{agent_name}_instructions.j2' and '{agent_name}_description.j2' in the specified language directory.

    Args:
        prompts_dir (str): Path to the base prompts directory.
        agent_name (str): Name of the agent (e.g., 'recruiter_agent').
        lang (str, optional): Language code (default: 'en').

    Returns:
        tuple[str, str]: Rendered instructions and description strings.
    """
    env = Environment(loader=FileSystemLoader(f"{prompts_dir}/{lang}"), autoescape=True)
    instructions_tmpl = env.get_template(f"{agent_name}_instructions.j2")
    description_tmpl  = env.get_template(f"{agent_name}_description.j2")
    instructions = instructions_tmpl.render()
    description  = description_tmpl.render()
    return instructions, description