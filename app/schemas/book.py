from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str | None = Field(default=None, max_length=200)
    description: str | None = None
    is_done: bool = False


class BookCreate(BookBase):
    """Payload for creating a book (title required)."""


class BookUpdate(BaseModel):
    """Payload for a partial update (PATCH); every field is optional."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, max_length=200)
    description: str | None = None
    is_done: bool | None = None


class BookRead(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
