import pytest

# Dummy GmailService for all tests
import mail_maestro.services.email_client as email_mod

class DummyGmail:
    def __init__(self, *args, **kwargs): pass
    def fetch_unread_messages(self): return []
    def create_draft(self, *a, **k): self.drafts = getattr(self, "drafts", []) + [(a, k)]
    def add_label(self, *a, **k): self.labels = getattr(self, "labels", []) + [(a, k)]
    def mark_as_read(self, *a, **k): self.read = getattr(self, "read", []) + [(a, k)]
    def send_email(self, *a, **k): self.sent = getattr(self, "sent", []) + [(a, k)]

@pytest.fixture(autouse=True)
def patch_gmail(monkeypatch):
    monkeypatch.setattr(email_mod, "GmailService", DummyGmail)
    yield

# Dummy LLM to avoid any real API/network calls in plugin tasks
import mail_maestro.plugins.recruiter.tasks as recruiter_tasks
import mail_maestro.plugins.concert.tasks as concert_tasks

class DummyLLM:
    def __call__(self, prompt, **kwargs):
        if "recruiter" in prompt.lower():
            return "Test Name|Test Company|Test Role"
        if "concert" in prompt.lower():
            return "Test Concert Details"
        return "Stub"

@pytest.fixture(autouse=True)
def patch_llms(monkeypatch):
    monkeypatch.setattr(recruiter_tasks, "llm", DummyLLM())
    monkeypatch.setattr(concert_tasks, "llm", DummyLLM())
    yield
