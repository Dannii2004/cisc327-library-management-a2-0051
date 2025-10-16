import pytest

import library_service as svc


def fakeBook(available=1):
    return {"id": 1, "title": "And Then There Were None", "available_copies": available}

def found(_id):
    return fakeBook(available=2)

def notFound(_id):
    return fakeBook(available=0)

def trueBorrow(patron_id, book_id, borrow_date, due_date):
    return True

def test_r3_happy_path(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_id", found)
    monkeypatch.setattr(svc, "get_patron_borrow_count", lambda pid: 0)
    monkeypatch.setattr(svc, "insert_borrow_record", trueBorrow)
    monkeypatch.setattr(svc, "update_book_availability", lambda bid, d: (d == -1))
    reqMet, message = svc.borrow_book_by_patron("765432", 1)
    assert reqMet is True and "due date" in message.lower()

def test_r3_invalid_patron_id():
    reqMet, message = svc.borrow_book_by_patron("1234", 2)
    assert reqMet is False and "6 digits" in message

def test_r3_book_not_found(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_id", lambda _id: None)
    reqMet, message = svc.borrow_book_by_patron("987654", 999)
    assert reqMet is False and "not found" in message.lower()

def test_r3_unavailable(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_id", notFound)
    reqMet, message = svc.borrow_book_by_patron("987654", 3)
    assert reqMet is False and "not available" in message.lower()

def test_r3_limit_is_5(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_id", found)
    monkeypatch.setattr(svc, "get_patron_borrow_count", lambda pid: 5)
    monkeypatch.setattr(svc, "insert_borrow_record", trueBorrow)
    monkeypatch.setattr(svc, "update_book_availability", lambda bid, d: (d == -1))
    reqMet, _ = svc.borrow_book_by_patron("765432", 1)
    assert reqMet is False
