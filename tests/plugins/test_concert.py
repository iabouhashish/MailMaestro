import pytest
from mail_maestro.plugins.concert import tasks as concert_tasks

@pytest.fixture
def dummy_ctx():
    return {
        "email": {
            "body": "Concert: Taylor Swift on July 1 at MSG",
            "subject": "Concert Invite",
            "thread_id": "thread-2",
            "id": "234",
        },
        "concert": {"details": "Taylor Swift at MSG, July 1 2024"},
        "gmail": type("Gmail", (), {
            "create_draft": lambda *a, **k: None,
            "mark_as_read": lambda *a, **k: None,
        })(),
        "scheduler": type("Scheduler", (), {"schedule": lambda *a, **k: None})(),
        "prompt_env_fn": lambda lang: type("Env", (), {
            "get_template": lambda self, name: type("Tmpl", (), {
                "render": staticmethod(lambda **_: "Taylor Swift at MSG, July 1 2024")
            })()
        })(),
    }

def test_extract_concert(dummy_ctx):
    ctx = concert_tasks.extract_concert(dummy_ctx.copy())
    assert "concert" in ctx
    assert "details" in ctx["concert"]

def test_compose_concert(dummy_ctx):
    ctx = concert_tasks.compose_concert(dummy_ctx.copy())
    assert "summary" in ctx["concert"]

def test_schedule_concert(dummy_ctx):
    dummy_ctx['concert']['summary'] = "Test summary"
    concert_tasks.schedule_concert(dummy_ctx.copy())  # should not raise