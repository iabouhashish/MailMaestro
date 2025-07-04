import pytest
from mail_maestro.agents.mailmaestro_agent import get_mailmaestro_agent

class DummyAgent:
    async def run_async(self, ctx: dict) -> str:
        """
        Asynchronously executes the main logic for the agent.

        Args:
            ctx: The context object containing relevant information for execution.

        Returns:
            str: The result of the asynchronous operation, "ok" in this case.
        """
        return "ok"

@pytest.mark.asyncio
async def test_get_mailmaestro_agent(tmp_path):
    """
    Test the asynchronous creation of a MailMaestro agent with dynamically generated prompt files.

    This test verifies that:
    - The required prompt files for the specified language are created in a temporary directory.
    - The `get_mailmaestro_agent` function correctly loads these prompts and initializes the agent.
    - The resulting agent's configuration has the expected name ("MailMaestroAgent").
    - The agent's instructions contain the string "mailmaestro".

    Args:
        tmp_path (pathlib.Path): Temporary directory provided by pytest for file operations.

    Raises:
        AssertionError: If the agent's configuration does not match the expected values.
    """
    prompts_dir = tmp_path
    lang = "en"
    d = prompts_dir / lang
    d.mkdir(parents=True)
    (d / "mailmaestro_agent_instructions.j2").write_text("You are the mailmaestro.")
    (d / "mailmaestro_agent_description.j2").write_text("Handles everything.")
    recruiter_agent = DummyAgent()
    concert_agent = DummyAgent()
    agent = await get_mailmaestro_agent(str(prompts_dir), lang, recruiter_agent, concert_agent)
    assert agent.config.name == "MailMaestroAgent"
    assert "mailmaestro" in agent.config.instructions
