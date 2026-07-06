"""Audio and rendering schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    """Request to render a song to audio."""
    song_id: int
    soundfont_path: Optional[str] = None
    sample_rate: int = Field(48_000, ge=8_000, le=192_000)
    normalize: bool = True
    peak_db: float = Field(-1.0, ge=-20.0, le=0.0)
    format: str = Field("wav", pattern="^(wav|flac|mp3)$")


class MidiRenderRequest(BaseModel):
    """Render MIDI data (from CompositionResponse) directly to audio."""
    composition: dict           # CompositionResponse JSON
    soundfont_path: Optional[str] = None
    sample_rate: int = 48_000
    normalize: bool = True


class WaveformRequest(BaseModel):
    """Request waveform data for visualisation."""
    song_id: int
    num_points: int = Field(1000, ge=100, le=5000)


class WaveformResponse(BaseModel):
    """Waveform data for visualisation."""
    peaks: list[float]
    rms: list[float]
    duration_seconds: float
    sample_rate: int


class TrackMixSettingsSchema(BaseModel):
    """Per-track mixing parameters."""
    volume: float = Field(1.0, ge=0.0, le=2.0)
    pan: float = Field(0.0, ge=-1.0, le=1.0)
    muted: bool = False
    solo: bool = False
    reverb: float = Field(0.0, ge=0.0, le=1.0)
    chorus: float = Field(0.0, ge=0.0, le=1.0)


class RenderJobResponse(BaseModel):
    """Response when a render job is queued."""
    job_id: str
    song_id: int
    status: str = "pending"
    estimated_seconds: Optional[int] = None


class RenderResultResponse(BaseModel):
    """Result of a completed render."""
    wav_path: str
    duration_seconds: float
    sample_rate: int
    peak_db: float
    track_count: int
    download_url: str
