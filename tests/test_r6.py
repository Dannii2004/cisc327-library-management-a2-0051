import pytest

import library_service as svc

def test_r6_title_partial_case_insensitive(monkeypatch):
    monkeypatch.setattr(svc, "get_all_books", lambda: [
        {"id":1,"title":"And Then There Were None","author":"Agatha Christie",
         "isbn":"1312109876543","available_copies":1,"total_copies":1},
        {"id":2,"title":"A Tale of Two Cities","author":"Charles Dickens",
         "isbn":"1312109876543","available_copies":1,"total_copies":1}
    ])
    match = svc.search_books_in_catalog("none", "title")
    assert any(b["title"].lower() == "and then there were none" for b in match)

def test_r6_isbn_exact(monkeypatch):
    monkeypatch.setattr(svc, "get_all_books", lambda: [
        {"id":3,"title":"The Da Vinci Code","author":"Dan Brown",
         "isbn":"1312109876543","available_copies":1,"total_copies":1}
    ])
    yes = svc.search_books_in_catalog("1312109876543", "isbn")
    no  = svc.search_books_in_catalog("36829", "isbn")
    assert any(b["isbn"] == "1312109876543" for b in yes)
    assert not no

def test_r6_author_partial(monkeypatch):
    monkeypatch.setattr(svc, "get_all_books", lambda: [
        {"id":4,"title":"Murder on the Orient Express","author":"Agatha Christie",
         "isbn":"1111111111111","available_copies":1,"total_copies":1}
    ])
    match = svc.search_books_in_catalog("christie", "author")
    assert len(match) == 1 and match[0]["author"] == "Agatha Christie"
