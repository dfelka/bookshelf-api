from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Meta(BaseModel):
    page: int
    per_page: int
    total: int


class DataResponse(BaseModel, Generic[T]):
    """Envelope for a single resource: {"data": {...}}."""

    data: T


class ListResponse(BaseModel, Generic[T]):
    """Envelope for a paginated collection: {"data": [...], "meta": {...}}."""

    data: list[T]
    meta: Meta


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error envelope: {"error": {"code": ..., "message": ...}}."""

    error: ErrorDetail
