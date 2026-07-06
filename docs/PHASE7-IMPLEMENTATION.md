# Somancer Studio — Phase 7 Implementation Guide

**Status:** ✅ Complete  
**Version:** 0.7.0  
**Timeline:** Weeks 27–30

---

## Phase 7 Overview

Phase 7 delivers **Advanced Export Formats, Project Archives, and a Background Job Queue** — completing the production pipeline from AI composition through platform-ready delivery.

---

## What's New

### Backend

#### `services/export_service.py` — Advanced Multi-Format Export

| Method | Purpose |
| --- | --- |
| `convert_audio(wav, fmt, quality)` | WAV → MP3/FLAC/OGG/AAC/AIFF via ffmpeg |
| `batch_export(wav, formats, quality)` | Export to multiple formats simultaneously |
| `export_stems_zip(stems, name)` | Bundle stem WAVs into a single ZIP |
| `export_lyrics_txt(lyrics, name)` | Lyrics as plain text |
| `export_lyrics_pdf(lyrics, name)` | Formatted PDF with sections (requires reportlab) |
| `export_project_archive(project, songs)` | Full `.sonmancer` ZIP archive |
| `supported_formats()` | All formats with MIME types |
| `check_ffmpeg()` | Returns True if ffmpeg on PATH |

**Supported formats:**

| Format | Extension | Requires |
| --- | --- | --- |
| WAV | .wav | Nothing (copy) |
| FLAC | .flac | ffmpeg |
| MP3 | .mp3 | ffmpeg |
| OGG Vorbis | .ogg | ffmpeg |
| AAC | .aac | ffmpeg |
| AIFF | .aiff | ffmpeg |

**Quality presets:**
- `lossless` — FLAC level 8
- `hq` — MP3 320kbps / OGG Q9 / AAC 256kbps
- `standard` — MP3 192kbps / OGG Q6 / AAC 128kbps
- `low` — MP3 128kbps / OGG Q3 / AAC 96kbps

**`.sonmancer` Project Archive contents:**
```
project.json      ← metadata (project + songs)
audio/            ← rendered WAV files
midi/             ← MIDI compositions
lyrics/           ← per-song TXT files
README.txt        ← human-readable summary
```

---

#### `services/job_queue.py` — Background Job Queue

Thread-safe in-process job queue for long-running operations.

**Job lifecycle:** `PENDING → RUNNING → COMPLETED | FAILED | CANCELLED`

```python
queue = get_job_queue()

# Submit a job
job = queue.submit(
    job_type="export",
    fn=lambda job: do_work(job),   # job.progress = 0.0–1.0
    metadata={"song_id": 42}
)

# Poll for result
job = queue.get(job.id)
if job.status == JobStatus.COMPLETED:
    print(job.result)

# Cancel a pending/running job
queue.cancel(job.id)

# Stats
print(queue.stats)  # {"total": 5, "completed": 4, "failed": 1, ...}
```

**Phase 7:** Thread-based (4 workers).  
**Phase 8+:** Drop-in replacement with Celery + RabbitMQ for scale.

---

#### `api/advanced_export.py` — 12 new endpoints

**Format info:**
```
GET  /advanced-export/formats           ← supported formats + ffmpeg status
```

**Audio:**
```
POST /advanced-export/audio/convert     ← WAV → any format
POST /advanced-export/audio/batch       ← WAV → multiple formats at once
```

**Export:**
```
POST /advanced-export/stems-zip         ← bundle stems into ZIP
POST /advanced-export/lyrics/txt        ← lyrics as TXT
POST /advanced-export/lyrics/pdf        ← lyrics as PDF (reportlab)
POST /advanced-export/project-archive   ← full .sonmancer archive
```

**Jobs:**
```
GET  /advanced-export/jobs              ← list recent jobs
GET  /advanced-export/jobs/{id}         ← get job by ID
POST /advanced-export/jobs/{id}/cancel  ← cancel a job
POST /advanced-export/jobs/clear        ← remove old completed jobs
GET  /advanced-export/jobs/stats/summary ← queue statistics
```

---

#### Tests

- `tests/test_export_service.py` — 16 tests:
  - Format registry, ffmpeg detection
  - Lyrics TXT and empty export
  - Stems ZIP with valid WAVs
  - Project archive (JSON, README, audio inclusion)
  - WAV copy (no ffmpeg needed)
  - Invalid format + missing file error handling

- Job queue tests (within same file) — 6 tests:
  - Submit and complete
  - Failed job error capture
  - Job listing with filters
  - Cancellation
  - Stats
  - Clear completed

- **Total: 92 tests** (was 76)

---

### Frontend

#### `ExportPage` (`/export`) — 4 tabs:

**Tab 1 — Audio**
- Enter source WAV path
- Select target format (chips show ffmpeg requirement status)
- Select quality preset
- Convert → download link

**Tab 2 — Lyrics**
- Song name + artist name inputs
- Format selector (TXT / PDF)
- Multi-line lyrics textarea
- Export → download link

**Tab 3 — Project**
- Project JSON editor (manual/paste)
- Archive info panel listing ZIP contents
- Create Archive → download .sonmancer link

**Tab 4 — Jobs**
- Live job list with status icons + progress bars
- Refresh and Clear Completed buttons
- Queue stats chips (total/pending/running/done/failed)

---

## API Quick Reference

```bash
# Supported formats
curl http://localhost:8000/api/v1/advanced-export/formats

# Convert WAV to MP3
curl -X POST http://localhost:8000/api/v1/advanced-export/audio/convert \
  -H "Content-Type: application/json" \
  -d '{"source_wav": "/exports/render.wav", "target_format": "mp3", "quality": "hq"}'

# Batch export to multiple formats
curl -X POST http://localhost:8000/api/v1/advanced-export/audio/batch \
  -H "Content-Type: application/json" \
  -d '{"source_wav": "/exports/render.wav", "formats": ["mp3","flac","ogg"], "quality": "hq"}'

# Export lyrics as PDF
curl -X POST http://localhost:8000/api/v1/advanced-export/lyrics/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics": [
      {"line_number": 1, "section": "verse", "text": "I wander through the night"},
      {"line_number": 2, "section": "chorus", "text": "And feel alive"}
    ],
    "song_name": "Night Sky",
    "artist_name": "Sonmancer"
  }'

# Create project archive
curl -X POST http://localhost:8000/api/v1/advanced-export/project-archive \
  -H "Content-Type: application/json" \
  -d '{"project": {"name": "My Album", "artist_name": "Artist"}, "songs": []}'

# Job queue stats
curl http://localhost:8000/api/v1/advanced-export/jobs/stats/summary
```

---

## Installation Requirements

```bash
# ffmpeg (for MP3/FLAC/OGG/AAC/AIFF)
sudo apt-get install ffmpeg          # Ubuntu/Debian
brew install ffmpeg                  # macOS

# reportlab (for PDF lyrics/chord charts)
pip install reportlab

# Verify
ffmpeg -version
python3 -c "import reportlab; print('reportlab OK')"
```

---

## File Summary

| File | Type | New/Updated |
| --- | --- | --- |
| `services/export_service.py` | Backend | New |
| `services/job_queue.py` | Backend | New |
| `api/advanced_export.py` | Backend | New |
| `main.py` | Backend | Updated (v0.7.0) |
| `tests/test_export_service.py` | Backend | New (22 tests) |
| `pages/ExportPage.tsx` | Frontend | New |
| `App.tsx` | Frontend | Updated (/export) |
| `Sidebar.tsx` | Frontend | Updated (v0.7.0) |

**Total new files: 6**  
**Total files: ~185**  
**Total tests: 92**  
**Total API endpoints: ~67**

---

## What's Next (Phase 8: Stable v0.9 / v1.0)

- **Performance optimisation** — SQLAlchemy query caching, response compression
- **Dark mode** — MUI theme toggle (light/dark/system)
- **Keyboard shortcuts** — global hotkeys for playback, export, navigation
- **Accessibility** — ARIA labels, screen reader support, focus management
- **Cross-platform testing** — Windows 11 + Ubuntu 24.04 + macOS 14 verified builds
- **Documentation site** — Docusaurus/MkDocs user and developer guides
- **Plugin marketplace** — browse and install community plugins
- **Error reporting** — structured error logging + crash report export

