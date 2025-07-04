import pytest

@pytest.mark.asyncio
async def test_full_pipeline(monkeypatch, tmp_path):
    # Create dummy prompt templates for all agents
    lang = "en"
    d = tmp_path / lang
    d.mkdir(parents=True)
    for name in ["recruiter_agent", "concert_agent", "mailmaestro_agent"]:
        (d / f"{name}_instructions.j2").write_text("Prompt")
        (d / f"{name}_description.j2").write_text("Description")

    from mail_maestro.runner import run_mailmaestro_pipeline

    await run_mailmaestro_pipeline(str(tmp_path), lang)
