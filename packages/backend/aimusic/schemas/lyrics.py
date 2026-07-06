"""Lyrics schemas for validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LyricsBase(BaseModel):
    """Base lyrics fields."""

    song_id: int
    line_number: int
    section: str = Field(..., pattern="^(verse|chorus|bridge|pre-chorus|outro|intro)$")
    text: str = Field(..., min_length=1, max_length=500)
    mood: Optional[str] = None
    language: str = "en"


class LyricsCreate(LyricsBase):
    """Schema for creating lyrics."""

    pass


class LyricsUpdate(BaseModel):
    """Schema for updating lyrics."""

    text: Optional[str] = None
    section: Optional[str] = None
    mood: Optional[str] = None


class LyricsResponse(LyricsBase):
    """Schema for lyrics responses."""

    id: int
    start_time_seconds: Optional[float] = None
    end_time_seconds: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LyricsListResponse(BaseModel):
    """List response for lyrics."""

    lyrics: list[LyricsResponse]
    total: int
    skip: int
    limit: int
