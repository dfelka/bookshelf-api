from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.schemas.common import DataResponse, ListResponse, Meta
from app.services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=ListResponse[BookRead])
def list_books(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    author: str | None = Query(None, description="Filter by author (partial match)"),
    q: str | None = Query(None, description="Search in title (partial match)"),
    db: Session = Depends(get_db),
) -> ListResponse[BookRead]:
    books, total = book_service.list_books(
        db, page=page, per_page=per_page, author=author, q=q
    )
    return ListResponse[BookRead](
        data=[BookRead.model_validate(b) for b in books],
        meta=Meta(page=page, per_page=per_page, total=total),
    )


@router.get("/{book_id}", response_model=DataResponse[BookRead])
def get_book(
    book_id: int, db: Session = Depends(get_db)
) -> DataResponse[BookRead]:
    book = book_service.get_book(db, book_id)
    return DataResponse[BookRead](data=BookRead.model_validate(book))


@router.post(
    "",
    response_model=DataResponse[BookRead],
    status_code=status.HTTP_201_CREATED,
)
def create_book(
    payload: BookCreate, db: Session = Depends(get_db)
) -> DataResponse[BookRead]:
    book = book_service.create_book(db, payload)
    return DataResponse[BookRead](data=BookRead.model_validate(book))


@router.patch("/{book_id}", response_model=DataResponse[BookRead])
def update_book(
    book_id: int, payload: BookUpdate, db: Session = Depends(get_db)
) -> DataResponse[BookRead]:
    book = book_service.update_book(db, book_id, payload)
    return DataResponse[BookRead](data=BookRead.model_validate(book))


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)) -> Response:
    book_service.delete_book(db, book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
