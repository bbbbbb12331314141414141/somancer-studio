"""
MIDI Writer — convert CompositionResult to a standard .mid file.

Uses the `midiutil` library (pure-Python, no C dependencies).

Install:  pip install midiutil
"""

from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

try:
    from midiutil import MIDIFile
    _HAS_MIDIUTIL = True
except ImportError:
    _HAS_MIDIUTIL = False
    logger.warning("midiutil not installed — MIDI export disabled. Run: pip install midiutil")

if TYPE_CHECKING:
    from aimusic.services.agents.composer_agent import CompositionResult


def composition_to_midi_bytes(result: "CompositionResult") -> bytes:
    """
    Convert a CompositionResult into a MIDI file and return raw bytes.

    Raises RuntimeError if midiutil is not installed.
    """
    if not _HAS_MIDIUTIL:
        raise RuntimeError(
            "midiutil is required for MIDI export. Install with: pip install midiutil"
        )

    num_tracks = max(1, len(result.tracks))
    midi = MIDIFile(num_tracks, deinterleave=False)

    # Write tempo on track 0
    midi.addTempo(track=0, time=0, tempo=result.tempo)
    midi.addTimeSignature(
        track=0,
        time=0,
        numerator=result.time_signature_numerator,
        denominator=result.time_signature_denominator,
        clocks_per_tick=24,
    )

    for track_idx, track in enumerate(result.tracks):
        midi.addTrackName(track=track_idx, time=0, trackName=track.name)
        midi.addProgramChange(
            track=track_idx,
            channel=track.channel - 1,  # midiutil uses 0-based channels
            time=0,
            program=track.instrument,
        )

        for note in track.notes:
            channel = track.channel - 1  # 0-based
            midi.addNote(
                track=track_idx,
                channel=channel,
                pitch=note.pitch,
                time=note.start,
                duration=note.duration,
                volume=note.velocity,
            )

    buffer = io.BytesIO()
    midi.writeFile(buffer)
    return buffer.getvalue()


def save_midi_file(result: "CompositionResult", path: str) -> str:
    """Write MIDI file to disk and return the path."""
    data = composition_to_midi_bytes(result)
    with open(path, "wb") as f:
        f.write(data)
    logger.info(f"MIDI file written: {path}")
    return path
