"""Lyrics service business logic."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from aimusic.models.entities import Lyrics as LyricsModel, Song as SongModel
from aimusic.schemas.lyrics import LyricsCreate, LyricsUpdate, LyricsResponse


class LyricsService:
    """Handle lyrics operations."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def create_lyrics(self, data: LyricsCreate) -> LyricsResponse:
        """Create lyrics for a song."""
        # Verify song exists
        song = self.db.query(SongModel).filter(SongModel.id == data.song_id).first()
        if not song:
            raise ValueError(f"Song {data.song_id} not found")

        lyrics = LyricsModel(
            song_id=data.song_id,
            line_number=data.line_number,
            section=data.section,
            text=data.text,
            mood=data.mood,
            language=data.language,
        )
        self.db.add(lyrics)
        self.db.commit()
        self.db.refresh(lyrics)
        return LyricsResponse.model_validate(lyrics)

    def get_lyrics(self, lyrics_id: int) -> Optional[LyricsResponse]:
        """Get lyrics by ID."""
        lyrics = self.db.query(LyricsModel).filter(LyricsModel.id == lyrics_id).first()
        if not lyrics:
            return None
        return LyricsResponse.model_validate(lyrics)

    def list_lyrics(
        self,
        song_id: int,
        section: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[LyricsResponse], int]:
        """List lyrics for song with optional filtering."""
        query = self.db.query(LyricsModel).filter(LyricsModel.song_id == song_id)

        if section:
            query = query.filter(LyricsModel.section == section)

        total = query.count()
        lyrics_list = query.order_by(LyricsModel.line_number).offset(skip).limit(limit).all()

        return (
            [LyricsResponse.model_validate(l) for l in lyrics_list],
            total,
        )

    def update_lyrics(self, lyrics_id: int, data: LyricsUpdate) -> Optional[LyricsResponse]:
        """Update lyrics."""
        lyrics = self.db.query(LyricsModel).filter(LyricsModel.id == lyrics_id).first()
        if not lyrics:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(lyrics, key, value)

        self.db.commit()
        self.db.refresh(lyrics)
        return LyricsResponse.model_validate(lyrics)

    def delete_lyrics(self, lyrics_id: int) -> bool:
        """Delete lyrics."""
        lyrics = self.db.query(LyricsModel).filter(LyricsModel.id == lyrics_id).first()
        if not lyrics:
            return False

        self.db.delete(lyrics)
        self.db.commit()
        return True
