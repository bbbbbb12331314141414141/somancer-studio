"""Genre schemas for validation."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GenreBase(BaseModel):
    """Base genre fields."""

    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[int] = None
    description: Optional[str] = None
    bpm_min: Optional[int] = Field(None, ge=30, le=300)
    bpm_max: Optional[int] = Field(None, ge=30, le=300)


class GenreCreate(GenreBase):
    """Schema for creating genres."""

    common_keys: Optional[list[str]] = None
    common_instruments: Optional[list[str]] = None
    production_techniques: Optional[list[str]] = None
    vocal_style: Optional[str] = None


class GenreUpdate(BaseModel):
    """Schema for updating genres."""

    name: Optional[str] = None
    description: Optional[str] = None
    bpm_min: Optional[int] = None
    bpm_max: Optional[int] = None


class GenreResponse(GenreBase):
    """Schema for genre responses."""

    id: int
    common_keys: list[str]
    common_instruments: list[str]
    production_techniques: list[str]
    vocal_style: Optional[str]
    sources: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenreListResponse(BaseModel):
    """List response for genres."""

    genres: list[GenreResponse]
    total: int
    skip: int
    limit: int
