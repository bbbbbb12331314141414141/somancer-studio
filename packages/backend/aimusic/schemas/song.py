"""Song schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SongBase(BaseModel):
    """Base song fields."""

    name: str = Field(..., min_length=1, max_length=255)
    position: int = Field(default=1, ge=1)


class SongCreate(SongBase):
    """Schema for creating songs."""

    project_id: int


class SongUpdate(BaseModel):
    """Schema for updating songs."""

    name: Optional[str] = None
    position: Optional[int] = None


class SongResponse(SongBase):
    """Schema for song responses."""

    id: int
    project_id: int
    duration_seconds: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SongListResponse(BaseModel):
    """List response for songs."""

    songs: list[SongResponse]
    total: int
    skip: int
    limit: int
