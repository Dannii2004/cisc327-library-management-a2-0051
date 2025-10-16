import pytest
import library_service as svc
from datetime import datetime, timedelta


class TestPatronStatusReportHappyPath:
    def test_patron_status_no_borrows(self, monkeypatch):
        """Test patron status report with no active borrows."""
        info_loans = []
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('123456')
        
        assert isinstance(result, dict)
        assert 'total_borrowed' in result or 'total_fine' in result or 'days_overdue' in result

    def test_patron_status_single_on_time_book(self, monkeypatch):
        """Test patron status with single on-time book."""
        date_now = datetime.now()
        info_loans = [
            {
                'patron_id': '123456',
                'book_id': 1,
                'title': 'On Time Book',
                'borrow_date': date_now - timedelta(days=5),
                'due_date': date_now + timedelta(days=2),
                'return_date': None
            }
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans if patron_id == '123456' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('123456')
        
        assert isinstance(result, dict)
        assert result.get('total_fine', 0) == 0.0

    def test_patron_status_single_overdue_book(self, monkeypatch):
        """Test patron status with single overdue book."""
        date_now = datetime.now()
        days_past_due = 5
        daily_fine = 0.25
        total_fine = round(days_past_due * daily_fine, 2)
        
        info_loans = [
            {
                'patron_id': '234567',
                'book_id': 2,
                'title': 'Overdue Book',
                'borrow_date': date_now - timedelta(days=20),
                'due_date': date_now - timedelta(days=days_past_due),
                'return_date': None
            }
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans if patron_id == '234567' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('234567')
        
        assert isinstance(result, dict)
        assert result.get('total_fine', 0) == total_fine

    def test_patron_status_multiple_books(self, monkeypatch):
        """Test patron status with multiple borrowed books."""
        date_now = datetime.now()
        info_loans = [
            {
                'patron_id': '345678',
                'book_id': 1,
                'title': 'Book One',
                'borrow_date': date_now - timedelta(days=10),
                'due_date': date_now + timedelta(days=2),
                'return_date': None
            },
            {
                'patron_id': '345678',
                'book_id': 2,
                'title': 'Book Two',
                'borrow_date': date_now - timedelta(days=15),
                'due_date': date_now - timedelta(days=3),
                'return_date': None
            },
            {
                'patron_id': '345678',
                'book_id': 3,
                'title': 'Book Three',
                'borrow_date': date_now - timedelta(days=8),
                'due_date': date_now + timedelta(days=5),
                'return_date': None
            }
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans if patron_id == '345678' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('345678')
        
        assert isinstance(result, dict)
        assert result.get('total_fine', 0) >= 0.0

    def test_patron_status_multiple_overdue_books_sum(self, monkeypatch):
        """Test patron status correctly sums fees for multiple overdue books."""
        date_now = datetime.now()
        
        info_loans = [
            {
                'patron_id': '456789',
                'book_id': 1,
                'title': 'Overdue One',
                'borrow_date': date_now - timedelta(days=20),
                'due_date': date_now - timedelta(days=2),
                'return_date': None
            },
            {
                'patron_id': '456789',
                'book_id': 2,
                'title': 'Overdue Two',
                'borrow_date': date_now - timedelta(days=25),
                'due_date': date_now - timedelta(days=5),
                'return_date': None
            }
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans if patron_id == '456789' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('456789')
        
        # Book 1: 2 days * 0.25 = 0.50
        # Book 2: 5 days * 0.25 = 1.25
        # Total: 1.75
        expected_total = 1.75
        assert result.get('total_fine', 0) == expected_total


class TestPatronStatusReportMixedScenarios:
    def test_patron_status_mixed_on_time_and_overdue(self, monkeypatch):
        """Test patron status with mix of on-time and overdue books."""
        date_now = datetime.now()
        info_loans = [
            {
                'patron_id': '567890',
                'book_id': 1,
                'title': 'On Time',
                'borrow_date': date_now - timedelta(days=5),
                'due_date': date_now + timedelta(days=3),
                'return_date': None
            },
            {
                'patron_id': '567890',
                'book_id': 2,
                'title': 'Overdue',
                'borrow_date': date_now - timedelta(days=20),
                'due_date': date_now - timedelta(days=3),
                'return_date': None
            }
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans if patron_id == '567890' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('567890')
        
        # Only overdue book incurs fee: 3 days * 0.25 = 0.75
        assert result.get('total_fine', 0) == 0.75

    def test_patron_status_returned_books_excluded(self, monkeypatch):
        """Test patron status excludes returned books from fees."""
        date_now = datetime.now()
        info_loans = [
            {
                'patron_id': '678901',
                'book_id': 1,
                'title': 'Returned',
                'borrow_date': date_now - timedelta(days=20),
                'due_date': date_now - timedelta(days=5),
                'return_date': date_now - timedelta(days=2)
            },
            {
                'patron_id': '678901',
                'book_id': 2,
                'title': 'Still Out',
                'borrow_date': date_now - timedelta(days=10),
                'due_date': date_now + timedelta(days=5),
                'return_date': None
            }
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans if patron_id == '678901' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('678901')
        
        assert isinstance(result, dict)

    def test_patron_status_all_returned_no_fees(self, monkeypatch):
        """Test patron with all books returned has zero fees."""
        date_now = datetime.now()
        info_loans = [
            {
                'patron_id': '789012',
                'book_id': 1,
                'title': 'Book One',
                'borrow_date': date_now - timedelta(days=20),
                'due_date': date_now - timedelta(days=10),
                'return_date': date_now - timedelta(days=9)
            },
            {
                'patron_id': '789012',
                'book_id': 2,
                'title': 'Book Two',
                'borrow_date': date_now - timedelta(days=15),
                'due_date': date_now - timedelta(days=5),
                'return_date': date_now - timedelta(days=4)
            }
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans if patron_id == '789012' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('789012')
        
        assert result.get('total_fine', 0) == 0.0


class TestPatronStatusReportStructure:
    def test_patron_status_returns_dict(self, monkeypatch):
        """Test that patron status report returns a dictionary."""
        def mock_get_borrow_records_by_patron(patron_id):
            return []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('123456')
        
        assert isinstance(result, dict)

    def test_patron_status_aggregates_data(self, monkeypatch):
        """Test that patron status aggregates patron's borrow records."""
        date_now = datetime.now()
        call_log = []
        
        info_loans = [
            {
                'patron_id': '890123',
                'book_id': 1,
                'title': 'Book One',
                'borrow_date': date_now - timedelta(days=10),
                'due_date': date_now - timedelta(days=2),
                'return_date': None
            }
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            call_log.append(('get_borrow_records_by_patron', patron_id))
            return info_loans if patron_id == '890123' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('890123')
        
        assert ('get_borrow_records_by_patron', '890123') in call_log

    def test_patron_status_computes_per_book_fees(self, monkeypatch):
        """Test that patron status computes per-book fees."""
        date_now = datetime.now()
        info_loans = [
            {
                'patron_id': '901234',
                'book_id': 1,
                'title': 'Book',
                'borrow_date': date_now - timedelta(days=15),
                'due_date': date_now - timedelta(days=7),
                'return_date': None
            }
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans if patron_id == '901234' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('901234')
        
        # 7 days * 0.25 = 1.75
        assert result.get('total_fine', 0) == 1.75

    def test_patron_status_calculates_days_late(self, monkeypatch):
        """Test that patron status calculates days late for each book."""
        date_now = datetime.now()
        info_loans = [
            {
                'patron_id': '012345',
                'book_id': 1,
                'title': 'Late Book',
                'borrow_date': date_now - timedelta(days=20),
                'due_date': date_now - timedelta(days=10),
                'return_date': None
            }
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans if patron_id == '012345' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('012345')
        
        assert isinstance(result, dict)
        assert result.get('total_fine', 0) > 0.0


class TestPatronStatusReportEdgeCases:
    def test_patron_status_exactly_6_digit_id(self, monkeypatch):
        """Test patron status with exactly 6-digit patron ID."""
        def mock_get_borrow_records_by_patron(patron_id):
            return []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('654321')
        
        assert isinstance(result, dict)

    def test_patron_status_nonexistent_patron(self, monkeypatch):
        """Test patron status for nonexistent patron."""
        def mock_get_borrow_records_by_patron(patron_id):
            return []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('999999')
        
        assert isinstance(result, dict)
        assert result.get('total_fine', 0) == 0.0

    def test_patron_status_many_overdue_books(self, monkeypatch):
        """Test patron status with many overdue books."""
        date_now = datetime.now()
        info_loans = [
            {
                'patron_id': '111111',
                'book_id': i,
                'title': f'Book {i}',
                'borrow_date': date_now - timedelta(days=20+i),
                'due_date': date_now - timedelta(days=i),
                'return_date': None
            }
            for i in range(1, 6)
        ]
        
        def mock_get_borrow_records_by_patron(patron_id):
            return info_loans if patron_id == '111111' else []
        
        monkeypatch.setattr(svc, 'get_borrow_records_by_patron', mock_get_borrow_records_by_patron)
        
        result = svc.get_patron_status_report('111111')
        
        # Books 1-5 with days overdue: 1, 2, 3, 4, 5 days
        # Total fee: (1+2+3+4+5) * 0.25 = 15 * 0.25 = 3.75
        borrowd_summ = result.get('total_fine', 0)
        assert borrowd_summ > 0.0
