"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books
)
def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    if not title or not title.strip():
        return False, "Title is required."
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    if not author or not author.strip():
        return False, "Author is required."
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    if len(isbn) != 13 or not isbn.isdigit():
        return False, "ISBN must be exactly 13 digits."
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."

    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."

    ins = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if isinstance(ins, tuple):
        ins_ok = bool(ins[0])
    else:
        ins_ok = bool(ins)

    if ins_ok:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."





def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'







def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:

    """
    Process book return by a patron.

    """
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "The patron ID entered is invalid - 6 digits only."

    book = get_book_by_id(book_id)
    if not book:
        return False, "This book cannot be located."

    ret_upd = update_borrow_record_return_date(patron_id, book_id, datetime.now())
    if not ret_upd:
        return False, "No active borrow record."

    copy_upd = update_book_availability(book_id, +1)
    if not copy_upd:
        return False, "Failed to update book availability."

    return True, f'Book "{book["title"]}" has been returned.'





































def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    info_book = get_book_by_id(book_id)
    if not info_book:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'The provided book information has not been found'}

    import database
    get_borrow_record = getattr(database, "get_borrow_record", None)
    info_loan = get_borrow_record(patron_id, book_id) if callable(get_borrow_record) else None

    if not info_loan or info_loan.get("due_date") is None:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'The borrow record has not been located'}

    past_due = info_loan["due_date"]
    date_now = datetime.now()
    days_past_due = max((date_now - past_due).days, 0)
    daily_fine = 0.25
    total_fine = round(days_past_due * daily_fine, 2)

    return {
        'fee_amount': total_fine,
        'days_overdue': days_past_due,
        'status': 'Your late fee has been calculated' if days_past_due > 0 else 'No overdue charge'
    }

















def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    """
    search_input = search_term.strip().lower()
    match_results = []

    for info_book in get_all_books():
        if search_type == "title" and search_input in info_book["title"].lower():
            match_results.append(info_book)
        elif search_type == "author" and search_input in info_book["author"].lower():
            match_results.append(info_book)
        elif search_type == "isbn" and search_input in info_book["isbn"]:
            match_results.append(info_book)

    return match_results





def get_patron_status_report(patron_id: str) -> Dict:
    import database
    get_borrow_records_by_patron = getattr(database, "get_borrow_records_by_patron", None)
    info_loans = get_borrow_records_by_patron(patron_id) if callable(get_borrow_records_by_patron) else []

    """
    Get status report for a patron.
    """

    borrowd_summ = []
    fee_total = 0.0

    for info_loan in info_loans:
        past_due = info_loan["due_date"]
        returned_date = info_loan.get("return_date")
        date_now = datetime.now()

        if returned_date:
            days_break = (returned_date - past_due).days
        else:
            days_break = (date_now - past_due).days

        days_past_due = max(days_break, 0)
        daily_fine = 0.25
        total_fine = round(days_past_due * daily_fine, 2)
        fee_total += total_fine

        borrowd_summ.append({
            "book_title": info_loan["title"],
            "isbn": info_loan["isbn"],
            "due_date": past_due.strftime("%Y-%m-%d"),
            "returned": bool(returned_date),
            "days_late": days_past_due,
            "fee": total_fine,
        })

    return {
        "patron_id": patron_id,
        "borrowed_books": borrowd_summ,
        "total_late_fees": fee_total
    }


#git test stuff
def get_borrow_records_by_patron(patron_id: str):
    """Temporary placeholder for CI tests."""
    return []
