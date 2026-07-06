"""
Database models for Sonmancer Studio.

Tables:
- Projects: Top-level album/EP/single projects
- Songs: Individual songs within a project
- Tracks: Audio/MIDI tracks within a song
- Lyrics: Lyric lines with timing and metadata
- Genres: Reference genre database
- Plugins: Installed plugins metadata
- Settings: User and system settings
- AIModels: Available AI models (local + remote)
- Jobs: Background tasks (rendering, exporting)
- Exports: Export history and metadata
- History: Undo/redo history
- AIConversations: Chat history with AI agents
"""

from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import (
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class ProjectType(str, PyEnum):
    ALBUM = "album"
    EP = "ep"
    SINGLE = "single"
    DEMO = "demo"


class TrackType(str, PyEnum):
    AUDIO = "audio"
    MIDI = "midi"
    SYNTH = "synth"


class JobStatus(str, PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    project_type: Mapped[ProjectType] = mapped_column(
        Enum(ProjectType), default=ProjectType.SINGLE
    )
    genre: Mapped[Optional[str]] = mapped_column(String(100))
    artist_name: Mapped[str] = mapped_column(String(255), default="Unknown")
    bpm: Mapped[Optional[int]] = mapped_column(Integer)
    key: Mapped[Optional[str]] = mapped_column(String(10))  # e.g., "C Major", "Am"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    cover_art_path: Mapped[Optional[str]] = mapped_column(String(512))
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    songs: Mapped[list["Song"]] = relationship("Song", back_populates="project")
    exports: Mapped[list["Export"]] = relationship("Export", back_populates="project")


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=1)  # Track order in album
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="songs")
    tracks: Mapped[list["Track"]] = relationship("Track", back_populates="song")
    lyrics: Mapped[list["Lyrics"]] = relationship("Lyrics", back_populates="song")
    ai_conversations: Mapped[list["AIConversation"]] = relationship(
        "AIConversation", back_populates="song"
    )


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    track_type: Mapped[TrackType] = mapped_column(
        Enum(TrackType), default=TrackType.AUDIO
    )
    instrument: Mapped[Optional[str]] = mapped_column(
        String(100)
    )  # e.g., "Piano", "Violin", "Synth Lead"
    position: Mapped[int] = mapped_column(Integer, default=0)  # Layering order
    volume: Mapped[float] = mapped_column(Float, default=1.0)  # 0.0 - 2.0
    pan: Mapped[float] = mapped_column(Float, default=0.0)  # -1.0 (left) to 1.0 (right)
    muted: Mapped[bool] = mapped_column(Boolean, default=False)
    solo: Mapped[bool] = mapped_column(Boolean, default=False)
    audio_path: Mapped[Optional[str]] = mapped_column(String(512))
    midi_path: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    song: Mapped["Song"] = relationship("Song", back_populates="tracks")


class Lyrics(Base):
    __tablename__ = "lyrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer)
    section: Mapped[str] = mapped_column(String(50))  # "verse", "chorus", "bridge"
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_time_seconds: Mapped[Optional[float]] = mapped_column(Float)
    end_time_seconds: Mapped[Optional[float]] = mapped_column(Float)
    mood: Mapped[Optional[str]] = mapped_column(String(100))
    language: Mapped[str] = mapped_column(String(10), default="en")
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    song: Mapped["Song"] = relationship("Song", back_populates="lyrics")


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("genres.id"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    bpm_min: Mapped[Optional[int]] = mapped_column(Integer)
    bpm_max: Mapped[Optional[int]] = mapped_column(Integer)
    common_keys: Mapped[list] = mapped_column(JSON, default=list)  # ["C Major", "Am"]
    common_instruments: Mapped[list] = mapped_column(JSON, default=list)
    typical_chord_progressions: Mapped[list] = mapped_column(JSON, default=list)
    production_techniques: Mapped[list] = mapped_column(JSON, default=list)
    vocal_style: Mapped[Optional[str]] = mapped_column(String(200))
    sources: Mapped[list] = mapped_column(JSON, default=list)  # Citation sources
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)


class Plugin(Base):
    __tablename__ = "plugins"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20))
    plugin_type: Mapped[str] = mapped_column(String(50))  # "effect", "generator", "theme"
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    path: Mapped[str] = mapped_column(String(512))
    manifest: Mapped[dict] = mapped_column(JSON)  # Plugin metadata
    installed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text)
    value_type: Mapped[str] = mapped_column(String(20))  # "string", "int", "float", "bool"
    category: Mapped[str] = mapped_column(String(100))  # "audio", "ui", "gpu", "models"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AIModel(Base):
    __tablename__ = "ai_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_type: Mapped[str] = mapped_column(
        String(50)
    )  # "text", "music", "voice", "image"
    provider: Mapped[str] = mapped_column(String(100))  # "ollama", "anthropic", "openai"
    model_id: Mapped[str] = mapped_column(String(255))  # ollama ID, API model name, etc.
    version: Mapped[str] = mapped_column(String(20))
    local: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    size_gb: Mapped[Optional[float]] = mapped_column(Float)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    downloaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    song_id: Mapped[Optional[int]] = mapped_column(ForeignKey("songs.id"))
    job_type: Mapped[str] = mapped_column(String(100))  # "render", "export", "mix"
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 - 1.0
    result_path: Mapped[Optional[str]] = mapped_column(String(512))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)


class Export(Base):
    __tablename__ = "exports"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    format: Mapped[str] = mapped_column(String(20))  # "wav", "mp3", "flac", "ogg"
    quality: Mapped[Optional[str]] = mapped_column(String(50))  # "hq", "standard", "low"
    file_path: Mapped[str] = mapped_column(String(512))
    file_size_mb: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    exported_by: Mapped[Optional[str]] = mapped_column(String(100))  # user agent
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="exports")


class History(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(100))  # "track_added", "lyrics_modified", etc.
    before_state: Mapped[dict] = mapped_column(JSON)  # Serialized state before action
    after_state: Mapped[dict] = mapped_column(JSON)  # Serialized state after action
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    song_id: Mapped[Optional[int]] = mapped_column(ForeignKey("songs.id"))
    agent_name: Mapped[str] = mapped_column(
        String(50)
    )  # "producer", "songwriter", "composer", etc.
    context: Mapped[Optional[str]] = mapped_column(String(100))  # what was being discussed
    messages: Mapped[list] = mapped_column(JSON)  # List of {role: "user"|"assistant", content: str}
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    song: Mapped[Optional["Song"]] = relationship("Song", back_populates="ai_conversations")
