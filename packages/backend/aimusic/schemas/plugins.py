"""Plugin and harmony schemas."""

from typing import Optional
from pydantic import BaseModel, Field


# ── Plugin Management ─────────────────────────────────────────────────────────

class PluginManifestSchema(BaseModel):
    id: str
    name: str
    version: str
    plugin_type: str
    author: str
    description: str
    entry_point: Optional[str] = None
    api_version: str = "1.0"
    tags: list[str] = []
    permissions: list[str] = []


class LoadedPluginSchema(BaseModel):
    manifest: PluginManifestSchema
    directory: str
    loaded: bool
    error: Optional[str] = None


class PluginListResponse(BaseModel):
    plugins: list[LoadedPluginSchema]
    total: int
    plugin_type: Optional[str] = None


class PluginInstallRequest(BaseModel):
    plugin_id: str


class ExamplePluginResponse(BaseModel):
    directory: str
    files_created: list[str]
    message: str


# ── Vocal Harmony ─────────────────────────────────────────────────────────────

class HarmonyNoteSchema(BaseModel):
    pitch: int
    start: float
    duration: float
    velocity: int
    voice: str


class HarmonyRequest(BaseModel):
    lead_notes: list[dict] = Field(..., description="List of MIDI note dicts")
    key: str = "C Major"
    voice_count: int = Field(2, ge=1, le=3)
    chord_progression: Optional[list[str]] = None
    tighten_voicing: bool = True


class HarmonyResponse(BaseModel):
    lead: list[HarmonyNoteSchema]
    voices: dict[str, list[HarmonyNoteSchema]]
    key: str
    chord_progression: list[str]
    voice_count: int
    midi_tracks: list[dict]


class ParallelHarmonyRequest(BaseModel):
    lead_notes: list[dict]
    interval_semitones: int = Field(7, ge=1, le=12)
    key: str = "C Major"
    voice_name: str = "harmony"
