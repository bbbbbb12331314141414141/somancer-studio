"""
Export Service — multi-format audio and project archive export.

Formats:
  Audio:   WAV, FLAC, MP3 (via ffmpeg), OGG, AAC, AIFF
  MIDI:    Standard MIDI (.mid)
  Stems:   ZIP bundle of individual stem WAV files
  Lyrics:  TXT, Markdown, PDF (via reportlab)
  Project: .sonmancer (ZIP archive with all assets + metadata JSON)
  Chord Charts: PDF
  Lead Sheets:  PDF

External dependencies (all optional, fail gracefully):
  ffmpeg  — MP3, OGG, AAC, AIFF conversion
  reportlab — PDF generation (lyrics, chord charts, lead sheets)
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class ExportResult:
    """Result of any export operation."""
    path: str
    format: str
    size_bytes: int
    duration_seconds: Optional[float] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ProjectArchiveResult:
    """Result of a full project archive export."""
    path: str
    size_bytes: int
    included_files: list[str]
    song_count: int
    export_time: str


# ── Format registry ───────────────────────────────────────────────────────────

AUDIO_FORMATS = {
    "wav":  {"extension": ".wav",  "mime": "audio/wav",   "ffmpeg": False},
    "flac": {"extension": ".flac", "mime": "audio/flac",  "ffmpeg": True},
    "mp3":  {"extension": ".mp3",  "mime": "audio/mpeg",  "ffmpeg": True},
    "ogg":  {"extension": ".ogg",  "mime": "audio/ogg",   "ffmpeg": True},
    "aac":  {"extension": ".aac",  "mime": "audio/aac",   "ffmpeg": True},
    "aiff": {"extension": ".aiff", "mime": "audio/aiff",  "ffmpeg": True},
}

QUALITY_PRESETS = {
    "lossless": {"flac": "-compression_level 8", "wav": ""},
    "hq":       {"mp3": "-b:a 320k", "ogg": "-q:a 9", "aac": "-b:a 256k"},
    "standard": {"mp3": "-b:a 192k", "ogg": "-q:a 6", "aac": "-b:a 128k"},
    "low":      {"mp3": "-b:a 128k", "ogg": "-q:a 3", "aac": "-b:a 96k"},
}


# ── Export Service ─────────────────────────────────────────────────────────────

class ExportService:
    """Handles all audio, MIDI, lyrics, and project archive exports."""

    def __init__(self, output_dir: Optional[str] = None) -> None:
        self.output_dir = output_dir or os.path.join(os.getcwd(), "exports")
        os.makedirs(self.output_dir, exist_ok=True)

    # ── Audio Conversion ──────────────────────────────────────────────────────

    def convert_audio(
        self,
        source_wav: str,
        target_format: str,
        quality: str = "hq",
        output_path: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> ExportResult:
        """
        Convert a WAV file to the target audio format.

        WAV→WAV is a copy. All other formats use ffmpeg.

        Args:
            source_wav: Path to source WAV file.
            target_format: One of wav, flac, mp3, ogg, aac, aiff.
            quality: One of lossless, hq, standard, low.
            output_path: Destination path (auto-generated if None).
            metadata: ID3/FLAC tags to embed.

        Returns:
            ExportResult with output path and metadata.
        """
        fmt = target_format.lower()
        if fmt not in AUDIO_FORMATS:
            raise ValueError(f"Unsupported format: {fmt!r}. Choose from: {list(AUDIO_FORMATS)}")

        if not os.path.isfile(source_wav):
            raise FileNotFoundError(f"Source WAV not found: {source_wav}")

        info = AUDIO_FORMATS[fmt]
        if output_path is None:
            stem = Path(source_wav).stem
            output_path = os.path.join(self.output_dir, f"{stem}{info['extension']}")

        if fmt == "wav":
            shutil.copy2(source_wav, output_path)
        else:
            self._ffmpeg_convert(source_wav, output_path, fmt, quality, metadata or {})

        size = os.path.getsize(output_path)
        return ExportResult(
            path=output_path,
            format=fmt,
            size_bytes=size,
            metadata=metadata or {},
        )

    def batch_export(
        self,
        source_wav: str,
        formats: list[str],
        quality: str = "hq",
        base_name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict[str, ExportResult]:
        """
        Export a WAV to multiple formats simultaneously.

        Returns a dict mapping format → ExportResult.
        """
        if base_name is None:
            base_name = Path(source_wav).stem

        results: dict[str, ExportResult] = {}
        for fmt in formats:
            try:
                info = AUDIO_FORMATS.get(fmt.lower(), {})
                ext = info.get("extension", f".{fmt}")
                out_path = os.path.join(self.output_dir, f"{base_name}{ext}")
                results[fmt] = self.convert_audio(
                    source_wav, fmt, quality, out_path, metadata
                )
                logger.info(f"Exported {fmt}: {out_path}")
            except Exception as exc:
                logger.warning(f"Export to {fmt} failed: {exc}")
        return results

    # ── Stems ZIP ─────────────────────────────────────────────────────────────

    def export_stems_zip(
        self,
        stem_paths: dict[str, str],
        song_name: str = "composition",
        include_full_mix: bool = True,
        full_mix_path: Optional[str] = None,
    ) -> ExportResult:
        """
        Bundle individual stem WAV files into a single ZIP archive.

        Args:
            stem_paths: {stem_name: wav_path} dict.
            song_name: Base name for the archive.
            include_full_mix: Add full mix WAV to archive if provided.
            full_mix_path: Path to the full mix WAV.

        Returns:
            ExportResult pointing to the ZIP file.
        """
        zip_path = os.path.join(self.output_dir, f"{song_name}_stems.zip")

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for stem_name, wav_path in stem_paths.items():
                if os.path.isfile(wav_path):
                    arcname = f"{song_name}_stem_{stem_name}.wav"
                    zf.write(wav_path, arcname)
                    logger.info(f"  Added stem: {arcname}")

            if include_full_mix and full_mix_path and os.path.isfile(full_mix_path):
                zf.write(full_mix_path, f"{song_name}_full_mix.wav")

            # Include README
            readme = f"""# {song_name} — Stems

Generated by Sonmancer Studio
Export date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## Stems included:
""" + "\n".join(f"- {song_name}_stem_{name}.wav" for name in stem_paths)
            zf.writestr("README.txt", readme)

        size = os.path.getsize(zip_path)
        return ExportResult(
            path=zip_path,
            format="zip",
            size_bytes=size,
            metadata={"stem_count": len(stem_paths), "song_name": song_name},
        )

    # ── Lyrics Export ─────────────────────────────────────────────────────────

    def export_lyrics_txt(
        self,
        lyrics: list[dict],
        song_name: str = "lyrics",
        include_metadata: bool = True,
    ) -> ExportResult:
        """
        Export lyrics to a plain text file.

        Each line: "{section}: {text}"
        """
        out_path = os.path.join(self.output_dir, f"{song_name}_lyrics.txt")
        lines = []

        if include_metadata:
            lines.append(f"# {song_name}")
            lines.append(f"# Generated by Sonmancer Studio")
            lines.append(f"# {datetime.utcnow().strftime('%Y-%m-%d')}")
            lines.append("")

        current_section = None
        for lyric in sorted(lyrics, key=lambda l: (l.get("section", ""), l.get("line_number", 0))):
            section = lyric.get("section", "verse")
            if section != current_section:
                lines.append(f"\n[{section.upper()}]")
                current_section = section
            lines.append(lyric.get("text", ""))

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return ExportResult(
            path=out_path,
            format="txt",
            size_bytes=os.path.getsize(out_path),
            metadata={"line_count": len(lyrics)},
        )

    def export_lyrics_pdf(
        self,
        lyrics: list[dict],
        song_name: str = "lyrics",
        artist_name: str = "",
    ) -> ExportResult:
        """Export lyrics to PDF using reportlab."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
            )
            from reportlab.lib.units import cm
        except ImportError:
            raise RuntimeError(
                "reportlab not installed. Install with: pip install reportlab"
            )

        out_path = os.path.join(self.output_dir, f"{song_name}_lyrics.pdf")
        doc = SimpleDocTemplate(
            out_path, pagesize=A4,
            leftMargin=3*cm, rightMargin=3*cm,
            topMargin=3*cm, bottomMargin=3*cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title", parent=styles["Title"], fontSize=24, spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "Subtitle", parent=styles["Normal"], fontSize=12,
            textColor=(0.4, 0.4, 0.4), spaceAfter=20,
        )
        section_style = ParagraphStyle(
            "Section", parent=styles["Normal"], fontSize=10,
            textColor=(0.6, 0.6, 0.6), spaceBefore=16, spaceAfter=4,
            fontName="Helvetica-Bold",
        )
        lyric_style = ParagraphStyle(
            "Lyric", parent=styles["Normal"], fontSize=13, leading=20,
        )

        story = [
            Paragraph(song_name, title_style),
        ]
        if artist_name:
            story.append(Paragraph(artist_name, subtitle_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=(0.8, 0.8, 0.8)))
        story.append(Spacer(1, 0.5*cm))

        current_section = None
        for lyric in sorted(lyrics, key=lambda l: (l.get("section", ""), l.get("line_number", 0))):
            section = lyric.get("section", "verse")
            if section != current_section:
                story.append(Paragraph(section.upper(), section_style))
                current_section = section
            story.append(Paragraph(lyric.get("text", ""), lyric_style))

        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"Generated by Sonmancer Studio • {datetime.utcnow().strftime('%Y-%m-%d')}",
            ParagraphStyle("Footer", parent=styles["Normal"],
                           fontSize=8, textColor=(0.6, 0.6, 0.6)),
        ))

        doc.build(story)

        return ExportResult(
            path=out_path,
            format="pdf",
            size_bytes=os.path.getsize(out_path),
            metadata={"line_count": len(lyrics), "artist": artist_name},
        )

    # ── Project Archive ───────────────────────────────────────────────────────

    def export_project_archive(
        self,
        project_data: dict,
        songs_data: list[dict],
        audio_paths: Optional[list[str]] = None,
        midi_paths: Optional[list[str]] = None,
        output_path: Optional[str] = None,
    ) -> ProjectArchiveResult:
        """
        Create a complete .sonmancer project archive.

        The archive is a standard ZIP containing:
          project.json          — project + songs metadata
          audio/                — rendered WAV files
          midi/                 — MIDI files
          lyrics/               — lyrics per song as TXT
          README.txt            — human-readable summary

        Args:
            project_data: Project metadata dict.
            songs_data: List of song dicts (may include lyrics).
            audio_paths: Optional list of WAV paths to include.
            midi_paths: Optional list of MIDI paths to include.
            output_path: Destination .sonmancer file.

        Returns:
            ProjectArchiveResult with path and summary.
        """
        name = project_data.get("name", "project").replace(" ", "_")
        if output_path is None:
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"{name}_{ts}.sonmancer")

        included: list[str] = []

        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # Metadata
            manifest = {
                "format": "sonmancer-project",
                "version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                "generator": "Sonmancer Studio v0.7.0",
                "project": project_data,
                "songs": songs_data,
            }
            zf.writestr("project.json", json.dumps(manifest, indent=2, ensure_ascii=False))
            included.append("project.json")

            # Audio
            if audio_paths:
                for path in audio_paths:
                    if os.path.isfile(path):
                        arcname = f"audio/{Path(path).name}"
                        zf.write(path, arcname)
                        included.append(arcname)

            # MIDI
            if midi_paths:
                for path in midi_paths:
                    if os.path.isfile(path):
                        arcname = f"midi/{Path(path).name}"
                        zf.write(path, arcname)
                        included.append(arcname)

            # Lyrics per song
            for song in songs_data:
                lyrics = song.get("lyrics", [])
                if lyrics:
                    txt_lines = [f"[{l.get('section','').upper()}]\n{l.get('text','')}"
                                 for l in sorted(lyrics, key=lambda x: x.get("line_number", 0))]
                    safe_name = song.get("name", "song").replace(" ", "_")
                    arcname = f"lyrics/{safe_name}.txt"
                    zf.writestr(arcname, "\n".join(txt_lines))
                    included.append(arcname)

            # README
            readme = f"""# {project_data.get('name', 'Sonmancer Project')}

Artist: {project_data.get('artist_name', 'Unknown')}
Genre:  {project_data.get('genre', 'Unknown')}
Songs:  {len(songs_data)}
Format: Sonmancer Studio Project Archive v1.0

## Contents
{chr(10).join('  ' + f for f in included)}

## How to Open
Import this .sonmancer file into Sonmancer Studio v0.7.0+
"""
            zf.writestr("README.txt", readme)
            included.append("README.txt")

        size = os.path.getsize(output_path)
        return ProjectArchiveResult(
            path=output_path,
            size_bytes=size,
            included_files=included,
            song_count=len(songs_data),
            export_time=datetime.utcnow().isoformat(),
        )

    # ── Private: ffmpeg ───────────────────────────────────────────────────────

    def _ffmpeg_convert(
        self,
        src: str,
        dst: str,
        fmt: str,
        quality: str,
        metadata: dict,
    ) -> None:
        """Run ffmpeg to convert src → dst with quality preset and metadata tags."""
        if not shutil.which("ffmpeg"):
            raise RuntimeError(
                "ffmpeg not found. Install with:\n"
                "  Ubuntu: sudo apt-get install ffmpeg\n"
                "  macOS:  brew install ffmpeg\n"
                "  Windows: https://ffmpeg.org/download.html"
            )

        # Build quality flags
        quality_flags: list[str] = []
        preset = QUALITY_PRESETS.get(quality, {})
        if fmt in preset:
            quality_flags = preset[fmt].split()

        # Build metadata flags
        meta_flags: list[str] = []
        for key, value in metadata.items():
            meta_flags += ["-metadata", f"{key}={value}"]

        cmd = [
            "ffmpeg", "-y", "-i", src,
            *quality_flags,
            *meta_flags,
            dst,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"ffmpeg conversion failed ({fmt}):\n{result.stderr[-500:]}"
            )

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def check_ffmpeg() -> bool:
        """Return True if ffmpeg is available on the system PATH."""
        return bool(shutil.which("ffmpeg"))

    @staticmethod
    def supported_formats() -> dict:
        """Return all supported formats with metadata."""
        return {
            fmt: {
                "extension":  info["extension"],
                "mime":       info["mime"],
                "needs_ffmpeg": info["ffmpeg"],
            }
            for fmt, info in AUDIO_FORMATS.items()
        }
