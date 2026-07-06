"""
Vocal Harmony Service — generate 2–4 part harmonies from a lead melody.

Implements rule-based voice leading (no ML required) plus an optional
AI-assisted mode that uses the Composer agent for richer voicings.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class HarmonyNote:
    """A single note in a harmony voice."""
    pitch: int          # MIDI 0–127
    start: float        # beats
    duration: float     # beats
    velocity: int       # 0–127
    voice: str          # "lead" | "tenor" | "alto" | "baritone"


@dataclass
class HarmonyResult:
    """Multi-voice harmony output."""
    lead: list[HarmonyNote]
    voices: dict[str, list[HarmonyNote]]    # voice_name → notes
    key: str
    chord_progression: list[str]
    voice_count: int


# ── Music theory helpers ──────────────────────────────────────────────────────

# Diatonic intervals above root in semitones for common scales
_MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
_DORIAN      = [0, 2, 3, 5, 7, 9, 10]

_NOTE_TO_SEMITONE = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}


def _parse_key(key_str: str) -> tuple[int, list[int]]:
    """
    Parse a key string like "C Major" or "A Minor" into (root_semitone, scale_steps).
    """
    parts = key_str.strip().split()
    note_part = parts[0] if parts else "C"
    mode_part = parts[1].lower() if len(parts) > 1 else "major"

    root = _NOTE_TO_SEMITONE.get(note_part, 0)
    if "minor" in mode_part or "min" in mode_part:
        scale = _MINOR_SCALE
    elif "dorian" in mode_part:
        scale = _DORIAN
    else:
        scale = _MAJOR_SCALE

    return root, scale


def _nearest_scale_pitch(pitch: int, root: int, scale: list[int], above: bool = True) -> int:
    """
    Find the nearest scale pitch to `pitch`, either above or below.
    """
    pitch_class = (pitch - root) % 12
    # Find closest scale degree
    closest = min(scale, key=lambda s: abs(s - pitch_class))
    delta = closest - pitch_class
    if above and delta < 0:
        delta += 12
    elif not above and delta > 0:
        delta -= 12
    return pitch + delta


def _harmony_at_interval(lead_pitch: int, interval_semitones: int, root: int, scale: list[int]) -> int:
    """Return the nearest scale pitch at approximately `interval_semitones` above lead."""
    target = lead_pitch + interval_semitones
    return _nearest_scale_pitch(target, root, scale, above=True)


# ── Harmony Service ────────────────────────────────────────────────────────────

class VocalHarmonyService:
    """
    Generate vocal harmonies using rule-based voice leading.

    Supports 2–4 voices with configurable intervals and voice ranges.
    """

    # Comfortable MIDI ranges per voice type
    VOICE_RANGES = {
        "soprano": (60, 84),    # C4 – C6
        "mezzo":   (55, 79),    # G3 – G5
        "alto":    (53, 74),    # F3 – D5
        "tenor":   (48, 72),    # C3 – C5
        "baritone":(45, 67),    # A2 – G4
        "bass":    (40, 64),    # E2 – E4
    }

    # Default harmony intervals (semitones above lead)
    DEFAULT_INTERVALS = {
        "tenor":   3,    # minor third above
        "alto":    7,    # perfect fifth above
        "baritone": -4,  # major third below
    }

    def generate_harmonies(
        self,
        lead_notes: list[dict],     # [{"pitch": int, "start": float, "duration": float, "velocity": int}]
        key: str = "C Major",
        voice_count: int = 2,       # 1 (duet) to 3 (quartet)
        chord_progression: Optional[list[str]] = None,
        tighten_voicing: bool = True,
    ) -> HarmonyResult:
        """
        Generate harmonies for a lead melody.

        Args:
            lead_notes: List of lead voice MIDI notes.
            key: Key signature string (e.g. "C Major", "A Minor").
            voice_count: Number of additional harmony voices (1–3).
            chord_progression: Optional chord names for context.
            tighten_voicing: Keep voices within an octave of the lead.

        Returns:
            HarmonyResult with lead + harmony voices.
        """
        root, scale = _parse_key(key)
        voice_count = max(1, min(3, voice_count))

        # Assign voice names
        voice_names = ["tenor", "alto", "baritone"][:voice_count]

        # Build harmony voices
        voices: dict[str, list[HarmonyNote]] = {}
        for voice_name in voice_names:
            interval = self.DEFAULT_INTERVALS.get(voice_name, 4)
            voice_notes = self._generate_voice(
                lead_notes=lead_notes,
                interval=interval,
                root=root,
                scale=scale,
                voice=voice_name,
                tighten=tighten_voicing,
            )
            voices[voice_name] = voice_notes

        # Wrap lead
        lead_harmony = [
            HarmonyNote(
                pitch=n["pitch"],
                start=n["start"],
                duration=n["duration"],
                velocity=n.get("velocity", 80),
                voice="lead",
            )
            for n in lead_notes
        ]

        return HarmonyResult(
            lead=lead_harmony,
            voices=voices,
            key=key,
            chord_progression=chord_progression or [],
            voice_count=voice_count + 1,  # +1 for lead
        )

    def generate_parallel_harmony(
        self,
        lead_notes: list[dict],
        interval_semitones: int = 7,  # perfect 5th
        key: str = "C Major",
        voice_name: str = "harmony",
    ) -> list[HarmonyNote]:
        """
        Generate a simple parallel harmony at a fixed interval.
        Useful for chorus doublings and quick harmonies.
        """
        root, scale = _parse_key(key)
        return self._generate_voice(
            lead_notes=lead_notes,
            interval=interval_semitones,
            root=root,
            scale=scale,
            voice=voice_name,
            tighten=False,
        )

    def voices_to_midi_tracks(
        self,
        harmony_result: HarmonyResult,
        bpm: int = 120,
        include_lead: bool = True,
    ) -> list[dict]:
        """
        Convert a HarmonyResult to a list of MIDI track dicts compatible
        with CompositionResult.tracks format.
        """
        tracks = []

        if include_lead:
            tracks.append({
                "name": "Lead Vocal",
                "channel": 1,
                "instrument": 52,   # GM: choir aahs
                "notes": [
                    {"pitch": n.pitch, "start": n.start,
                     "duration": n.duration, "velocity": n.velocity}
                    for n in harmony_result.lead
                ],
            })

        channel_map = {"tenor": 2, "alto": 3, "baritone": 4}
        for voice_name, notes in harmony_result.voices.items():
            tracks.append({
                "name": f"Harmony {voice_name.capitalize()}",
                "channel": channel_map.get(voice_name, 5),
                "instrument": 52,   # GM: choir aahs
                "notes": [
                    {"pitch": n.pitch, "start": n.start,
                     "duration": n.duration, "velocity": int(n.velocity * 0.8)}
                    for n in notes
                ],
            })

        return tracks

    # ── Private ────────────────────────────────────────────────────────────────

    def _generate_voice(
        self,
        lead_notes: list[dict],
        interval: int,
        root: int,
        scale: list[int],
        voice: str,
        tighten: bool,
    ) -> list[HarmonyNote]:
        """Generate a single harmony voice."""
        lo, hi = self.VOICE_RANGES.get(voice, (48, 84))
        notes: list[HarmonyNote] = []
        prev_pitch: Optional[int] = None

        for n in lead_notes:
            lead_pitch = n["pitch"]
            target = _harmony_at_interval(lead_pitch, interval, root, scale)

            # Clamp to voice range
            while target < lo:
                target += 12
            while target > hi:
                target -= 12

            # Smooth voice leading: prefer minimal movement from previous note
            if prev_pitch is not None and tighten:
                candidates = [target - 12, target, target + 12]
                target = min(
                    (c for c in candidates if lo <= c <= hi),
                    key=lambda c: abs(c - prev_pitch),
                    default=target,
                )

            prev_pitch = target
            notes.append(HarmonyNote(
                pitch=target,
                start=n["start"],
                duration=n["duration"],
                velocity=int(n.get("velocity", 80) * 0.75),
                voice=voice,
            ))

        return notes
