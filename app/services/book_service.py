from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


def list_books(
    db: Session,
    *,
    page: int = 1,
    per_page: int = 20,
    author: str | None = None,
    q: str | None = None,
    is_done: bool | None = None,
) -> tuple[list[Book], int]:
    """Return a page of books plus the total count matching the filters."""
    filters = []
    if author:
        filters.append(Book.author.ilike(f"%{author}%"))
    if q:
        filters.append(Book.title.ilike(f"%{q}%"))
    if is_done is not None:
        filters.append(Book.is_done.is_(is_done))

    total = db.scalar(select(func.count()).select_from(Book).where(*filters)) or 0

    stmt = (
        select(Book)
        .where(*filters)
        .order_by(Book.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    books = list(db.scalars(stmt).all())
    return books, total


def get_book(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise NotFoundError(f"Book with id {book_id} not found")
    return book


def create_book(db: Session, payload: BookCreate) -> Book:
    book = Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(db: Session, book_id: int, payload: BookUpdate) -> Book:
    book = get_book(db, book_id)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    book = get_book(db, book_id)
    db.delete(book)
    db.commit()
