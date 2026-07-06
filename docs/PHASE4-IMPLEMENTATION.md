# Somancer Studio — Phase 4 Implementation Guide

**Status:** ✅ Complete  
**Version:** 0.4.0  
**Timeline:** Weeks 15–18

---

## Phase 4 Overview

Phase 4 delivers **Audio Rendering and Playback** — the full pipeline from AI-generated MIDI through FluidSynth synthesis to interactive waveform display and in-app audio playback.

---

## Pipeline

```
AI Composer Agent
      │
      ▼
CompositionResult (notes, tracks, chords)
      │
      ▼  utils/midi_writer.py
MIDI file (.mid)
      │
      ▼  FluidSynth + SF2 soundfont
WAV file (48kHz, 24-bit)
      │
      ▼  audio_service.get_waveform_data()
Peak/RMS arrays → WaveformDisplay SVG
      │
      ▼  PlaybackControls (HTML Audio API)
In-app playback with seek/volume
```

---

## What's New

### Backend

#### `services/audio_service.py`
Full FluidSynth rendering pipeline:

| Method | Purpose |
| --- | --- |
| `render_midi_file(midi, out, sf2)` | MIDI → WAV via FluidSynth CLI |
| `mix_wav_files(paths, out, settings)` | Multi-track mixing with gain/pan |
| `get_waveform_data(wav, num_points)` | Extract peaks + RMS for visualisation |
| `_normalize_wav(path, target_db)` | Peak normalisation to target dBFS |

Graceful dependency detection — raises `RuntimeError` with install instructions if `pyfluidsynth`, `soundfile`, or `numpy` are missing.

#### `schemas/audio.py`
New request/response types:
- `MidiRenderRequest` — composition JSON + render options
- `WaveformResponse` — peaks, RMS, duration, sample rate
- `RenderResultResponse` — render metadata + download URL
- `TrackMixSettingsSchema` — volume, pan, muted, reverb, chorus

#### `api/audio.py` — 4 new endpoints

| Endpoint | Purpose |
| --- | --- |
| `POST /audio/render-midi` | Render CompositionResponse JSON to WAV |
| `GET /audio/waveform/{filename}` | Return peak/RMS data for visualisation |
| `GET /audio/download/{filename}` | Download rendered WAV/FLAC |
| `GET /audio/soundfonts` | List available SF2 files |

#### Tests
- `tests/test_audio.py` — 5 tests (soundfont listing, 404 cases, error handling)
- **Total: 32 tests** (was 27)

---

### Frontend

#### `components/audio/WaveformDisplay.tsx`
SVG waveform renderer:
- Fetches peak data from `/api/v1/audio/waveform/{filename}` or accepts prop peaks
- Colour-splits played vs unplayed regions
- Playback cursor overlay
- Click-to-seek support
- Responsive via SVG `viewBox` + `preserveAspectRatio="none"`

#### `components/audio/PlaybackControls.tsx`
Transport bar built on the browser `Audio` API:
- Play / Pause / Stop buttons
- Seek slider (synced with playback position)
- Volume slider + mute toggle
- Download button (native `<a download>`)
- Emits `onProgressChange` for waveform cursor sync

#### `components/midi/PianoRoll.tsx`
Canvas-based MIDI note editor:
- 128-key piano rail with black/white key colours
- Beat/bar grid with bar numbers ruler
- Draw, Select, Erase tool modes
- Click to add/remove notes (snaps to 0.5 beats)
- Velocity visualised as inner fill bar
- Playback cursor overlay
- Notes colour-coded by selection state
- Scrollable canvas (x + y) via CSS overflow

#### `pages/AudioStudioPage.tsx`
Full-page audio production hub (`/audio`):
1. Left panel — genre, mood, key, BPM, bars → **Generate** button
2. Right panel (tabs):
   - **Piano Roll** — interactive note editor populated from AI
   - **Waveform** — waveform display + playback controls (enabled after render)
3. Header actions — **Export MIDI**, **Render Audio** buttons
4. Chord progression chip row from composition result

**Complete workflow in the UI:**
```
Set params → Generate (AI) → view/edit Piano Roll
→ Render Audio → switch to Waveform tab → play back → download
```

---

## Setup

### Install audio dependencies

```bash
# System — FluidSynth
sudo apt-get install fluidsynth fluid-soundfont-gm    # Ubuntu/Debian
brew install fluid-synth                               # macOS

# Python
pip install pyfluidsynth soundfile numpy scipy midiutil
```

### Verify soundfont

```bash
# List available soundfonts
curl http://localhost:8000/api/v1/audio/soundfonts

# Quick render test
fluidsynth -ni -F /tmp/test.wav /usr/share/sounds/sf2/FluidR3_GM.sf2 test.mid
```

### Full workflow API

```bash
# 1. Generate composition
curl -X POST http://localhost:8000/api/v1/ai/compose \
  -H "Content-Type: application/json" \
  -d '{"genre":"neo-soul","mood":"romantic","key":"Bb Major","bpm":85,"bars":8}' \
  > comp.json

# 2. Export MIDI (optional)
curl -X POST http://localhost:8000/api/v1/export/midi \
  -H "Content-Type: application/json" \
  -d @comp.json -o song.mid

# 3. Render to WAV
curl -X POST http://localhost:8000/api/v1/audio/render-midi \
  -H "Content-Type: application/json" \
  -d "{\"composition\": $(cat comp.json)}" > render.json

# 4. Get waveform data
FILENAME=$(cat render.json | python3 -c "import sys,json; print(json.load(sys.stdin)['wav_path'].split('/')[-1])")
curl "http://localhost:8000/api/v1/audio/waveform/$FILENAME?num_points=500"

# 5. Download the WAV
curl "http://localhost:8000/api/v1/audio/download/$FILENAME" -o output.wav
```

---

## Soundfont Management

Place SF2 files in `packages/backend/soundfonts/`:

```
packages/backend/soundfonts/
├── default.sf2            (auto-detected)
├── FluidR3_GM.sf2
├── GeneralUser.sf2
└── MuseScore_General.sf2
```

The `/audio/soundfonts` endpoint lists all detected fonts. The `render_midi_file` method auto-detects the system font if none is specified.

---

## File Summary

**Backend new files: 3**
- `services/audio_service.py`
- `schemas/audio.py`
- `api/audio.py`
- `tests/test_audio.py`

**Frontend new files: 4**
- `components/audio/WaveformDisplay.tsx`
- `components/audio/PlaybackControls.tsx`
- `components/midi/PianoRoll.tsx`
- `pages/AudioStudioPage.tsx`

**Updated: 3**
- `main.py` (v0.4.0, audio router)
- `App.tsx` (/audio route)
- `Sidebar.tsx` (Audio Studio link)

**Total files: ~155**  
**Total tests: 32**

---

## What's Next (Phase 5)

- **AI Mixing** — analyzes tracks, suggests EQ/compression/panning
- **Mastering pipeline** — Spotify/Apple Music loudness targets
- **VST3/CLAP plugin support** — load third-party instruments
- **Vocal synthesis** — lyrics → phonemes → singing model
- **Stem export** — individual track WAV files
- **Real-time preview** — hot-reload composition while editing

