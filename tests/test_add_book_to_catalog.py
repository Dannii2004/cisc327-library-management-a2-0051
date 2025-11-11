
import pytest

from services import library_service as svc

def test_add_book_title_required(monkeypatch):

    result, message = svc.add_book_to_catalog("", "Author", "1"*13, 1)

    assert result is False and "title" in message.lower()

def test_add_book_title_too_long(monkeypatch):

    long_title = "x" * 201

    result, message = svc.add_book_to_catalog(long_title, "Author", "1"*13, 1)
    
    assert result is False and "title" in message.lower()

def test_add_book_author_required(monkeypatch):
    
    result, message = svc.add_book_to_catalog("Title", "   ", "1"*13, 1)
    
    assert result is False and "author" in message.lower()

def test_add_book_author_too_long(monkeypatch):
    
    long_author = "y" * 101
    
    result, message = svc.add_book_to_catalog("Title", long_author, "1"*13, 1)
    
    assert result is False and "author" in message.lower()

def test_add_book_isbn_invalid_length(monkeypatch):
    
    result, message = svc.add_book_to_catalog("Title", "Author", "123", 1)
    
    assert result is False and "isbn" in message.lower()

def test_add_book_isbn_non_digit(monkeypatch):
    
    result, message = svc.add_book_to_catalog("Title", "Author", "12345678901ab", 1)
    
    assert result is False and "isbn" in message.lower()

@pytest.mark.parametrize("bad_total", [0, -1])

def test_add_book_total_copies_not_positive(monkeypatch, bad_total):
    
    result, message = svc.add_book_to_catalog("Title", "Author", "1"*13, bad_total)
    
    assert result is False and "positive" in message.lower()

def test_add_book_duplicate_isbn(monkeypatch):

    monkeypatch.setattr(svc, "get_book_by_isbn", lambda isbn: {"id": 7, "isbn": isbn})
    
    result, message = svc.add_book_to_catalog("T", "A", "1"*13, 1)
    
    assert result is False and "exists" in message.lower()

def test_add_book_insert_failure_tuple_false(monkeypatch):
   
    monkeypatch.setattr(svc, "get_book_by_isbn", lambda isbn: None)

    monkeypatch.setattr(svc, "insert_book", lambda *a, **k: (False, "db err"))
    
    result, message = svc.add_book_to_catalog("T", "A", "1"*13, 1)
    
    assert result is False and ("database" in message.lower() or "error" in message.lower())

def test_add_book_insert_failure_bool_false(monkeypatch):
    
    monkeypatch.setattr(svc, "get_book_by_isbn", lambda isbn: None)

    monkeypatch.setattr(svc, "insert_book", lambda *a, **k: False)
    
    result, message = svc.add_book_to_catalog("T", "A", "1"*13, 1)
    
    assert result is False and ("database" in message.lower() or "error" in message.lower())

def test_add_book_success_tuple_true(monkeypatch):
    
    monkeypatch.setattr(svc, "get_book_by_isbn", lambda isbn: None)

    monkeypatch.setattr(svc, "insert_book", lambda *a, **k: (True, "ok"))
    
    result, message = svc.add_book_to_catalog(" Title  ", " Author ", "1"*13, 2)
    
    assert result is True and "success" in message.lower()
   