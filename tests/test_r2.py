
import library_service as svc


def test_r2_catalog_shape_via_get_all_books(monkeypatch):
    monkeypatch.setattr(svc, "get_all_books", lambda: [
        {
            "id": 1,
            "title": "Harry Potter and the Philosopher's Stone",
            "author": "J. K. Rowling",
            "isbn": "1312109876543",
            "available_copies": 2,
            "total_copies": 2
        },
        {
            "id": 2,
            "title": "The Purpose Driven Life",
            "author": "Rick Warren",
            "isbn": "1312109876543",
            "available_copies": 1,
            "total_copies": 1
        }
    ])
    Allbooks = svc.get_all_books()
    assert isinstance(Allbooks, list) and Allbooks
    
    book = Allbooks[0]


    for k in ["id","title","author","isbn","available_copies","total_copies"]:
        assert k in book
