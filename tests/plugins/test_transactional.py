from mail_maestro.plugins.transactional import tasks as transactional_tasks

def test_label_transactional():
    email = {"id": "321"}
    called = {"labeled": False, "read": False}
    class DummyGmail:
        def add_label(self, _id, label_name): called["labeled"] = (_id, label_name)
        def mark_as_read(self, _id): called["read"] = _id
    ctx = {"email": email, "gmail": DummyGmail()}
    transactional_tasks.label_transactional(ctx)
    assert called["labeled"] == ("321", "Transactional")
    assert called["read"] == "321"
