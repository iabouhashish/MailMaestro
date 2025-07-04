import pytest
from datetime import datetime, timedelta
from mail_maestro.scheduler import Scheduler

class DummyNotionService:
    called = False
    last_concert = None
    last_dbid = None
    @classmethod
    def get_instance(cls):
        return cls
    @classmethod
    def insert_concert(cls, concert, dbid):
        cls.called = True
        cls.last_concert = concert
        cls.last_dbid = dbid


def test_scheduler_schedules_and_calls_notion(monkeypatch):
    # Patch NotionService in scheduler
    import mail_maestro.scheduler
    monkeypatch.setattr(mail_maestro.scheduler, "NotionService", DummyNotionService)

    scheduler = Scheduler()
    concert = {
        "event_name": "Test Event",
        "summary": "A test concert event.",
        "date_time": (datetime.now() + timedelta(seconds=2)).isoformat(),
        "venue_address": "Test Venue, Test City",
        "presale_info": "Presale starts soon",
        "ticket_link": "https://example.com/tickets",
        "additional_notes": "No notes."
    }
    DummyNotionService.called = False
    DummyNotionService.last_concert = None
    DummyNotionService.last_dbid = None

    scheduler.schedule(concert)
    # Wait for the job to run
    import time
    time.sleep(3)
    assert DummyNotionService.called is True
    assert DummyNotionService.last_concert == concert
    assert DummyNotionService.last_dbid == '220c4a082ac980d5b6a9cc8e0f46a3b3'
    scheduler.shutdown()
