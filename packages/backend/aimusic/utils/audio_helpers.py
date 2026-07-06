"""
Audio helper utilities — format conversion, loudness measurement,
stem detection, and duration estimation.
"""

from __future__ import annotations

import math
import os
from typing import Optional


# ── Loudness standards ────────────────────────────────────────────────────────

PLATFORM_TARGETS: dict[str, float] = {
    "spotify":      -14.0,   # Integrated LUFS
    "apple_music":  -16.0,
    "youtube":      -14.0,
    "amazon_music": -14.0,
    "tidal":        -14.0,
    "soundcloud":   -14.0,
    "cd":            -9.0,
    "broadcast":    -23.0,
    "vinyl":        -12.0,
}


def target_lufs(platform: str) -> float:
    """Return the target integrated LUFS for a streaming platform."""
    return PLATFORM_TARGETS.get(platform.lower(), -14.0)


# ── File utilities ────────────────────────────────────────────────────────────

def wav_duration_from_header(path: str) -> Optional[float]:
    """
    Read WAV duration in seconds directly from the file header.
    Fast — does not load audio data. Returns None on error.
    """
    try:
        import wave
        with wave.open(path, "rb") as wf:
            return wf.getnframes() / wf.getframerate()
    except Exception:
        return None


def format_bytes(size: int) -> str:
    """Human-readable file size string."""
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size //= 1024
    return f"{size:.1f} TB"


def audio_format_from_path(path: str) -> str:
    """Return lowercase audio format from file extension."""
    return os.path.splitext(path)[1].lstrip(".").lower()


# ── BPM / timing helpers ──────────────────────────────────────────────────────

def beats_to_seconds(beats: float, bpm: float) -> float:
    """Convert a beat position to seconds."""
    return beats * (60.0 / bpm)


def seconds_to_beats(seconds: float, bpm: float) -> float:
    """Convert seconds to beats."""
    return seconds * (bpm / 60.0)


def bars_to_seconds(bars: int, bpm: float, beats_per_bar: int = 4) -> float:
    """Convert bars to seconds."""
    return beats_to_seconds(bars * beats_per_bar, bpm)


def estimate_render_time(bars: int, bpm: float, track_count: int) -> float:
    """
    Rough estimate of FluidSynth render time in seconds.
    Assumes ~0.2s per bar per track on an average machine.
    """
    return bars_to_seconds(bars, bpm) * 0.1 + track_count * 0.5


# ── MIDI helpers ──────────────────────────────────────────────────────────────

def midi_pitch_to_name(pitch: int) -> str:
    """Convert MIDI pitch number to note name (e.g. 60 → 'C4')."""
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = (pitch // 12) - 1
    name   = note_names[pitch % 12]
    return f"{name}{octave}"


def note_name_to_midi(name: str) -> int:
    """
    Convert note name to MIDI pitch (e.g. 'C4' → 60, 'A#3' → 58).
    Raises ValueError for invalid input.
    """
    mapping = {"C":0,"C#":1,"Db":1,"D":2,"D#":3,"Eb":3,"E":4,"F":5,
               "F#":6,"Gb":6,"G":7,"G#":8,"Ab":8,"A":9,"A#":10,"Bb":10,"B":11}

    name = name.strip()
    # Split into note + octave
    if len(name) >= 3 and name[1] in ("#", "b"):
        note_part = name[:2]
        octave    = int(name[2:])
    else:
        note_part = name[0]
        octave    = int(name[1:])

    if note_part not in mapping:
        raise ValueError(f"Unknown note: {note_part!r}")
    return (octave + 1) * 12 + mapping[note_part]


def quantize_beat(beat: float, grid: float = 0.25) -> float:
    """Snap a beat position to the nearest grid division."""
    return round(beat / grid) * grid
