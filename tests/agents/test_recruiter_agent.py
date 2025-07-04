import pytest
from mail_maestro.agents.recruiter_agent import get_recruiter_agent

@pytest.mark.asyncio
async def test_get_recruiter_agent(tmp_path):
    prompts_dir = tmp_path
    lang = "en"
    d = prompts_dir / lang
    d.mkdir(parents=True)
    (d / "recruiter_agent_instructions.j2").write_text("You are a recruiter agent.")
    (d / "recruiter_agent_description.j2").write_text("Handles recruiter stuff.")
    agent = await get_recruiter_agent(str(prompts_dir), lang)
    assert agent.config.name == "RecruiterAgent"
    assert "recruiter agent" in agent.config.instructions
