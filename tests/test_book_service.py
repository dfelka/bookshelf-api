"""Unit tests for the book service layer.

Error paths use a mocked Session (no DB required). Behavioural tests run
against the in-memory SQLite session from conftest, exercising the real
SQLAlchemy query/filter logic without touching Postgres.
"""

from unittest.mock import MagicMock

import pytest

from app.errors import NotFoundError
from app.schemas.book import BookCreate, BookUpdate
from app.services import book_service

# --------------------------------------------------------------------------- #
# Error paths — mocked session                                                #
# --------------------------------------------------------------------------- #


def test_get_book_raises_not_found_for_missing_id() -> None:
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError) as exc:
        book_service.get_book(db, 99)

    assert "99" in str(exc.value)
    db.get.assert_called_once()


def test_update_book_raises_not_found_for_missing_id() -> None:
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        book_service.update_book(db, 99, BookUpdate(title="x"))

    db.commit.assert_not_called()


def test_delete_book_raises_not_found_for_missing_id() -> None:
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        book_service.delete_book(db, 99)

    db.delete.assert_not_called()


# --------------------------------------------------------------------------- #
# Behaviour — real in-memory session                                          #
# --------------------------------------------------------------------------- #


def test_create_book_persists_and_generates_id(db_session) -> None:
    book = book_service.create_book(
        db_session, BookCreate(title="Dune", author="Herbert")
    )

    assert book.id is not None
    assert book.title == "Dune"
    assert book.author == "Herbert"
    assert book.is_done is False
    assert book.created_at is not None


def test_get_book_returns_existing(db_session) -> None:
    created = book_service.create_book(db_session, BookCreate(title="1984"))

    fetched = book_service.get_book(db_session, created.id)

    assert fetched.id == created.id
    assert fetched.title == "1984"


def test_update_book_only_changes_sent_fields(db_session) -> None:
    created = book_service.create_book(
        db_session, BookCreate(title="Original", author="Author")
    )

    updated = book_service.update_book(db_session, created.id, BookUpdate(is_done=True))

    assert updated.is_done is True
    assert updated.title == "Original"  # untouched
    assert updated.author == "Author"  # untouched


def test_delete_book_removes_it(db_session) -> None:
    created = book_service.create_book(db_session, BookCreate(title="Gone"))

    book_service.delete_book(db_session, created.id)

    with pytest.raises(NotFoundError):
        book_service.get_book(db_session, created.id)


def test_list_books_paginates(db_session) -> None:
    for i in range(1, 6):
        book_service.create_book(db_session, BookCreate(title=f"Book {i}"))

    page1, total = book_service.list_books(db_session, page=1, per_page=2)
    page2, _ = book_service.list_books(db_session, page=2, per_page=2)

    assert total == 5
    assert [b.title for b in page1] == ["Book 1", "Book 2"]
    assert [b.title for b in page2] == ["Book 3", "Book 4"]


def test_list_books_filters_by_author(db_session) -> None:
    book_service.create_book(db_session, BookCreate(title="A", author="Tolkien"))
    book_service.create_book(db_session, BookCreate(title="B", author="Herbert"))

    books, total = book_service.list_books(db_session, author="tolk")

    assert total == 1
    assert books[0].author == "Tolkien"


def test_list_books_searches_title_with_q(db_session) -> None:
    book_service.create_book(db_session, BookCreate(title="The Hobbit"))
    book_service.create_book(db_session, BookCreate(title="Foundation"))

    books, total = book_service.list_books(db_session, q="hobbit")

    assert total == 1
    assert books[0].title == "The Hobbit"


def test_list_books_filters_by_is_done(db_session) -> None:
    book_service.create_book(db_session, BookCreate(title="Read", is_done=True))
    book_service.create_book(db_session, BookCreate(title="Unread", is_done=False))

    done, done_total = book_service.list_books(db_session, is_done=True)
    unread, unread_total = book_service.list_books(db_session, is_done=False)

    assert done_total == 1 and done[0].title == "Read"
    assert unread_total == 1 and unread[0].title == "Unread"
