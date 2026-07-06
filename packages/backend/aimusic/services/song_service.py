"""Song service business logic."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from aimusic.models.entities import Song as SongModel, Project as ProjectModel
from aimusic.schemas.song import SongCreate, SongUpdate, SongResponse


class SongService:
    """Handle song operations."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def create_song(self, data: SongCreate) -> SongResponse:
        """Create a new song."""
        # Verify project exists
        project = self.db.query(ProjectModel).filter(ProjectModel.id == data.project_id).first()
        if not project:
            raise ValueError(f"Project {data.project_id} not found")

        song = SongModel(
            project_id=data.project_id,
            name=data.name,
            position=data.position,
        )
        self.db.add(song)
        self.db.commit()
        self.db.refresh(song)
        return SongResponse.model_validate(song)

    def get_song(self, song_id: int) -> Optional[SongResponse]:
        """Get song by ID."""
        song = self.db.query(SongModel).filter(SongModel.id == song_id).first()
        if not song:
            return None
        return SongResponse.model_validate(song)

    def list_songs(
        self,
        project_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[SongResponse], int]:
        """List songs for project."""
        query = self.db.query(SongModel).filter(SongModel.project_id == project_id)
        total = query.count()
        songs = query.order_by(SongModel.position).offset(skip).limit(limit).all()

        return (
            [SongResponse.model_validate(s) for s in songs],
            total,
        )

    def update_song(
        self,
        song_id: int,
        data: SongUpdate,
    ) -> Optional[SongResponse]:
        """Update song."""
        song = self.db.query(SongModel).filter(SongModel.id == song_id).first()
        if not song:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(song, key, value)

        self.db.commit()
        self.db.refresh(song)
        return SongResponse.model_validate(song)

    def delete_song(self, song_id: int) -> bool:
        """Delete song."""
        song = self.db.query(SongModel).filter(SongModel.id == song_id).first()
        if not song:
            return False

        self.db.delete(song)
        self.db.commit()
        return True
