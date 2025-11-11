
import pytest

from services.library_service import borrow_book_by_patron

def contains_any(text: str, needles):

    t = (text or "").lower()

    return any(n in t for n in needles)

VOLUME = {"id": 42, "title": "Intro to Testing", "available_copies": 2}

def test_patron_id_guard(monkeypatch):

    """Reject non-6-digit patron IDs."""

    monkeypatch.setattr("services.library_service.get_book_by_id", lambda bid: VOLUME)
   
    monkeypatch.setattr("services.library_service.get_patron_borrow_count", lambda pid: 0)

    for bad in ["", "12x456", "12345", "1234567"]:
     
        ok, msg = borrow_book_by_patron(bad, 777)   # custom book id
       
        assert ok is False
        
        assert contains_any(msg, ["invalid", "patron", "6 digits"])

def test_missing_book_lookup(monkeypatch):
   
    """Reject when the book cannot be found in the catalog."""
   
    monkeypatch.setattr("services.library_service.get_book_by_id", lambda bid: None)

   
    ok, msg = borrow_book_by_patron("900321", 101)  # custom patron/book ids
    
    assert ok is False
    
    assert contains_any(msg, ["book not found", "cannot be located", "missing", "unknown"])

def test_no_stock(monkeypatch):
    
    """Reject when there are no available copies (0 or negative)."""
    
    monkeypatch.setattr(
    
        "services.library_service.get_book_by_id",
        lambda bid: dict(VOLUME, available_copies=0),
    
    )
    
    ok, msg = borrow_book_by_patron("004200", 42)
    
    assert ok is False
    
    assert contains_any(msg, ["not available", "unavailable", "no copies", "out of stock"])

    
    monkeypatch.setattr(
        "services.library_service.get_book_by_id",
        lambda bid: dict(VOLUME, available_copies=-3),
    
    )
    
    ok, msg = borrow_book_by_patron("004200", 42)
    
    assert ok is False
    
    assert contains_any(msg, ["not available", "unavailable", "no copies", "out of stock"])

def test_borrow_cap_hit(monkeypatch):
    
    """Reject when patron has reached or exceeded the cap (5)."""
    
    monkeypatch.setattr("services.library_service.get_book_by_id", lambda bid: VOLUME)

    monkeypatch.setattr("services.library_service.get_patron_borrow_count", lambda pid: 7)

    ok, msg = borrow_book_by_patron("777777", 42)
    
    assert ok is False
    
    assert contains_any(msg, ["limit", "maximum", "5"])

def test_borrow_record_db_error(monkeypatch):
    
    """DB error while creating the borrow record."""
    
    monkeypatch.setattr("services.library_service.get_book_by_id", lambda bid: VOLUME)
    
    monkeypatch.setattr("services.library_service.get_patron_borrow_count", lambda pid: 2)

    monkeypatch.setattr("services.library_service.insert_borrow_record", lambda *a, **k: False)

    ok, msg = borrow_book_by_patron("135790", 42)
    
    assert ok is False
    assert contains_any(msg, ["database", "creating borrow", "borrow record", "insert"])

def test_decrement_stock_db_error(monkeypatch):
   
    """DB error while decrementing available copies after insert succeeds."""
    
    monkeypatch.setattr("services.library_service.get_book_by_id", lambda bid: VOLUME)
    
    monkeypatch.setattr("services.library_service.get_patron_borrow_count", lambda pid: 0)
    
    monkeypatch.setattr("services.library_service.insert_borrow_record", lambda *a, **k: True)

    monkeypatch.setattr("services.library_service.update_book_availability", lambda *a, **k: False)

   
    ok, msg = borrow_book_by_patron("246810", 42)
    
    assert ok is False
    
    assert contains_any(msg, ["database", "update", "availability", "decrement"])

def test_happy_path_borrow(monkeypatch):
   
    """Successful borrow: insert succeeds and availability is decremented."""
    
    monkeypatch.setattr("services.library_service.get_book_by_id", lambda bid: VOLUME)
    
    monkeypatch.setattr("services.library_service.get_patron_borrow_count", lambda pid: 1)
   
    monkeypatch.setattr("services.library_service.insert_borrow_record", lambda *a, **k: True)
   
    monkeypatch.setattr("services.library_service.update_book_availability", lambda *a, **k: True)

    ok, msg = borrow_book_by_patron("909090", 42)
    
    assert ok is True

    assert contains_any(msg, ["success", "borrowed", "due date", "completed", "ok"])
