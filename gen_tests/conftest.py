import pytest
from services import library_service as svc

@pytest.fixture(autouse=True)
def _ai_isolation(monkeypatch, request):
    if "gen_tests" in str(getattr(request.node, "fspath", "")):
        monkeypatch.setattr(svc, "get_book_by_isbn", lambda _: None, raising=False)
        monkeypatch.setattr(svc, "insert_book", lambda *a, **k: True, raising=False)
