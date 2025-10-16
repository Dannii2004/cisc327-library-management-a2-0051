import library_service as svc
from datetime import datetime, timedelta
import database

def test_r7_status_shape_and_totals(monkeypatch):
    now = datetime.now()
    recs = [
        {"title":"Book A","isbn":"AAA","due_date": now - timedelta(days=3), "return_date": None},
        {"title":"Book B","isbn":"BBB","due_date": now + timedelta(days=2), "return_date": None},
        {"title":"Book C","isbn":"CCC","due_date": now - timedelta(days=1), "return_date": now}
    ]
    monkeypatch.setattr(database, "get_borrow_records_by_patron", lambda pid: recs, raising=False)
    rep = svc.get_patron_status_report("765432")
    assert rep["patron_id"] == "765432"
    assert isinstance(rep["borrowed_books"], list)
    assert "total_late_fees" in rep
    assert any(item["isbn"] == "AAA" and item["days_late"] >= 3 for item in rep["borrowed_books"])
    assert rep["total_late_fees"] >= 0.75

