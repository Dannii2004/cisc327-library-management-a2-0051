import pytest
import library_service as svc


class TestSearchBooksHappyPath:
    def test_search_books_by_title(self, monkeypatch):
        """Test successful search by title."""
        info_book = {
            'id': 1,
            'title': 'Python Programming',
            'author': 'Guido van Rossum',
            'isbn': '1234567890123',
            'total_copies': 5,
            'available_copies': 3
        }
        
        def mock_get_all_books():
            return [info_book]
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Python', 'title')
        
        assert len(result) > 0
        assert any(book['id'] == 1 for book in result)

    def test_search_books_by_author(self, monkeypatch):
        """Test successful search by author."""
        info_book = {
            'id': 2,
            'title': 'Clean Code',
            'author': 'Robert Martin',
            'isbn': '9876543210987',
            'total_copies': 4,
            'available_copies': 2
        }
        
        def mock_get_all_books():
            return [info_book]
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Robert', 'author')
        
        assert len(result) > 0
        assert any(book['id'] == 2 for book in result)

    def test_search_books_by_isbn(self, monkeypatch):
        """Test search by ISBN (exact substring)."""
        info_book = {
            'id': 3,
            'title': 'Design Patterns',
            'author': 'Gang of Four',
            'isbn': '1111111111111',
            'total_copies': 6,
            'available_copies': 1
        }
        
        def mock_get_all_books():
            return [info_book]
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('1111111111111', 'isbn')
        
        assert len(result) > 0
        assert result[0]['isbn'] == '1111111111111'

    def test_search_books_multiple_results(self, monkeypatch):
        """Test search returning multiple matching books."""
        books = [
            {'id': 1, 'title': 'Python 101', 'author': 'Alice', 'isbn': '1111111111111', 'total_copies': 5, 'available_copies': 3},
            {'id': 2, 'title': 'Python Advanced', 'author': 'Bob', 'isbn': '2222222222222', 'total_copies': 3, 'available_copies': 1},
            {'id': 3, 'title': 'Java Basics', 'author': 'Charlie', 'isbn': '3333333333333', 'total_copies': 7, 'available_copies': 4}
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Python', 'title')
        
        assert len(result) == 2
        assert all(book['title'].lower().count('python') > 0 for book in result)

    def test_search_books_case_insensitive(self, monkeypatch):
        """Test case-insensitive search."""
        info_book = {
            'id': 4,
            'title': 'THE GREAT BOOK',
            'author': 'AUTHOR NAME',
            'isbn': '4444444444444',
            'total_copies': 2,
            'available_copies': 1
        }
        
        def mock_get_all_books():
            return [info_book]
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result_lower = svc.search_books_in_catalog('great', 'title')
        result_upper = svc.search_books_in_catalog('GREAT', 'title')
        result_mixed = svc.search_books_in_catalog('GrEaT', 'title')
        
        assert len(result_lower) > 0
        assert len(result_upper) > 0
        assert len(result_mixed) > 0


class TestSearchBooksEdgeCases:
    def test_search_books_empty_result(self, monkeypatch):
        """Test search with no matching results."""
        info_book = {
            'id': 1,
            'title': 'Python Book',
            'author': 'Author',
            'isbn': '1234567890123',
            'total_copies': 5,
            'available_copies': 3
        }
        
        def mock_get_all_books():
            return [info_book]
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Nonexistent', 'title')
        
        assert len(result) == 0

    def test_search_books_partial_match_title(self, monkeypatch):
        """Test partial matching on title."""
        info_book = {
            'id': 5,
            'title': 'Complete Python Guide',
            'author': 'John Doe',
            'isbn': '5555555555555',
            'total_copies': 3,
            'available_copies': 2
        }
        
        def mock_get_all_books():
            return [info_book]
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('omplete Py', 'title')
        
        assert len(result) > 0

    def test_search_books_partial_match_author(self, monkeypatch):
        """Test partial matching on author."""
        info_book = {
            'id': 6,
            'title': 'Database Design',
            'author': 'Jane Elizabeth Smith',
            'isbn': '6666666666666',
            'total_copies': 4,
            'available_copies': 2
        }
        
        def mock_get_all_books():
            return [info_book]
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Elizabeth', 'author')
        
        assert len(result) > 0

    def test_search_books_isbn_substring(self, monkeypatch):
        """Test ISBN substring matching."""
        info_book = {
            'id': 7,
            'title': 'Book Title',
            'author': 'Book Author',
            'isbn': '9999999999999',
            'total_copies': 2,
            'available_copies': 1
        }
        
        def mock_get_all_books():
            return [info_book]
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('99999999', 'isbn')
        
        assert len(result) > 0

    def test_search_books_empty_catalog(self, monkeypatch):
        """Test search on empty catalog."""
        def mock_get_all_books():
            return []
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Any Book', 'title')
        
        assert result == []


class TestSearchBooksInvalidInputs:
    def test_search_books_empty_search_term(self, monkeypatch):
        """Test search with empty search term."""
        def mock_get_all_books():
            return []
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('', 'title')
        
        # Should return empty or all books depending on implementation
        assert isinstance(result, list)

    def test_search_books_invalid_search_type(self, monkeypatch):
        """Test search with invalid search type."""
        def mock_get_all_books():
            return []
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('search term', 'invalid_type')
        
        assert isinstance(result, list)

    def test_search_books_special_characters_in_title(self, monkeypatch):
        """Test search with special characters."""
        info_book = {
            'id': 8,
            'title': 'C++ Secrets & Tips',
            'author': 'Developer',
            'isbn': '8888888888888',
            'total_copies': 3,
            'available_copies': 1
        }
        
        def mock_get_all_books():
            return [info_book]
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('C++', 'title')
        
        assert isinstance(result, list)