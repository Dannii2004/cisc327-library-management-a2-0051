import pytest
import library_service as svc


class TestBorrowBookHappyPath:
    def test_borrow_book_success(self, monkeypatch):
        """Test successful book borrowing."""
        info_book = {
            'id': 1,
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890123',
            'total_copies': 5,
            'available_copies': 3
        }
        
        call_log = []
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 1 else None
        
        def mock_get_patron_borrow_count(patron_id):
            return 0
        
        def mock_insert_borrow_record(patron_id, book_id, borrow_date, due_date):
            call_log.append(('insert_borrow_record', patron_id, book_id))
            return True
        
        def mock_update_book_availability(book_id, delta):
            call_log.append(('update_book_availability', book_id, delta))
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_patron_borrow_count', mock_get_patron_borrow_count)
        monkeypatch.setattr(svc, 'insert_borrow_record', mock_insert_borrow_record)
        monkeypatch.setattr(svc, 'update_book_availability', mock_update_book_availability)
        
        success, message = svc.borrow_book_by_patron('123456', 1)
        
        assert success is True
        assert ('insert_borrow_record', '123456', 1) in call_log
        assert ('update_book_availability', 1, -1) in call_log

    def test_borrow_book_patron_at_limit_minus_one(self, monkeypatch):
        """Test borrowing when patron has 4 books (limit is 5)."""
        info_book = {
            'id': 2,
            'title': 'Book Two',
            'author': 'Author Two',
            'isbn': '2222222222222',
            'total_copies': 10,
            'available_copies': 5
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 2 else None
        
        def mock_get_patron_borrow_count(patron_id):
            return 4
        
        def mock_insert_borrow_record(patron_id, book_id, borrow_date, due_date):
            return True
        
        def mock_update_book_availability(book_id, delta):
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_patron_borrow_count', mock_get_patron_borrow_count)
        monkeypatch.setattr(svc, 'insert_borrow_record', mock_insert_borrow_record)
        monkeypatch.setattr(svc, 'update_book_availability', mock_update_book_availability)
        
        success, message = svc.borrow_book_by_patron('234567', 2)
        
        assert success is True

    def test_borrow_book_last_available_copy(self, monkeypatch):
        """Test borrowing last available copy."""
        info_book = {
            'id': 3,
            'title': 'Rare Book',
            'author': 'Rare Author',
            'isbn': '3333333333333',
            'total_copies': 5,
            'available_copies': 1
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 3 else None
        
        def mock_get_patron_borrow_count(patron_id):
            return 0
        
        def mock_insert_borrow_record(patron_id, book_id, borrow_date, due_date):
            return True
        
        def mock_update_book_availability(book_id, delta):
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_patron_borrow_count', mock_get_patron_borrow_count)
        monkeypatch.setattr(svc, 'insert_borrow_record', mock_insert_borrow_record)
        monkeypatch.setattr(svc, 'update_book_availability', mock_update_book_availability)
        
        success, message = svc.borrow_book_by_patron('345678', 3)
        
        assert success is True


class TestBorrowBookEdgeCases:
    def test_borrow_book_patron_id_exactly_6_digits(self, monkeypatch):
        """Test with patron ID exactly 6 digits."""
        info_book = {
            'id': 4,
            'title': 'Valid Book',
            'author': 'Valid Author',
            'isbn': '4444444444444',
            'total_copies': 5,
            'available_copies': 2
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 4 else None
        
        def mock_get_patron_borrow_count(patron_id):
            return 0
        
        def mock_insert_borrow_record(patron_id, book_id, borrow_date, due_date):
            return True
        
        def mock_update_book_availability(book_id, delta):
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_patron_borrow_count', mock_get_patron_borrow_count)
        monkeypatch.setattr(svc, 'insert_borrow_record', mock_insert_borrow_record)
        monkeypatch.setattr(svc, 'update_book_availability', mock_update_book_availability)
        
        success, message = svc.borrow_book_by_patron('456789', 4)
        
        assert success is True

    def test_borrow_book_no_available_copies(self, monkeypatch):
        """Test borrowing when no copies available."""
        info_book = {
            'id': 5,
            'title': 'All Borrowed',
            'author': 'Borrowed Author',
            'isbn': '5555555555555',
            'total_copies': 5,
            'available_copies': 0
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 5 else None
        
        def mock_get_patron_borrow_count(patron_id):
            return 0
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_patron_borrow_count', mock_get_patron_borrow_count)
        
        success, message = svc.borrow_book_by_patron('567890', 5)
        
        assert success is False
        assert 'available' in message.lower() or 'copies' in message.lower()


class TestBorrowBookInvalidInputs:
    def test_borrow_book_patron_id_too_short(self, monkeypatch):
        """Test rejection of patron ID less than 6 digits."""
        monkeypatch.setattr(svc, 'get_book_by_id', lambda x: None, raising=False)
        
        success, message = svc.borrow_book_by_patron('12345', 1)
        
        assert success is False
        assert 'patron' in message.lower()

    def test_borrow_book_patron_id_too_long(self, monkeypatch):
        """Test rejection of patron ID more than 6 digits."""
        monkeypatch.setattr(svc, 'get_book_by_id', lambda x: None, raising=False)
        
        success, message = svc.borrow_book_by_patron('1234567', 1)
        
        assert success is False

    def test_borrow_book_patron_id_non_numeric(self, monkeypatch):
        """Test rejection of non-numeric patron ID."""
        monkeypatch.setattr(svc, 'get_book_by_id', lambda x: None, raising=False)
        
        success, message = svc.borrow_book_by_patron('12345A', 1)
        
        assert success is False

    def test_borrow_book_nonexistent_book(self, monkeypatch):
        """Test borrowing nonexistent book."""
        def mock_get_book_by_id(book_id):
            return None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        
        success, message = svc.borrow_book_by_patron('123456', 999)
        
        assert success is False
        assert 'book' in message.lower() or 'found' in message.lower()

    def test_borrow_book_patron_at_limit_5(self, monkeypatch):
        """Test rejection when patron already has 5 books."""
        info_book = {
            'id': 6,
            'title': 'Limited Book',
            'author': 'Limited Author',
            'isbn': '6666666666666',
            'total_copies': 10,
            'available_copies': 5
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 6 else None
        
        def mock_get_patron_borrow_count(patron_id):
            return 5
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_patron_borrow_count', mock_get_patron_borrow_count)
        
        success, message = svc.borrow_book_by_patron('678901', 6)
        
        assert success is False
        assert 'limit' in message.lower() or 'maximum' in message.lower()

    def test_borrow_book_patron_over_limit(self, monkeypatch):
        """Test rejection when patron exceeds limit."""
        info_book = {
            'id': 7,
            'title': 'Over Limit Book',
            'author': 'Over Author',
            'isbn': '7777777777777',
            'total_copies': 8,
            'available_copies': 4
        }
        
        def mock_get_book_by_id(book_id):
            return info_book if book_id == 7 else None
        
        def mock_get_patron_borrow_count(patron_id):
            return 6
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        monkeypatch.setattr(svc, 'get_patron_borrow_count', mock_get_patron_borrow_count)
        
        success, message = svc.borrow_book_by_patron('789012', 7)
        
        assert success is False

    def test_borrow_book_invalid_book_id(self, monkeypatch):
        """Test borrowing with invalid book ID."""
        def mock_get_book_by_id(book_id):
            return None
        
        monkeypatch.setattr(svc, 'get_book_by_id', mock_get_book_by_id)
        
        success, message = svc.borrow_book_by_patron('123456', -1)
        
        assert success is False

    def test_borrow_book_empty_patron_id(self, monkeypatch):
        """Test borrowing with empty patron ID."""
        monkeypatch.setattr(svc, 'get_book_by_id', lambda x: None, raising=False)
        
        success, message = svc.borrow_book_by_patron('', 1)
        
        assert success is False