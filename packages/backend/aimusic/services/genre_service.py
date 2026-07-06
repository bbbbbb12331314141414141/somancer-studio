"""Genre service business logic."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from aimusic.models.entities import Genre as GenreModel
from aimusic.schemas.genre import GenreCreate, GenreUpdate, GenreResponse


class GenreService:
    """Handle genre operations."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def create_genre(self, data: GenreCreate) -> GenreResponse:
        """Create a new genre."""
        genre = GenreModel(
            name=data.name,
            parent_id=data.parent_id,
            description=data.description,
            bpm_min=data.bpm_min,
            bpm_max=data.bpm_max,
            common_keys=data.common_keys or [],
            common_instruments=data.common_instruments or [],
            production_techniques=data.production_techniques or [],
            vocal_style=data.vocal_style,
        )
        self.db.add(genre)
        self.db.commit()
        self.db.refresh(genre)
        return GenreResponse.model_validate(genre)

    def get_genre(self, genre_id: int) -> Optional[GenreResponse]:
        """Get genre by ID."""
        genre = self.db.query(GenreModel).filter(GenreModel.id == genre_id).first()
        if not genre:
            return None
        return GenreResponse.model_validate(genre)

    def list_genres(
        self,
        parent_id: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[GenreResponse], int]:
        """List genres with optional filtering."""
        query = self.db.query(GenreModel)

        if parent_id is not None:
            query = query.filter(GenreModel.parent_id == parent_id)

        if search:
            query = query.filter(
                or_(
                    GenreModel.name.ilike(f"%{search}%"),
                    GenreModel.description.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        genres = query.order_by(GenreModel.name).offset(skip).limit(limit).all()

        return (
            [GenreResponse.model_validate(g) for g in genres],
            total,
        )

    def update_genre(self, genre_id: int, data: GenreUpdate) -> Optional[GenreResponse]:
        """Update genre."""
        genre = self.db.query(GenreModel).filter(GenreModel.id == genre_id).first()
        if not genre:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(genre, key, value)

        self.db.commit()
        self.db.refresh(genre)
        return GenreResponse.model_validate(genre)

    def delete_genre(self, genre_id: int) -> bool:
        """Delete genre."""
        genre = self.db.query(GenreModel).filter(GenreModel.id == genre_id).first()
        if not genre:
            return False

        self.db.delete(genre)
        self.db.commit()
        return True

    def get_subgenres(self, parent_id: int) -> list[GenreResponse]:
        """Get all subgenres for a parent genre."""
        genres = self.db.query(GenreModel).filter(GenreModel.parent_id == parent_id).all()
        return [GenreResponse.model_validate(g) for g in genres]
