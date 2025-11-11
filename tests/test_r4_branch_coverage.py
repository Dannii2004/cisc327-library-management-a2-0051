
import importlib
libmod = importlib.import_module("services.library_service")

def test_return_book_no_active_record_branch(monkeypatch):

    monkeypatch.setattr(libmod, "get_book_by_id", lambda _bid: {"title": "Mock Book"})

    monkeypatch.setattr(libmod, "update_borrow_record_return_date", lambda _pid, _bid, _ts: False)

    ok, msg = libmod.return_book_by_patron("123456", 1)

    assert ok is False

    assert "no active borrow record" in msg.lower()

def test_return_book_availability_update_fail_branch(monkeypatch):

    monkeypatch.setattr(libmod, "get_book_by_id", lambda _bid: {"title": "Mock Book"})

    monkeypatch.setattr(libmod, "update_borrow_record_return_date", lambda _pid, _bid, _ts: True)

    monkeypatch.setattr(libmod, "update_book_availability", lambda _bid, _delta: False)

    ok, msg = libmod.return_book_by_patron("123456", 1)

    assert ok is False

    assert "failed to update book availability" in msg.lower()
