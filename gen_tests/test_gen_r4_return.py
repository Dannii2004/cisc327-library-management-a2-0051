import pytest
import library_service as svc


class TestReturnBookHappyPath:
    def test_return_book_success(self, monkeypatch):
        """Test successful book return."""
        info_book = {
            'id': 1,
            'title': 'Return Test Book',
            'author': 'Return Author',
            'isbn': '1234567890123',
            'total_copies': 5,
            'available_copies': 3
        }
        
        call_log = []
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 1 else None
        
        def mock_update_borrow_record_return_date(patron_id, book_id, return_date):
            call_log.append(('update_borrow_record_return_date', patron_id, book_id))
            return True
        
        def mock_update_book_availability(book_id, delta):
            call_log.append(('update_book_availability', book_id, delta))
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'update_borrow_record_return_date', mock_update_borrow_record_return_date)
        monkeypatch.setattr(svc, 'update_book_availability', mock_update_book_availability)
        
        success, message = svc.return_book_by_patron('123456', 1)
        
        assert success is True
        assert ('update_borrow_record_return_date', '123456', 1) in call_log
        assert ('update_book_availability', 1, 1) in call_log

    def test_return_book_increases_availability(self, monkeypatch):
        """Test that return increases available copies by 1."""
        info_book = {
            'id': 2,
            'title': 'Book Two',
            'author': 'Author Two',
            'isbn': '2222222222222',
            'total_copies': 10,
            'available_copies': 5
        }
        
        call_log = []
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 2 else None
        
        def mock_update_borrow_record_return_date(patron_id, book_id, return_date):
            call_log.append('update_borrow_record_return_date')
            return True
        
        def mock_update_book_availability(book_id, delta):
            call_log.append(('update_book_availability', delta))
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'update_borrow_record_return_date', mock_update_borrow_record_return_date)
        monkeypatch.setattr(svc, 'update_book_availability', mock_update_book_availability)
        
        success, message = svc.return_book_by_patron('234567', 2)
        
        assert success is True
        assert ('update_book_availability', 1) in call_log


class TestReturnBookEdgeCases:
    def test_return_book_patron_id_exactly_6_digits(self, monkeypatch):
        """Test return with patron ID exactly 6 digits."""
        info_book = {
            'id': 3,
            'title': 'Valid Book',
            'author': 'Valid Author',
            'isbn': '3333333333333',
            'total_copies': 5,
            'available_copies': 2
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 3 else None
        
        def mock_update_borrow_record_return_date(patron_id, book_id, return_date):
            return True
        
        def mock_update_book_availability(book_id, delta):
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'update_borrow_record_return_date', mock_update_borrow_record_return_date)
        monkeypatch.setattr(svc, 'update_book_availability', mock_update_book_availability)
        
        success, message = svc.return_book_by_patron('345678', 3)
        
        assert success is True

    def test_return_book_restores_to_total_copies(self, monkeypatch):
        """Test return when all copies were borrowed."""
        info_book = {
            'id': 4,
            'title': 'All Out',
            'author': 'Author Four',
            'isbn': '4444444444444',
            'total_copies': 3,
            'available_copies': 0
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 4 else None
        
        def mock_update_borrow_record_return_date(patron_id, book_id, return_date):
            return True
        
        def mock_update_book_availability(book_id, delta):
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'update_borrow_record_return_date', mock_update_borrow_record_return_date)
        monkeypatch.setattr(svc, 'update_book_availability', mock_update_book_availability)
        
        success, message = svc.return_book_by_patron('456789', 4)
        
        assert success is True


class TestReturnBookInvalidInputs:
    def test_return_book_patron_id_too_short(self, monkeypatch):
        """Test rejection of patron ID less than 6 digits."""
        monkeypatch.setattr(svc, 'get_book_by_id', lambda x: None, raising=False)
        
        success, message = svc.return_book_by_patron('12345', 1)
        
        assert success is False
        assert 'patron' in message.lower()

    def test_return_book_patron_id_too_long(self, monkeypatch):
        """Test rejection of patron ID more than 6 digits."""
        monkeypatch.setattr(svc, 'get_book_by_id', lambda x: None, raising=False)
        
        success, message = svc.return_book_by_patron('1234567', 1)
        
        assert success is False

    def test_return_book_patron_id_non_numeric(self, monkeypatch):
        """Test rejection of non-numeric patron ID."""
        monkeypatch.setattr(svc, 'get_book_by_id', lambda x: None, raising=False)
        
        success, message = svc.return_book_by_patron('12345A', 1)
        
        assert success is False

    def test_return_book_nonexistent_book(self, monkeypatch):
        """Test returning nonexistent book."""
        def mock_get_book_by_id(book_id):
            return None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        
        success, message = svc.return_book_by_patron('123456', 999)
        
        assert success is False
        assert 'book' in message.lower() or 'found' in message.lower()

    def test_return_book_no_active_borrow_record(self, monkeypatch):
        """Test return with no active borrow record."""
        info_book = {
            'id': 5,
            'title': 'Never Borrowed',
            'author': 'Author Five',
            'isbn': '5555555555555',
            'total_copies': 5,
            'available_copies': 5
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 5 else None
        
        def mock_update_borrow_record_return_date(patron_id, book_id, return_date):
            return False
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'update_borrow_record_return_date', mock_update_borrow_record_return_date)
        
        success, message = svc.return_book_by_patron('567890', 5)
        
        assert success is False
        assert 'borrow' in message.lower() or 'record' in message.lower()

    def test_return_book_invalid_book_id(self, monkeypatch):
        """Test return with invalid book ID."""
        def mock_get_book_by_id(book_id):
            return None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        
        success, message = svc.return_book_by_patron('123456', -1)
        
        assert success is False

    def test_return_book_empty_patron_id(self, monkeypatch):
        """Test return with empty patron ID."""
        monkeypatch.setattr(svc, 'get_book_by_id', lambda x: None, raising=False)
        
        success, message = svc.return_book_by_patron('', 1)
        
        assert success is False