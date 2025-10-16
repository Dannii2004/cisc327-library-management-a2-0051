import pytest
import library_service as svc


class TestSearchBooksComprehensive:
    def test_search_title_case_insensitive_lower(self, monkeypatch):
        """Test title search is case-insensitive with lowercase input."""
        books = [
            {
                'id': 1,
                'title': 'THE PYTHON GUIDE',
                'author': 'John Smith',
                'isbn': '1111111111111',
                'total_copies': 5,
                'available_copies': 3
            }
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('python', 'title')
        
        assert len(result) > 0
        assert result[0]['id'] == 1

    def test_search_title_case_insensitive_upper(self, monkeypatch):
        """Test title search is case-insensitive with uppercase input."""
        books = [
            {
                'id': 2,
                'title': 'the python guide',
                'author': 'John Smith',
                'isbn': '2222222222222',
                'total_copies': 5,
                'available_copies': 3
            }
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('PYTHON', 'title')
        
        assert len(result) > 0

    def test_search_author_partial_match(self, monkeypatch):
        """Test author search with partial match."""
        books = [
            {
                'id': 3,
                'title': 'Book Title',
                'author': 'Christopher Alexander Pattern',
                'isbn': '3333333333333',
                'total_copies': 3,
                'available_copies': 1
            }
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Alexander', 'author')
        
        assert len(result) > 0

    def test_search_isbn_exact_substring(self, monkeypatch):
        """Test ISBN search finds exact substring."""
        books = [
            {
                'id': 4,
                'title': 'ISBN Book',
                'author': 'Author Name',
                'isbn': '9876543210987',
                'total_copies': 2,
                'available_copies': 2
            }
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('987654321', 'isbn')
        
        assert len(result) > 0
        assert result[0]['isbn'] == '9876543210987'

    def test_search_filters_out_non_matching(self, monkeypatch):
        """Test search filters out non-matching books."""
        books = [
            {
                'id': 5,
                'title': 'Python Programming',
                'author': 'Author One',
                'isbn': '1111111111111',
                'total_copies': 5,
                'available_copies': 3
            },
            {
                'id': 6,
                'title': 'Java Programming',
                'author': 'Author Two',
                'isbn': '2222222222222',
                'total_copies': 4,
                'available_copies': 2
            }
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Python', 'title')
        
        assert len(result) == 1
        assert result[0]['id'] == 5

    def test_search_returns_list_of_dicts(self, monkeypatch):
        """Test search returns list of book dictionaries."""
        books = [
            {
                'id': 7,
                'title': 'Test Book',
                'author': 'Test Author',
                'isbn': '3333333333333',
                'total_copies': 5,
                'available_copies': 3
            }
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Test', 'title')
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], dict)
        assert 'id' in result[0]
        assert 'title' in result[0]

    def test_search_multiple_matches_all_returned(self, monkeypatch):
        """Test all matching books are returned."""
        books = [
            {'id': 8, 'title': 'Design Patterns', 'author': 'Gang of Four', 'isbn': '4444444444444', 'total_copies': 3, 'available_copies': 1},
            {'id': 9, 'title': 'Design Principles', 'author': 'Robert Martin', 'isbn': '5555555555555', 'total_copies': 2, 'available_copies': 2},
            {'id': 10, 'title': 'Advanced Python', 'author': 'Guido', 'isbn': '6666666666666', 'total_copies': 4, 'available_copies': 3}
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Design', 'title')
        
        assert len(result) == 2
        assert any(book['id'] == 8 for book in result)
        assert any(book['id'] == 9 for book in result)

    def test_search_empty_catalog_returns_empty_list(self, monkeypatch):
        """Test search on empty catalog returns empty list."""
        def mock_get_all_books():
            return []
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Any Search Term', 'title')
        
        assert result == []

    def test_search_no_results_returns_empty_list(self, monkeypatch):
        """Test search with no matches returns empty list."""
        books = [
            {'id': 11, 'title': 'Java Book', 'author': 'Java Author', 'isbn': '7777777777777', 'total_copies': 5, 'available_copies': 2}
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Python', 'title')
        
        assert result == []

    def test_search_whitespace_handling(self, monkeypatch):
        """Test search with leading/trailing spaces."""
        books = [
            {'id': 12, 'title': 'Book with Spaces', 'author': 'Author', 'isbn': '8888888888888', 'total_copies': 3, 'available_copies': 1}
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Spaces', 'title')
        
        assert len(result) > 0

    def test_search_single_character_title(self, monkeypatch):
        """Test search with single character match."""
        books = [
            {'id': 13, 'title': 'A Book', 'author': 'Author', 'isbn': '9999999999999', 'total_copies': 1, 'available_copies': 1}
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('A', 'title')
        
        assert len(result) > 0

    def test_search_numbers_in_title(self, monkeypatch):
        """Test search for numbers in title."""
        books = [
            {'id': 14, 'title': 'Python 3.9 Guide', 'author': 'Author', 'isbn': '1010101010101', 'total_copies': 2, 'available_copies': 1}
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('3.9', 'title')
        
        assert len(result) > 0

    def test_search_special_characters_in_author(self, monkeypatch):
        """Test search for author with special characters."""
        books = [
            {'id': 15, 'title': 'Book', 'author': "O'Brien Smith", 'isbn': '1111010101010', 'total_copies': 3, 'available_copies': 2}
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog("Brien", 'author')
        
        assert len(result) > 0

    def test_search_isbn_all_zeros(self, monkeypatch):
        """Test search for ISBN with repeated digits."""
        books = [
            {'id': 16, 'title': 'Book', 'author': 'Author', 'isbn': '0000000000000', 'total_copies': 1, 'available_copies': 1}
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('0000', 'isbn')
        
        assert len(result) > 0

    def test_search_preserves_book_data_in_results(self, monkeypatch):
        """Test that search results contain complete book data."""
        books = [
            {
                'id': 17,
                'title': 'Complete Data Book',
                'author': 'Data Author',
                'isbn': '1111111110101',
                'total_copies': 10,
                'available_copies': 5
            }
        ]
        
        def mock_get_all_books():
            return books
        
        monkeypatch.setattr(svc, 'get_all_books', mock_get_all_books)
        
        result = svc.search_books_in_catalog('Complete', 'title')
        
        assert result[0]['id'] == 17
        assert result[0]['title'] == 'Complete Data Book'
        assert result[0]['author'] == 'Data Author'
        assert result[0]['isbn'] == '1111111110101'
        assert result[0]['total_copies'] == 10
        assert result[0]['available_copies'] == 5