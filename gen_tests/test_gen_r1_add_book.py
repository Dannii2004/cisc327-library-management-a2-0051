import pytest
import library_service as svc
from datetime import datetime


class TestAddBookHappyPath:
    def test_add_book_success(self, monkeypatch):
        """Test successful book addition with valid inputs."""
        call_log = []
        
        def mock_get_book_by_isbn(isbn):
            call_log.append(('get_book_by_isbn', isbn))
            return None
        
        def mock_insert_book(title, author, isbn, total, available):
            call_log.append(('insert_book', title, author, isbn, total, available))
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_isbn', mock_get_book_by_isbn)
        monkeypatch.setattr(svc, 'insert_book', mock_insert_book)
        
        success, message = svc.add_book_to_catalog('Python Mastery', 'John Doe', '1234567890123', 10)
        
        assert success is True
        assert 'success' in message.lower() or 'added' in message.lower()
        assert ('get_book_by_isbn', '1234567890123') in call_log
        assert ('insert_book', 'Python Mastery', 'John Doe', '1234567890123', 10, 10) in call_log

    def test_add_book_single_copy(self, monkeypatch):
        """Test adding book with minimum valid copies."""
        call_log = []
        
        def mock_get_book_by_isbn(isbn):
            return None
        
        def mock_insert_book(title, author, isbn, total, available):
            call_log.append(('insert_book', total, available))
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_isbn', mock_get_book_by_isbn)
        monkeypatch.setattr(svc, 'insert_book', mock_insert_book)
        
        success, message = svc.add_book_to_catalog('Single Copy', 'Author', '9876543210987', 1)
        
        assert success is True
        assert ('insert_book', 1, 1) in call_log

    def test_add_book_many_copies(self, monkeypatch):
        """Test adding book with large copy count."""
        def mock_get_book_by_isbn(isbn):
            return None
        
        def mock_insert_book(title, author, isbn, total, available):
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_isbn', mock_get_book_by_isbn)
        monkeypatch.setattr(svc, 'insert_book', mock_insert_book)
        
        success, message = svc.add_book_to_catalog('Popular Book', 'Author', '1111111111111', 1000)
        
        assert success is True


class TestAddBookEdgeCases:
    def test_add_book_max_title_length(self, monkeypatch):
        """Test adding book with maximum valid title length (200 chars)."""
        title = 'A' * 200
        
        def mock_get_book_by_isbn(isbn):
            return None
        
        def mock_insert_book(title, author, isbn, total, available):
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_isbn', mock_get_book_by_isbn)
        monkeypatch.setattr(svc, 'insert_book', mock_insert_book)
        
        success, message = svc.add_book_to_catalog(title, 'Author', '1234567890123', 5)
        
        assert success is True

    def test_add_book_max_author_length(self, monkeypatch):
        """Test adding book with maximum valid author length (100 chars)."""
        author = 'B' * 100
        
        def mock_get_book_by_isbn(isbn):
            return None
        
        def mock_insert_book(title, author, isbn, total, available):
            return True
        
        monkeypatch.setattr(svc, 'get_book_by_isbn', mock_get_book_by_isbn)
        monkeypatch.setattr(svc, 'insert_book', mock_insert_book)
        
        success, message = svc.add_book_to_catalog('Title', author, '1234567890123', 5)
        
        assert success is True

    def test_add_book_duplicate_isbn(self, monkeypatch):
        """Test rejection of duplicate ISBN."""
        existing_book = {
            'id': 1,
            'title': 'Existing Book',
            'author': 'Existing Author',
            'isbn': '1234567890123',
            'total_copies': 5,
            'available_copies': 5
        }
        
        def mock_get_book_by_isbn(isbn):
            if isbn == '1234567890123':
                return existing_book
            return None
        
        monkeypatch.setattr(svc, 'get_book_by_isbn', mock_get_book_by_isbn)
        
        success, message = svc.add_book_to_catalog('New Book', 'New Author', '1234567890123', 5)
        
        assert success is False
        assert 'duplicate' in message.lower() or 'exists' in message.lower()


class TestAddBookInvalidInputs:
    def test_add_book_title_too_long(self, monkeypatch):
        """Test rejection of title exceeding 200 chars."""
        title = 'A' * 201
        
        monkeypatch.setattr(svc, 'get_book_by_isbn', lambda x: None, raising=False)
        
        success, message = svc.add_book_to_catalog(title, 'Author', '1234567890123', 5)
        
        assert success is False
        assert 'title' in message.lower()

    def test_add_book_author_too_long(self, monkeypatch):
        """Test rejection of author exceeding 100 chars."""
        author = 'A' * 101
        
        monkeypatch.setattr(svc, 'get_book_by_isbn', lambda x: None, raising=False)
        
        success, message = svc.add_book_to_catalog('Title', author, '1234567890123', 5)
        
        assert success is False
        assert 'author' in message.lower()

    def test_add_book_isbn_not_13_digits(self, monkeypatch):
        """Test rejection of ISBN not exactly 13 digits."""
        monkeypatch.setattr(svc, 'get_book_by_isbn', lambda x: None, raising=False)
        
        # Too short
        success, message = svc.add_book_to_catalog('Title', 'Author', '123456789012', 5)
        assert success is False
        
        # Too long
        success, message = svc.add_book_to_catalog('Title', 'Author', '12345678901234', 5)
        assert success is False
        
        # Non-numeric
        success, message = svc.add_book_to_catalog('Title', 'Author', '123456789012A', 5)
        assert success is False

    def test_add_book_zero_copies(self, monkeypatch):
        """Test rejection of zero total copies."""
        monkeypatch.setattr(svc, 'get_book_by_isbn', lambda x: None, raising=False)
        
        success, message = svc.add_book_to_catalog('Title', 'Author', '1234567890123', 0)
        
        assert success is False
        assert 'copies' in message.lower() or 'positive' in message.lower()

    def test_add_book_negative_copies(self, monkeypatch):
        """Test rejection of negative total copies."""
        monkeypatch.setattr(svc, 'get_book_by_isbn', lambda x: None, raising=False)
        
        success, message = svc.add_book_to_catalog('Title', 'Author', '1234567890123', -5)
        
        assert success is False

    def test_add_book_empty_title(self, monkeypatch):
        """Test rejection of empty title."""
        monkeypatch.setattr(svc, 'get_book_by_isbn', lambda x: None, raising=False)
        
        success, message = svc.add_book_to_catalog('', 'Author', '1234567890123', 5)
        
        assert success is False

    def test_add_book_empty_author(self, monkeypatch):
        """Test rejection of empty author."""
        monkeypatch.setattr(svc, 'get_book_by_isbn', lambda x: None, raising=False)
        
        success, message = svc.add_book_to_catalog('Title', '', '1234567890123', 5)
        
        assert success is False