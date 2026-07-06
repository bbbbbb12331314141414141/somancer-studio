"""AI endpoint schemas."""

from typing import Optional
from pydantic import BaseModel, Field


# ── Lyrics generation ────────────────────────────────────────────────────────

class LyricsGenerationRequest(BaseModel):
    song_id: Optional[int] = None
    section: str = Field("verse", pattern="^(verse|chorus|bridge|pre-chorus|outro|intro)$")
    count: int = Field(4, ge=1, le=16)
    genre: Optional[str] = None
    mood: Optional[str] = None
    theme: Optional[str] = None
    vocabulary: str = "poetic"
    perspective: str = "first_person"
    language: str = "en"
    length: str = Field("medium", pattern="^(short|medium|long)$")
    rhyme: bool = True
    existing_lyrics: Optional[str] = None
    model: str = "mistral"


class GeneratedLyricLine(BaseModel):
    line_number: int
    section: str
    text: str
    mood: Optional[str] = None
    rhyme_scheme: Optional[str] = None


class LyricsGenerationResponse(BaseModel):
    lines: list[GeneratedLyricLine]
    agent: str = "songwriter"
    model: str
    song_id: Optional[int] = None


# ── Composition ──────────────────────────────────────────────────────────────

class CompositionRequest(BaseModel):
    song_id: Optional[int] = None
    genre: str = "pop"
    mood: str = "happy"
    key: str = "C Major"
    bpm: int = Field(120, ge=30, le=300)
    bars: int = Field(8, ge=1, le=64)
    instruments: list[str] = ["piano", "bass", "drums"]
    complexity: str = Field("medium", pattern="^(simple|medium|complex)$")
    model: str = "mistral"


class MidiNoteSchema(BaseModel):
    pitch: int
    start: float
    duration: float
    velocity: int


class MidiTrackSchema(BaseModel):
    name: str
    channel: int
    instrument: int
    notes: list[MidiNoteSchema]


class CompositionResponse(BaseModel):
    tempo: int
    time_signature_numerator: int
    time_signature_denominator: int
    key: str
    tracks: list[MidiTrackSchema]
    chord_progression: list[str]
    structure: list[str]
    agent: str = "composer"
    model: str
    song_id: Optional[int] = None


# ── Song brief ───────────────────────────────────────────────────────────────

class SongBriefRequest(BaseModel):
    genre: str
    mood: Optional[str] = None
    theme: Optional[str] = None
    target_audience: Optional[str] = None
    duration_seconds: int = Field(210, ge=30, le=600)
    model: str = "mistral"


class SongBriefResponse(BaseModel):
    title: str
    genre: str
    mood: str
    theme: str
    bpm: int
    key: str
    duration_seconds: int
    structure: list[str]
    instruments: list[str]
    production_notes: str
    lyric_style: str
    agent: str = "producer"
    model: str


# ── Models ───────────────────────────────────────────────────────────────────

class OllamaModelInfo(BaseModel):
    name: str
    size: Optional[int] = None
    modified_at: Optional[str] = None


class ModelsResponse(BaseModel):
    models: list[OllamaModelInfo]
    available: bool
    host: str
