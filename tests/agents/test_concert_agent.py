import pytest
from mail_maestro.agents.concert_agent import get_concert_agent

@pytest.mark.asyncio
async def test_get_concert_agent(tmp_path):
    prompts_dir = tmp_path
    lang = "en"
    d = prompts_dir / lang
    d.mkdir(parents=True)
    (d / "concert_agent_instructions.j2").write_text("You are a concert agent.")
    (d / "concert_agent_description.j2").write_text("Handles concert stuff.")
    agent = await get_concert_agent(str(prompts_dir), lang)
    assert agent.config.name == "ConcertAgent"
    assert "concert agent" in agent.config.instructions
