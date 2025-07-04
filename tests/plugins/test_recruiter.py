import pytest
from mail_maestro.plugins.recruiter import tasks as recruiter_tasks

@pytest.fixture
def dummy_ctx():
    return {
        "email": {
            "body": "Hi Ibrahim, we loved your resume. Role: AI Lead at OpenAI.",
            "subject": "Great Opportunity",
            "thread_id": "thread-1",
            "id": "123",
        },
        "gmail": type("Gmail", (), {"create_draft": lambda *a, **k: None, "mark_as_read": lambda *a, **k: None}),
        "prompt_env_fn": lambda lang: type("Env", (), {
            "get_template": lambda self, name: type("Tmpl", (), {
                "render": staticmethod(lambda **_: "Ibrahim|OpenAI|AI Lead")
            })()
        })(),
    }

def test_extract_recruiter(dummy_ctx, monkeypatch):
    class DummyLLM:
        def __call__(self, prompt, **kwargs): return "A|B|C"
    monkeypatch.setattr(recruiter_tasks, "llm", DummyLLM())
    ctx = recruiter_tasks.extract_recruiter(dummy_ctx.copy())
    assert "recruiter_info" in ctx
    assert ctx["recruiter_info"]["company"] == "B"

def test_compose_recruiter(dummy_ctx):
    dummy_ctx["recruiter_info"] = {"name": "Ibrahim", "company": "OpenAI", "role": "AI Lead"}
    ctx = recruiter_tasks.compose_recruiter(dummy_ctx.copy())
    assert "summary" in ctx

def test_finalize_recruiter(dummy_ctx):
    dummy_ctx["recruiter_info"] = {"company": "OpenAI"}
    dummy_ctx["summary"] = "Hi!"
    def draft(*a, **k): dummy_ctx["drafted"] = True
    def read(*a, **k): dummy_ctx["read"] = True
    gmail = dummy_ctx["gmail"] = type("Gmail", (), {
        "create_draft": draft,
        "mark_as_read": read
    })()
    recruiter_tasks.finalize_recruiter(dummy_ctx)
    assert dummy_ctx.get("drafted") is True
    assert dummy_ctx.get("read") is True
