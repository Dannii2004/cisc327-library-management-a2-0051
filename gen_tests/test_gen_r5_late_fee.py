import pytest
import library_service as svc
from datetime import datetime, timedelta


class TestCalculateLateFeeHappyPath:
    def test_calculate_late_fee_no_overdue(self, monkeypatch):
        """Test fee calculation when book is not overdue."""
        info_book = {
            'id': 1,
            'title': 'On Time Book',
            'author': 'Author One',
            'isbn': '1111111111111',
            'total_copies': 5,
            'available_copies': 3
        }
        
        date_now = datetime.now()
        due_date = date_now + timedelta(days=5)
        
        info_loan = {
            'patron_id': '123456',
            'book_id': 1,
            'borrow_date': date_now,
            'due_date': due_date,
            'return_date': None
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 1 else None
        
        def mock_get_borrow_record(patron_id, book_id):
            return info_loan if (patron_id == '123456' and book_id == 1) else None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_borrow_record', mock_get_borrow_record)
        
        result = svc.calculate_late_fee_for_book('123456', 1)
        
        assert isinstance(result, dict)
        assert result['fee_amount'] == 0.0
        assert result['days_overdue'] == 0

    def test_calculate_late_fee_one_day_overdue(self, monkeypatch):
        """Test fee calculation for 1 day overdue."""
        info_book = {
            'id': 2,
            'title': 'One Day Late',
            'author': 'Author Two',
            'isbn': '2222222222222',
            'total_copies': 10,
            'available_copies': 5
        }
        
        date_now = datetime.now()
        due_date = date_now - timedelta(days=1)
        days_past_due = 1
        daily_fine = 0.25
        total_fine = round(days_past_due * daily_fine, 2)
        
        info_loan = {
            'patron_id': '234567',
            'book_id': 2,
            'borrow_date': date_now - timedelta(days=15),
            'due_date': due_date,
            'return_date': None
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 2 else None
        
        def mock_get_borrow_record(patron_id, book_id):
            return info_loan if (patron_id == '234567' and book_id == 2) else None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_borrow_record', mock_get_borrow_record)
        
        result = svc.calculate_late_fee_for_book('234567', 2)
        
        assert result['fee_amount'] == total_fine
        assert result['days_overdue'] == days_past_due

    def test_calculate_late_fee_multiple_days_overdue(self, monkeypatch):
        """Test fee calculation for multiple days overdue."""
        info_book = {
            'id': 3,
            'title': 'Very Late Book',
            'author': 'Author Three',
            'isbn': '3333333333333',
            'total_copies': 3,
            'available_copies': 1
        }
        
        date_now = datetime.now()
        due_date = date_now - timedelta(days=10)
        days_past_due = 10
        daily_fine = 0.25
        total_fine = round(days_past_due * daily_fine, 2)
        
        info_loan = {
            'patron_id': '345678',
            'book_id': 3,
            'borrow_date': date_now - timedelta(days=25),
            'due_date': due_date,
            'return_date': None
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 3 else None
        
        def mock_get_borrow_record(patron_id, book_id):
            return info_loan if (patron_id == '345678' and book_id == 3) else None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_borrow_record', mock_get_borrow_record)
        
        result = svc.calculate_late_fee_for_book('345678', 3)
        
        assert result['fee_amount'] == total_fine
        assert result['days_overdue'] == days_past_due

    def test_calculate_late_fee_rounding(self, monkeypatch):
        """Test fee calculation is rounded to 2 decimal places."""
        info_book = {
            'id': 4,
            'title': 'Rounding Test',
            'author': 'Author Four',
            'isbn': '4444444444444',
            'total_copies': 5,
            'available_copies': 2
        }
        
        date_now = datetime.now()
        due_date = date_now - timedelta(days=3)
        
        info_loan = {
            'patron_id': '456789',
            'book_id': 4,
            'borrow_date': date_now - timedelta(days=20),
            'due_date': due_date,
            'return_date': None
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 4 else None
        
        def mock_get_borrow_record(patron_id, book_id):
            return info_loan if (patron_id == '456789' and book_id == 4) else None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_borrow_record', mock_get_borrow_record)
        
        result = svc.calculate_late_fee_for_book('456789', 4)
        
        assert isinstance(result['fee_amount'], float)
        assert len(str(result['fee_amount']).split('.')[-1]) <= 2


class TestCalculateLateFeeDictStructure:
    def test_calculate_late_fee_returns_dict_with_required_keys(self, monkeypatch):
        """Test that result dict contains required keys."""
        info_book = {
            'id': 5,
            'title': 'Key Test',
            'author': 'Author Five',
            'isbn': '5555555555555',
            'total_copies': 5,
            'available_copies': 3
        }
        
        info_loan = {
            'patron_id': '567890',
            'book_id': 5,
            'borrow_date': datetime.now() - timedelta(days=10),
            'due_date': datetime.now() - timedelta(days=2),
            'return_date': None
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 5 else None
        
        def mock_get_borrow_record(patron_id, book_id):
            return info_loan if (patron_id == '567890' and book_id == 5) else None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_borrow_record', mock_get_borrow_record)
        
        result = svc.calculate_late_fee_for_book('567890', 5)
        
        assert 'fee_amount' in result
        assert 'days_overdue' in result
        assert 'status' in result


class TestCalculateLateFeeMissingData:
    def test_calculate_late_fee_book_not_found(self, monkeypatch):
        """Test fee calculation when book not found."""
        def mock_get_book_by_id(book_id):
            return None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        
        result = svc.calculate_late_fee_for_book('123456', 999)
        
        assert isinstance(result, dict)
        assert result['fee_amount'] == 0
        assert 'not found' in result['status'].lower() or 'not' in result['status'].lower()

    def test_calculate_late_fee_borrow_record_not_found(self, monkeypatch):
        """Test fee calculation when borrow record not located."""
        info_book = {
            'id': 6,
            'title': 'Found Book',
            'author': 'Author Six',
            'isbn': '6666666666666',
            'total_copies': 5,
            'available_copies': 3
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 6 else None
        
        def mock_get_borrow_record(patron_id, book_id):
            return None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_borrow_record', mock_get_borrow_record)
        
        result = svc.calculate_late_fee_for_book('678901', 6)
        
        assert result['fee_amount'] == 0
        assert 'not located' in result['status'].lower() or 'not found' in result['status'].lower()

    def test_calculate_late_fee_returned_book(self, monkeypatch):
        """Test fee calculation for already returned book (return_date set)."""
        info_book = {
            'id': 7,
            'title': 'Already Returned',
            'author': 'Author Seven',
            'isbn': '7777777777777',
            'total_copies': 5,
            'available_copies': 4
        }
        
        date_now = datetime.now()
        due_date = date_now - timedelta(days=5)
        
        info_loan = {
            'patron_id': '789012',
            'book_id': 7,
            'borrow_date': date_now - timedelta(days=20),
            'due_date': due_date,
            'return_date': due_date + timedelta(days=3)
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 7 else None
        
        def mock_get_borrow_record(patron_id, book_id):
            return info_loan if (patron_id == '789012' and book_id == 7) else None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_borrow_record', mock_get_borrow_record)
        
        result = svc.calculate_late_fee_for_book('789012', 7)
        
        assert isinstance(result, dict)
        assert 'fee_amount' in result


class TestCalculateLateFeeFeeCalculation:
    def test_calculate_late_fee_exactly_25_cents_per_day(self, monkeypatch):
        """Test that fee is exactly 0.25 per day."""
        info_book = {
            'id': 8,
            'title': 'Precision Test',
            'author': 'Author Eight',
            'isbn': '8888888888888',
            'total_copies': 5,
            'available_copies': 3
        }
        
        date_now = datetime.now()
        due_date = date_now - timedelta(days=7)
        
        info_loan = {
            'patron_id': '890123',
            'book_id': 8,
            'borrow_date': date_now - timedelta(days=22),
            'due_date': due_date,
            'return_date': None
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 8 else None
        
        def mock_get_borrow_record(patron_id, book_id):
            return info_loan if (patron_id == '890123' and book_id == 8) else None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_borrow_record', mock_get_borrow_record)
        
        result = svc.calculate_late_fee_for_book('890123', 8)
        
        expected_fee = round(7 * 0.25, 2)
        assert result['fee_amount'] == expected_fee