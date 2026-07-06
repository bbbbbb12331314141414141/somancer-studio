"""
Audio Service — FluidSynth MIDI rendering and audio processing.

Converts MIDI data to audio using SF2 soundfonts, applies basic
mixing (gain, pan), and returns WAV/PCM output.

Dependencies:
    pip install pyfluidsynth soundfile numpy scipy
    apt-get install fluidsynth  (or brew install fluid-synth)
"""

from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy imports — only fail at call time if missing
try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

try:
    import soundfile as sf
    _HAS_SOUNDFILE = True
except ImportError:
    _HAS_SOUNDFILE = False

try:
    import fluidsynth
    _HAS_FLUIDSYNTH = True
except ImportError:
    _HAS_FLUIDSYNTH = False


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class TrackMixSettings:
    """Per-track mixing parameters."""
    volume: float = 1.0       # 0.0 – 2.0
    pan: float = 0.0          # -1.0 (L) to 1.0 (R)
    muted: bool = False
    solo: bool = False
    reverb: float = 0.0       # 0.0 – 1.0
    chorus: float = 0.0       # 0.0 – 1.0


@dataclass
class RenderOptions:
    """Options for the audio render pipeline."""
    sample_rate: int = 48_000
    bit_depth: int = 24
    channels: int = 2          # 1 = mono, 2 = stereo
    normalize: bool = True
    peak_db: float = -1.0      # Target peak after normalisation
    soundfont_path: Optional[str] = None
    track_settings: dict[str, TrackMixSettings] = field(default_factory=dict)


@dataclass
class RenderResult:
    """Result of a render operation."""
    wav_path: str
    duration_seconds: float
    sample_rate: int
    peak_db: float
    track_count: int


# ── Helpers ───────────────────────────────────────────────────────────────────

def _find_default_soundfont() -> Optional[str]:
    """Search common locations for an SF2 soundfont."""
    candidates = [
        "/usr/share/sounds/sf2/FluidR3_GM.sf2",
        "/usr/share/soundfonts/FluidR3_GM.sf2",
        "/usr/local/share/sounds/sf2/FluidR3_GM.sf2",
        os.path.expanduser("~/.local/share/sounds/sf2/FluidR3_GM.sf2"),
        "C:/Windows/System32/drivers/gm.dls",
        os.path.join(os.getcwd(), "soundfonts", "default.sf2"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def _db_to_linear(db: float) -> float:
    """Convert dB value to linear amplitude."""
    return 10 ** (db / 20.0)


def _linear_to_db(linear: float) -> float:
    """Convert linear amplitude to dB."""
    if linear <= 0:
        return -96.0
    import math
    return 20 * math.log10(linear)


# ── AudioService ──────────────────────────────────────────────────────────────

class AudioService:
    """
    Handles MIDI → audio rendering via FluidSynth.

    All methods check for required dependencies before executing and
    raise RuntimeError with installation instructions if missing.
    """

    def __init__(self, options: Optional[RenderOptions] = None) -> None:
        self.options = options or RenderOptions()

    # ── Public API ────────────────────────────────────────────────────────────

    def render_midi_file(
        self,
        midi_path: str,
        output_path: Optional[str] = None,
        soundfont_path: Optional[str] = None,
    ) -> RenderResult:
        """
        Render a MIDI file to WAV using FluidSynth.

        Args:
            midi_path: Path to the .mid file to render.
            output_path: Destination WAV path (auto-generated if None).
            soundfont_path: Path to SF2 soundfont (auto-detected if None).

        Returns:
            RenderResult with path and metadata.

        Raises:
            RuntimeError: If FluidSynth or required deps are not installed.
            FileNotFoundError: If midi_path or soundfont does not exist.
        """
        self._check_deps()

        sf2 = soundfont_path or self.options.soundfont_path or _find_default_soundfont()
        if not sf2:
            raise FileNotFoundError(
                "No SF2 soundfont found. Download FluidR3_GM.sf2 and place it in "
                "./soundfonts/default.sf2, or install fluidsynth system soundfonts:\n"
                "  Ubuntu: sudo apt-get install fluid-soundfont-gm\n"
                "  macOS:  brew install fluid-synth"
            )
        if not os.path.isfile(sf2):
            raise FileNotFoundError(f"Soundfont not found: {sf2}")
        if not os.path.isfile(midi_path):
            raise FileNotFoundError(f"MIDI file not found: {midi_path}")

        if output_path is None:
            stem = Path(midi_path).stem
            output_path = os.path.join(tempfile.gettempdir(), f"{stem}_rendered.wav")

        logger.info(f"Rendering {midi_path} → {output_path} (SF2: {sf2})")

        fs = fluidsynth.Synth(samplerate=float(self.options.sample_rate))
        fs.start(driver="file")           # Render to file (no audio device needed)
        sfid = fs.sfload(sf2)
        fs.program_select(0, sfid, 0, 0)

        # Use FluidSynth CLI for reliable file rendering
        import subprocess
        cmd = [
            "fluidsynth",
            "-ni",                         # Non-interactive, no audio output
            "-F", output_path,             # Write to file
            "-r", str(self.options.sample_rate),
            sf2,
            midi_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FluidSynth rendering failed:\n{result.stderr}")

        fs.delete()

        # Post-process: normalise if requested
        duration = self._get_wav_duration(output_path)
        peak = self._get_peak_db(output_path)

        if self.options.normalize:
            output_path = self._normalize_wav(output_path, self.options.peak_db)
            peak = self.options.peak_db

        return RenderResult(
            wav_path=output_path,
            duration_seconds=duration,
            sample_rate=self.options.sample_rate,
            peak_db=peak,
            track_count=1,
        )

    def mix_wav_files(
        self,
        wav_paths: list[str],
        output_path: str,
        track_settings: Optional[list[TrackMixSettings]] = None,
    ) -> RenderResult:
        """
        Mix multiple WAV files into a single stereo output.

        Args:
            wav_paths: List of WAV files to mix.
            output_path: Destination for the mixed WAV.
            track_settings: Per-track gain/pan (uses defaults if None).

        Returns:
            RenderResult with path and metadata.
        """
        self._check_deps()
        if not wav_paths:
            raise ValueError("No WAV files provided for mixing")

        settings = track_settings or [TrackMixSettings() for _ in wav_paths]

        # Load all tracks as numpy arrays
        tracks: list[np.ndarray] = []
        sr: Optional[int] = None

        for path, mix in zip(wav_paths, settings):
            if mix.muted:
                continue
            data, file_sr = sf.read(path, dtype="float32", always_2d=True)
            if sr is None:
                sr = file_sr
            elif file_sr != sr:
                logger.warning(f"Sample rate mismatch: {file_sr} vs {sr}, skipping {path}")
                continue

            # Apply gain
            data = data * mix.volume

            # Apply pan (stereo only)
            if data.shape[1] == 2:
                left_gain  = min(1.0, 1.0 - mix.pan)
                right_gain = min(1.0, 1.0 + mix.pan)
                data[:, 0] *= left_gain
                data[:, 1] *= right_gain

            tracks.append(data)

        if not tracks:
            raise ValueError("All tracks were muted")

        # Pad to same length and sum
        max_len = max(t.shape[0] for t in tracks)
        mixed = np.zeros((max_len, 2), dtype=np.float32)
        for t in tracks:
            pad = max_len - t.shape[0]
            if pad > 0:
                t = np.pad(t, ((0, pad), (0, 0)))
            mixed += t

        # Normalise
        peak = float(np.max(np.abs(mixed)))
        if self.options.normalize and peak > 0:
            target = _db_to_linear(self.options.peak_db)
            mixed = mixed * (target / peak)

        sf.write(output_path, mixed, sr or self.options.sample_rate, subtype="PCM_24")

        return RenderResult(
            wav_path=output_path,
            duration_seconds=len(mixed) / (sr or self.options.sample_rate),
            sample_rate=sr or self.options.sample_rate,
            peak_db=_linear_to_db(float(np.max(np.abs(mixed)))),
            track_count=len(tracks),
        )

    def get_waveform_data(
        self,
        wav_path: str,
        num_points: int = 1000,
    ) -> dict:
        """
        Extract waveform data for visualisation.

        Returns a dict with:
            - peaks: list of peak amplitudes (normalised 0–1)
            - rms: list of RMS values per chunk
            - duration_seconds: total duration
            - sample_rate: file sample rate
        """
        self._check_deps()
        data, sr = sf.read(wav_path, dtype="float32", always_2d=True)

        # Convert to mono for waveform
        mono = np.mean(data, axis=1)
        chunk_size = max(1, len(mono) // num_points)

        peaks = []
        rms_vals = []
        for i in range(0, len(mono), chunk_size):
            chunk = mono[i : i + chunk_size]
            peaks.append(float(np.max(np.abs(chunk))))
            rms_vals.append(float(np.sqrt(np.mean(chunk ** 2))))

        max_peak = max(peaks) if peaks else 1.0

        return {
            "peaks": [p / max_peak for p in peaks],
            "rms":   [r / max_peak for r in rms_vals],
            "duration_seconds": len(mono) / sr,
            "sample_rate": sr,
        }

    # ── Private ───────────────────────────────────────────────────────────────

    def _check_deps(self) -> None:
        missing = []
        if not _HAS_NUMPY:
            missing.append("numpy")
        if not _HAS_SOUNDFILE:
            missing.append("soundfile")
        if not _HAS_FLUIDSYNTH:
            missing.append("pyfluidsynth")
        if missing:
            raise RuntimeError(
                f"Missing audio dependencies: {', '.join(missing)}\n"
                f"Install with: pip install {' '.join(missing)}\n"
                f"Also ensure fluidsynth is installed: sudo apt-get install fluidsynth"
            )

    def _get_wav_duration(self, path: str) -> float:
        info = sf.info(path)
        return info.frames / info.samplerate

    def _get_peak_db(self, path: str) -> float:
        data, _ = sf.read(path, dtype="float32")
        peak = float(np.max(np.abs(data)))
        return _linear_to_db(peak)

    def _normalize_wav(self, path: str, target_db: float = -1.0) -> str:
        data, sr = sf.read(path, dtype="float32", always_2d=True)
        peak = float(np.max(np.abs(data)))
        if peak > 0:
            gain = _db_to_linear(target_db) / peak
            data = np.clip(data * gain, -1.0, 1.0)
        sf.write(path, data, sr, subtype="PCM_24")
        return path
