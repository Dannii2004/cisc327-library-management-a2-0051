import library_service as svc
from datetime import datetime, timedelta
import database

def test_r5_book_not_found(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda _: None)
    stat = svc.calculate_late_fee_for_book("765432", 1)
    assert stat["fee_amount"] == 0.0
    assert "not been found" in stat["status"].lower()

def test_r5_borrow_record_not_found(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda _: {"id": 1})
    monkeypatch.setattr(database, "get_borrow_record", lambda pid, bid: None, raising=False)
    stat = svc.calculate_late_fee_for_book("765432", 1)
    assert stat["fee_amount"] == 0.0
    assert "has not been located" in stat["status"].lower()

def test_r5_no_overdue(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda _: {"id": 1})
    due = datetime.now() + timedelta(days=2)
    monkeypatch.setattr(database, "get_borrow_record", lambda pid, bid: {"due_date": due}, raising=False)
    stat = svc.calculate_late_fee_for_book("765432", 1)
    assert stat["fee_amount"] == 0.0
    assert stat["days_overdue"] == 0
    assert "no overdue charge" in stat["status"].lower()

def test_r5_overdue_calc(monkeypatch):
    monkeypatch.setattr("library_service.get_book_by_id", lambda _: {"id": 1})
    due = datetime.now() - timedelta(days=5)
    monkeypatch.setattr(database, "get_borrow_record", lambda pid, bid: {"due_date": due}, raising=False)
    stat = svc.calculate_late_fee_for_book("765432", 1)
    assert stat["days_overdue"] == 5
    assert stat["fee_amount"] == 1.25
    assert "late fee has been calculated" in stat["status"].lower()
