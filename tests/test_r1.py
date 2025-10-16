import pytest

import library_service as svc

def noIsbn(isbn):
    return None

def trueDb(title, author, isbn, total_copies, available_copies):
    assert available_copies == total_copies
    return True

def falseDb(*args, **kwargs):
    return False


def test_r1_val(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_isbn", noIsbn)
    monkeypatch.setattr(svc, "insert_book", trueDb)
    reqMet, message = svc.add_book_to_catalog(
        "Harry Potter and the Philosopher's Stone", "J. K. Rowling", "1312109876543", 3
    )
    assert reqMet is True and "success" in message.lower()

def test_r1_rejects_empty_title(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_isbn", noIsbn)
    reqMet, message = svc.add_book_to_catalog(
        "", "Agatha Christie", "1312109876543", 7
    )
    assert reqMet is False and "title" in message.lower()



def test_r1_rejects_author_over_100(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_isbn", noIsbn)
    charsOver_max = "a" * 101
    reqMet, message = svc.add_book_to_catalog(
        "The Da Vinci Code", charsOver_max, "1312109876543", 5
    )
    assert reqMet is False and "author" in message.lower()


def test_r1_rejects_isbn_not_13(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_isbn", noIsbn)
    reqMet, message = svc.add_book_to_catalog(
        "Black Beauty", "Anna Sewell", "36829", 5
    )
    assert reqMet is False and "13 digits" in message

def test_r1_duplicate_isbn(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_isbn", lambda i: {"id": 1, "isbn": i})
    reqMet, message = svc.add_book_to_catalog(
        "Alice's Adventures in Wonderland", "Lewis Carroll", "1312109876543", 7
    )
    assert reqMet is False and "already exists" in message.lower()



def test_r1_db_insert_failure(monkeypatch):
    monkeypatch.setattr(svc, "get_book_by_isbn", noIsbn)
    monkeypatch.setattr(svc, "insert_book", falseDb)
    reqMet, message = svc.add_book_to_catalog(
        "A Tale of Two Cities", "Charles Dickens", "1312109876543", 10
    )
    assert reqMet is False and "database error" in message.lower()


























