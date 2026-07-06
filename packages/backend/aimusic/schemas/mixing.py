"""Mixing and mastering schemas."""

from typing import Optional
from pydantic import BaseModel, Field


# ── Mix Engineer ──────────────────────────────────────────────────────────────

class TrackInput(BaseModel):
    name: str
    instrument: str
    channel: Optional[int] = None


class MixPlanRequest(BaseModel):
    genre: str
    mood: str
    tracks: list[TrackInput]
    reference_style: Optional[str] = None
    model: str = "mistral"


class EQBandSchema(BaseModel):
    frequency: float
    gain_db: float
    q: float
    filter_type: str


class CompressorSchema(BaseModel):
    threshold_db: float
    ratio: float
    attack_ms: float
    release_ms: float
    makeup_gain_db: float
    knee_db: float = 6.0


class TrackMixPlanSchema(BaseModel):
    track_name: str
    instrument: str
    volume_db: float
    pan: float
    eq_bands: list[EQBandSchema]
    compressor: Optional[CompressorSchema] = None
    reverb_send: float
    delay_send: float
    notes: str


class MixPlanResponse(BaseModel):
    master_buss_eq: list[EQBandSchema]
    tracks: list[TrackMixPlanSchema]
    mix_notes: str
    genre: str
    mood: str
    agent: str = "mix_engineer"
    model: str


class StereoPlanRequest(BaseModel):
    tracks: list[str]
    genre: str
    model: str = "mistral"


# ── Mastering Engineer ────────────────────────────────────────────────────────

class MasteringChainRequest(BaseModel):
    genre: str
    mood: str
    platform: str = Field("spotify", description="Target streaming platform")
    dynamic_range: str = Field("medium", pattern="^(compressed|medium|dynamic)$")
    notes: Optional[str] = None
    model: str = "mistral"


class MasteringBandSchema(BaseModel):
    stage: str
    enabled: bool
    parameters: dict


class MasteringChainResponse(BaseModel):
    target_platform: str
    target_lufs: float
    target_peak_db: float
    stages: list[MasteringBandSchema]
    notes: str
    expected_character: str
    agent: str = "mastering_engineer"
    model: str


class MasterReviewRequest(BaseModel):
    genre: str
    measured_lufs: float
    measured_peak_db: float
    platform: str = "spotify"
    model: str = "mistral"


# ── Stem Export ───────────────────────────────────────────────────────────────

class StemExportRequest(BaseModel):
    composition: dict           # CompositionResponse JSON
    soundfont_path: Optional[str] = None
    sample_rate: int = 48_000
    normalize: bool = True
    song_name: str = "composition"


class StemExportResponse(BaseModel):
    full_mix_path: str
    stems: dict[str, str]       # stem_name → wav_path
    duration_seconds: float
    sample_rate: int
    stem_count: int
    download_urls: dict[str, str]


# ── Vocal Synthesis ───────────────────────────────────────────────────────────

class VocalSynthesisRequest(BaseModel):
    song_id: Optional[int] = None
    lyrics: list[dict]          # [{text, section}, ...]
    bpm: float = 120.0
    engine: str = "tts_stub"


class VocalEngineInfo(BaseModel):
    name: str
    label: str
    available: bool
    quality: str
    note: str


class VocalSynthesisResponse(BaseModel):
    audio_path: str
    duration_seconds: float
    sample_rate: int
    lines_rendered: int
    engine: str
    download_url: str
