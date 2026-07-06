"""
Vocal Synthesis Service — text-to-singing pipeline foundation.

Phase 5 scaffolding. Provides:
  1. Phoneme conversion (text → IPA approximation)
  2. Note-aligned lyric timing
  3. Stub TTS fallback (pyttsx3) for dev testing
  4. Interface for future DiffSinger / RVC / VITS integration

Full singing model integration ships in Phase 6.
"""

from __future__ import annotations

import logging
import os
import re
import tempfile
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class PhonemeSegment:
    """A phoneme aligned to a MIDI note."""
    phoneme: str          # IPA-ish representation
    start_beat: float
    duration_beats: float
    pitch: int            # MIDI pitch


@dataclass
class VocalLine:
    """A line of lyrics with per-word timing."""
    text: str
    section: str          # verse | chorus | bridge
    phoneme_segments: list[PhonemeSegment] = field(default_factory=list)
    audio_path: Optional[str] = None


@dataclass
class VocalSynthesisResult:
    """Result of the vocal synthesis pipeline."""
    audio_path: str
    duration_seconds: float
    sample_rate: int
    lines_rendered: int
    engine: str           # "tts_stub" | "diffsinger" | "rvc" | "vits"


# ── Simple English → phoneme approximation ─────────────────────────────────────

# Minimal CMU-style mapping for common words (expandable)
_PHONEME_MAP: dict[str, str] = {
    "the": "ðə", "a": "ə", "and": "ænd", "in": "ɪn", "is": "ɪz",
    "i": "aɪ", "you": "juː", "me": "miː", "my": "maɪ", "we": "wiː",
    "love": "lʌv", "heart": "hɑːrt", "night": "naɪt", "light": "laɪt",
    "sky": "skaɪ", "dream": "driːm", "feel": "fiːl", "rain": "reɪn",
    "fire": "faɪər", "soul": "soʊl", "time": "taɪm", "road": "roʊd",
    "home": "hoʊm", "free": "friː", "rise": "raɪz", "fall": "fɔːl",
}


def text_to_phonemes(text: str) -> list[str]:
    """
    Convert a lyric line to a list of approximate IPA phonemes.

    This is a best-effort approximation for English. Real deployment
    should use an espeak-ng, Festival, or Flite backend.
    """
    words = re.sub(r"[^\w\s'-]", "", text.lower()).split()
    phonemes = []
    for word in words:
        ph = _PHONEME_MAP.get(word)
        if ph:
            phonemes.extend(list(ph))
        else:
            # Naive: treat each letter as a phoneme placeholder
            phonemes.extend([c for c in word if c.isalpha()])
    return phonemes


def align_phonemes_to_notes(
    text: str,
    notes: list[dict],   # [{"pitch": int, "start": float, "duration": float}]
    section: str = "verse",
) -> VocalLine:
    """
    Align phonemes evenly across available MIDI notes.

    Args:
        text: Lyric line.
        notes: MIDI notes from ComposerAgent.
        section: Song section name.

    Returns:
        VocalLine with phoneme segments timed to notes.
    """
    phonemes = text_to_phonemes(text)
    if not phonemes or not notes:
        return VocalLine(text=text, section=section)

    # Distribute phonemes across notes
    segments: list[PhonemeSegment] = []
    ph_per_note = max(1, len(phonemes) // len(notes))

    ph_idx = 0
    for note in notes:
        note_phonemes = phonemes[ph_idx: ph_idx + ph_per_note]
        if not note_phonemes:
            break
        dur_each = note["duration"] / max(1, len(note_phonemes))
        for j, ph in enumerate(note_phonemes):
            segments.append(PhonemeSegment(
                phoneme=ph,
                start_beat=note["start"] + j * dur_each,
                duration_beats=dur_each,
                pitch=note["pitch"],
            ))
        ph_idx += ph_per_note

    return VocalLine(text=text, section=section, phoneme_segments=segments)


# ── Synthesis engine stubs ────────────────────────────────────────────────────

class VocalSynthesisService:
    """
    Vocal synthesis pipeline.

    Phase 5 uses pyttsx3 TTS as a development stub.
    Phase 6 will integrate DiffSinger / VITS singing models.
    """

    def __init__(self, engine: str = "tts_stub") -> None:
        self.engine = engine

    # ── Public ────────────────────────────────────────────────────────────────

    def synthesise(
        self,
        vocal_lines: list[VocalLine],
        bpm: float = 120.0,
        output_path: Optional[str] = None,
    ) -> VocalSynthesisResult:
        """
        Render vocal lines to audio.

        Currently uses pyttsx3 TTS as a stub. Each line is rendered
        individually, then concatenated into a single WAV.

        Args:
            vocal_lines: Lines with text and optional phoneme alignment.
            bpm: Song tempo for timing calculations.
            output_path: Destination WAV (auto-generated if None).

        Returns:
            VocalSynthesisResult with path and metadata.
        """
        if output_path is None:
            output_path = os.path.join(
                os.getcwd(), "exports", "vocals", "vocal_render.wav"
            )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if self.engine == "tts_stub":
            return self._render_tts_stub(vocal_lines, output_path)
        elif self.engine == "diffsinger":
            return self._render_diffsinger(vocal_lines, bpm, output_path)
        else:
            raise ValueError(f"Unknown vocal engine: {self.engine!r}")

    def get_available_engines(self) -> list[dict]:
        """Return available synthesis engines and their status."""
        engines = []

        # TTS stub
        try:
            import pyttsx3
            pyttsx3.init()
            engines.append({
                "name": "tts_stub",
                "label": "TTS (development stub)",
                "available": True,
                "quality": "low",
                "note": "pyttsx3 text-to-speech; not a singing voice",
            })
        except ImportError:
            engines.append({
                "name": "tts_stub",
                "label": "TTS (development stub)",
                "available": False,
                "quality": "low",
                "note": "Install with: pip install pyttsx3",
            })

        # DiffSinger
        engines.append({
            "name": "diffsinger",
            "label": "DiffSinger (singing synthesis)",
            "available": False,
            "quality": "high",
            "note": "Coming in Phase 6 — requires DiffSinger model weights",
        })

        # RVC
        engines.append({
            "name": "rvc",
            "label": "RVC (voice conversion)",
            "available": False,
            "quality": "high",
            "note": "Coming in Phase 6 — requires RVC model weights",
        })

        return engines

    # ── Private: TTS stub ─────────────────────────────────────────────────────

    @staticmethod
    def _render_tts_stub(
        vocal_lines: list[VocalLine],
        output_path: str,
    ) -> VocalSynthesisResult:
        """Render lyrics as TTS speech (development placeholder)."""
        try:
            import pyttsx3
        except ImportError:
            raise RuntimeError(
                "pyttsx3 not installed.\n"
                "Install with: pip install pyttsx3\n"
                "Note: TTS stub produces speech, not singing. "
                "Full singing synthesis arrives in Phase 6."
            )

        engine = pyttsx3.init()
        engine.setProperty("rate", 140)
        engine.setProperty("volume", 0.9)

        # Concatenate all lyric lines with pauses
        full_text = "  ".join(line.text for line in vocal_lines)
        engine.save_to_file(full_text, output_path)
        engine.runAndWait()

        if not os.path.isfile(output_path):
            raise RuntimeError("pyttsx3 did not write output file")

        return VocalSynthesisResult(
            audio_path=output_path,
            duration_seconds=len(vocal_lines) * 3.0,   # rough estimate
            sample_rate=22_050,
            lines_rendered=len(vocal_lines),
            engine="tts_stub",
        )

    # ── Private: DiffSinger stub (Phase 6) ────────────────────────────────────

    @staticmethod
    def _render_diffsinger(
        vocal_lines: list[VocalLine],
        bpm: float,
        output_path: str,
    ) -> VocalSynthesisResult:
        raise NotImplementedError(
            "DiffSinger integration arrives in Phase 6. "
            "Use engine='tts_stub' for development."
        )
