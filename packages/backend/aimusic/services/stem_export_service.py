"""
Stem Export Service — render and export individual track stems as separate WAV files.

A stem is a mix-down of one or more related tracks (e.g. "drums", "bass",
"keys", "vocals"). Each stem gets its own WAV file alongside a full mix.
"""

from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from aimusic.services.audio_service import AudioService, RenderOptions, TrackMixSettings
from aimusic.utils.midi_writer import composition_to_midi_bytes, _HAS_MIDIUTIL

if TYPE_CHECKING:
    from aimusic.services.agents.composer_agent import CompositionResult

logger = logging.getLogger(__name__)


@dataclass
class StemGroup:
    """A logical grouping of tracks that form one stem."""
    name: str                       # e.g. "drums", "bass", "keys"
    track_names: list[str]          # names of tracks included in this stem
    mix_settings: TrackMixSettings = field(default_factory=TrackMixSettings)


@dataclass
class StemExportResult:
    """Result of a stem export operation."""
    full_mix_path: str
    stems: dict[str, str]           # stem_name → wav_path
    duration_seconds: float
    sample_rate: int
    stem_count: int


# ── Default stem groupings by instrument type ─────────────────────────────────

DEFAULT_STEM_GROUPS: dict[str, list[str]] = {
    "drums":  ["Drums", "Percussion", "Hi-Hat", "Kick", "Snare"],
    "bass":   ["Bass", "Electric Bass", "Synth Bass"],
    "keys":   ["Piano", "Electric Piano", "Organ", "Synth", "Synth Pad", "Synth Lead"],
    "guitar": ["Guitar", "Electric Guitar", "Acoustic Guitar"],
    "strings":["Strings", "Violin", "Cello", "Viola", "Orchestra"],
    "brass":  ["Trumpet", "Saxophone", "Trombone", "Horn"],
    "fx":     ["FX", "Ambient", "Noise", "Texture"],
}


class StemExportService:
    """Handles exporting individual stems from a CompositionResult."""

    def __init__(self, output_dir: Optional[str] = None) -> None:
        self.output_dir = output_dir or os.path.join(os.getcwd(), "exports", "stems")
        os.makedirs(self.output_dir, exist_ok=True)

    def export_stems(
        self,
        result: "CompositionResult",
        stem_groups: Optional[list[StemGroup]] = None,
        soundfont_path: Optional[str] = None,
        sample_rate: int = 48_000,
        normalize: bool = True,
        song_name: str = "composition",
    ) -> StemExportResult:
        """
        Export all stems from a CompositionResult.

        For each stem group, mutes all tracks not in the group, renders MIDI,
        and saves a separate WAV. Also renders the full mix.

        Args:
            result: CompositionResult from ComposerAgent.compose().
            stem_groups: Custom groupings; auto-grouped if None.
            soundfont_path: Path to SF2 soundfont.
            sample_rate: Output sample rate.
            normalize: Apply peak normalisation.
            song_name: Base name for output files.

        Returns:
            StemExportResult with paths to all rendered files.
        """
        if not _HAS_MIDIUTIL:
            raise RuntimeError("midiutil required: pip install midiutil")

        groups = stem_groups or self._auto_group(result)

        options = RenderOptions(
            sample_rate=sample_rate,
            normalize=normalize,
            soundfont_path=soundfont_path,
        )
        svc = AudioService(options)

        # 1. Full mix
        full_midi = self._write_temp_midi(result)
        full_wav  = os.path.join(self.output_dir, f"{song_name}_full_mix.wav")
        try:
            render = svc.render_midi_file(full_midi, full_wav, soundfont_path)
            duration = render.duration_seconds
            sr = render.sample_rate
        finally:
            _safe_unlink(full_midi)

        # 2. Individual stems
        stems_out: dict[str, str] = {}

        for group in groups:
            # Build a filtered CompositionResult containing only this stem's tracks
            filtered = self._filter_tracks(result, group.track_names)
            if not filtered.tracks:
                logger.info(f"Stem '{group.name}': no matching tracks, skipping")
                continue

            stem_midi = self._write_temp_midi(filtered)
            stem_wav  = os.path.join(self.output_dir, f"{song_name}_stem_{group.name}.wav")
            try:
                svc.render_midi_file(stem_midi, stem_wav, soundfont_path)
                stems_out[group.name] = stem_wav
                logger.info(f"Stem '{group.name}' → {stem_wav}")
            except (RuntimeError, FileNotFoundError) as exc:
                logger.warning(f"Stem '{group.name}' render failed: {exc}")
            finally:
                _safe_unlink(stem_midi)

        return StemExportResult(
            full_mix_path=full_wav,
            stems=stems_out,
            duration_seconds=duration,
            sample_rate=sr,
            stem_count=len(stems_out),
        )

    # ── Private ───────────────────────────────────────────────────────────────

    def _auto_group(self, result: "CompositionResult") -> list[StemGroup]:
        """Automatically assign tracks to stem groups by instrument name."""
        groups: list[StemGroup] = []
        assigned: set[str] = set()

        for stem_name, keywords in DEFAULT_STEM_GROUPS.items():
            members = [
                t.name for t in result.tracks
                if any(kw.lower() in t.name.lower() for kw in keywords)
            ]
            if members:
                groups.append(StemGroup(name=stem_name, track_names=members))
                assigned.update(members)

        # Catch-all for unassigned tracks
        other = [t.name for t in result.tracks if t.name not in assigned]
        if other:
            groups.append(StemGroup(name="other", track_names=other))

        return groups

    @staticmethod
    def _filter_tracks(
        result: "CompositionResult",
        track_names: list[str],
    ) -> "CompositionResult":
        """Return a copy of result containing only named tracks."""
        from aimusic.services.agents.composer_agent import CompositionResult as CR
        lc_names = {n.lower() for n in track_names}
        kept = [t for t in result.tracks if t.name.lower() in lc_names]
        return CR(
            tempo=result.tempo,
            time_signature_numerator=result.time_signature_numerator,
            time_signature_denominator=result.time_signature_denominator,
            key=result.key,
            tracks=kept,
            chord_progression=result.chord_progression,
            structure=result.structure,
        )

    @staticmethod
    def _write_temp_midi(result: "CompositionResult") -> str:
        """Write a CompositionResult to a temp MIDI file and return the path."""
        data = composition_to_midi_bytes(result)
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp:
            tmp.write(data)
            return tmp.name


def _safe_unlink(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass
