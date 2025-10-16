
import pytest
import library_service as svc


def test_r4_invalid_patron():
    success, msg = svc.return_book_by_patron("123", 1)
    assert success is False
    assert "invalid" in msg.lower()

def test_r4_book_not_found(monkeypatch):
    def fake_get_book_by_id(_): return None
    monkeypatch.setattr("library_service.get_book_by_id", fake_get_book_by_id)
    success, msg = svc.return_book_by_patron("123456", 99)
    assert success is False
    assert "cannot be located" in msg.lower()

def test_r4_no_active_record(monkeypatch):
    def fake_get_book_by_id(_): return {"title": "Mock Book"}
    def fake_update_borrow_record_return_date(*_): return False
    monkeypatch.setattr("library_service.get_book_by_id", fake_get_book_by_id)
    monkeypatch.setattr("library_service.update_borrow_record_return_date", fake_update_borrow_record_return_date)
    success, msg = svc.return_book_by_patron("123456", 1)
    assert success is False
    assert "no active borrow record" in msg.lower()

def test_r4_availability_update_fail(monkeypatch):
    def fake_get_book_by_id(_): return {"title": "Mock Book"}
    def fake_update_borrow_record_return_date(*_): return True
    def fake_update_book_availability(*_): return False
    monkeypatch.setattr("library_service.get_book_by_id", fake_get_book_by_id)
    monkeypatch.setattr("library_service.update_borrow_record_return_date", fake_update_borrow_record_return_date)
    monkeypatch.setattr("library_service.update_book_availability", fake_update_book_availability)
    success, msg = svc.return_book_by_patron("123456", 1)
    assert success is False
    assert "failed to update book availability" in msg.lower()

def test_r4_success(monkeypatch):
    def fake_get_book_by_id(_): return {"title": "Test Book"}
    def fake_update_borrow_record_return_date(*_): return True
    def fake_update_book_availability(*_): return True
    monkeypatch.setattr("library_service.get_book_by_id", fake_get_book_by_id)
    monkeypatch.setattr("library_service.update_borrow_record_return_date", fake_update_borrow_record_return_date)
    monkeypatch.setattr("library_service.update_book_availability", fake_update_book_availability)
    success, msg = svc.return_book_by_patron("123456", 1)
    assert success is True
    assert "has been returned" in msg.lower()
