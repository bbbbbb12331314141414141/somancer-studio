"""Project schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project fields."""

    name: str = Field(..., min_length=1, max_length=255)
    project_type: str = Field(default="single", pattern="^(album|ep|single|demo)$")
    description: Optional[str] = None
    genre: Optional[str] = Field(None, max_length=100)
    artist_name: str = Field(default="Unknown", max_length=255)
    bpm: Optional[int] = Field(None, ge=30, le=300)
    key: Optional[str] = Field(None, max_length=10)


class ProjectCreate(ProjectBase):
    """Schema for creating projects."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating projects (all fields optional)."""

    name: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    artist_name: Optional[str] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    archived: Optional[bool] = None


class ProjectResponse(ProjectBase):
    """Schema for project responses."""

    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    archived: bool

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """List response for projects."""

    projects: list[ProjectResponse]
    total: int
    skip: int
    limit: int
