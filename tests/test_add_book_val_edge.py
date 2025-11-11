
import pytest

from services.library_service import add_book_to_catalog

def test_add_book_rejects_blank_title(monkeypatch):

    ok, msg = add_book_to_catalog("", "Alexis Quill", "5555555555555", 1)
    assert ok is False

    assert "title" in msg.lower()

def test_add_book_rejects_long_title(monkeypatch):

    long_title = "T" * 201

    ok, msg = add_book_to_catalog(long_title, "Alexis Quill", "5555555555555", 1)
    
    assert ok is False
   
    assert "200" in msg  

def test_add_book_rejects_blank_author(monkeypatch):
   
    ok, msg = add_book_to_catalog("Refactoring Recipes", "   ", "5555555555555", 1)
   
    assert ok is False
    
    assert "author" in msg.lower()

def test_add_book_rejects_long_author(monkeypatch):
    
    long_author = "A" * 101
    
    ok, msg = add_book_to_catalog("Refactoring Recipes", long_author, "5555555555555", 1)
    
    assert ok is False
    
    assert "100" in msg  

def test_add_book_rejects_bad_isbn(monkeypatch):
    
    ok, msg = add_book_to_catalog("Refactoring Recipes", "Alexis Quill", "not_isbn13", 1)
    
    assert ok is False
    
    assert "isbn" in msg.lower()

def test_add_book_rejects_nonpositive_copies(monkeypatch):
    
    ok, msg = add_book_to_catalog("Refactoring Recipes", "Alexis Quill", "5555555555555", 0)
    
    assert ok is False
    
    assert "copies" in msg.lower()

def test_add_book_duplicate_isbn(monkeypatch):

    def fake_get(isbn): return {"id": 4042, "isbn": isbn}
    
    def fake_insert(*args, **kwargs): raise AssertionError("insert should not be called")

    import services.library_service as svc
    
    monkeypatch.setattr(svc, "get_book_by_isbn", fake_get)
    
    monkeypatch.setattr(svc, "insert_book", fake_insert)

    ok, msg = add_book_to_catalog("Refactoring Recipes", "Alexis Quill", "7777777777777", 1)
    
    assert ok is False
    
    assert "exists" in msg.lower()

def test_add_book_db_insert_success(monkeypatch):
    
    import services.library_service as svc
    
    monkeypatch.setattr(svc, "get_book_by_isbn", lambda isbn: None)
    
    monkeypatch.setattr(svc, "insert_book", lambda *a, **k: (True, "ok"))

    ok, msg = add_book_to_catalog("  Pragmatic Unit Tester  ", "  A. Q. Reviewer  ", "8888888888888", 2)
    
    assert ok is True
    
    assert "successfully" in msg.lower()

def test_add_book_db_insert_failure(monkeypatch):
    
    import services.library_service as svc
    
    monkeypatch.setattr(svc, "get_book_by_isbn", lambda isbn: None)
    
    monkeypatch.setattr(svc, "insert_book", lambda *a, **k: False)

    ok, msg = add_book_to_catalog("SICP v2", "H. Abelson", "9999999999999", 1)
    
    assert ok is False
    
    assert "database" in msg.lower()
