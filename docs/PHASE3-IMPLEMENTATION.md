# Somancer Studio — Phase 3 Implementation Guide

**Status:** ✅ Complete  
**Version:** 0.3.0  
**Timeline:** Weeks 11–14

---

## Phase 3 Overview

Phase 3 delivers the **AI Core** — Ollama integration, three specialized AI agents, and a complete AI Studio UI. The app can now generate lyrics, compose MIDI, create song briefs, and research genre characteristics entirely offline.

---

## Architecture: Multi-Agent System

```
                  ┌─────────────────────┐
                  │   Ollama (local LLM) │
                  │  mistral / gemma2 /  │
                  │  llama3.2 / qwen2.5  │
                  └──────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
     ┌──────────────┐  ┌──────────┐  ┌──────────────┐
     │  Songwriter  │  │ Composer │  │   Producer   │
     │    Agent     │  │  Agent   │  │    Agent     │
     └──────────────┘  └──────────┘  └──────────────┘
              ↓              ↓
     ┌──────────────┐  ┌──────────────┐
     │   Lyrics     │  │  MIDI Data   │
     │  (text)      │  │  (notes)     │
     └──────────────┘  └──────────────┘
                                ↓
                       ┌──────────────┐
                       │  MIDI Writer  │
                       │  (.mid file) │
                       └──────────────┘
```

---

## What's New

### Backend

#### New Files

| File | Purpose |
| --- | --- |
| `services/ollama_service.py` | Ollama HTTP client (generate, stream, chat, model mgmt) |
| `services/agents/__init__.py` | Agent package |
| `services/agents/base_agent.py` | Shared agent logic (JSON parsing, prompt helpers) |
| `services/agents/songwriter_agent.py` | Lyrics generation, rewriting, continuation |
| `services/agents/composer_agent.py` | MIDI composition, chord progressions, arrangement |
| `services/agents/producer_agent.py` | Song briefs, lyrics review |
| `services/agents/genre_researcher_agent.py` | Genre musical profiling, comparison |
| `schemas/ai.py` | Pydantic schemas for all AI endpoints |
| `api/ai.py` | AI API router (lyrics, compose, brief, chords, models) |
| `api/export.py` | MIDI file export endpoint |
| `utils/midi_writer.py` | Convert CompositionResult → .mid bytes |
| `tests/test_ai.py` | 6 AI endpoint tests (mocked Ollama) |

#### New API Endpoints

**AI Core (`/api/v1/ai/`)**
```
GET  /ai/health              — Ollama availability + model count
GET  /ai/models              — List locally pulled Ollama models
POST /ai/models/{name}/pull  — Pull a model from Ollama registry
POST /ai/lyrics              — Generate lyrics (Songwriter Agent)
POST /ai/compose             — Generate MIDI (Composer Agent)
POST /ai/brief               — Generate song brief (Producer Agent)
GET  /ai/chords              — Generate chord progression
```

**Export (`/api/v1/export/`)**
```
POST /export/midi            — Compose + return downloadable .mid file
```

**Genre Research (added to `/api/v1/genres/`)**
```
POST /genres/{id}/research   — Enrich genre with AI research
GET  /genres/research/compare — Compare two genres
```

#### Agents

**SongwriterAgent**
- `generate_lyrics(params)` → `list[LyricLine]`
- `continue_lyrics(existing, params)` → `list[LyricLine]`
- `rewrite_lyrics(original, mood, vocabulary, genre)` → `list[LyricLine]`
- Supports: section, count, genre, mood, theme, vocabulary, perspective, language, length, rhyme

**ComposerAgent**
- `compose(params)` → `CompositionResult` (multi-track MIDI data)
- `generate_chord_progression(key, genre, mood, bars)` → `list[str]`
- `suggest_arrangement(genre, mood, duration_bars)` → `list[dict]`
- Auto-generates: plan → melody → bass → drums

**ProducerAgent**
- `create_song_brief(genre, mood, theme, target_audience)` → `SongBrief`
- `review_lyrics(lyrics, genre, mood)` → `dict` (score + suggestions)

**GenreResearcherAgent**
- `research_genre(name)` → `GenreProfile`
- `suggest_related_genres(name)` → `list[str]`
- `compare_genres(a, b)` → `dict`

**BaseAgent**
- JSON extraction with markdown fence stripping + regex fallback
- Retry logic (configurable, default 2 retries)
- Prompt context builder

#### MIDI Writer

`utils/midi_writer.py` converts a `CompositionResult` to standard MIDI bytes using `midiutil`.

```python
from aimusic.utils.midi_writer import composition_to_midi_bytes, save_midi_file

# In memory
midi_bytes = composition_to_midi_bytes(result)

# To disk
path = save_midi_file(result, "/exports/song.mid")
```

Requires: `pip install midiutil`

---

### Frontend

#### New Files

| File | Purpose |
| --- | --- |
| `pages/AIStudioPage.tsx` | Full AI Studio: 3 tabs (Lyrics, Composition, Song Brief) |
| `services/aiService.ts` | All AI API calls typed and centralised |
| `hooks/useAI.ts` | useAI hook with loading/error state |
| `hooks/useProjects.ts` | Re-export for consistent hook imports |

#### AI Studio Page (`/ai`)

**Tab 1 — Lyrics Generator**
- Sidebar: section, genre, mood, theme, count, model selector
- Real-time results with section chips and mood labels
- Powered by SongwriterAgent via `POST /ai/lyrics`

**Tab 2 — Composition**
- Sidebar: genre, mood, key, BPM slider, bars slider
- Results: tempo, key, chord progression chips, track list
- Powered by ComposerAgent via `POST /ai/compose`

**Tab 3 — Song Brief**
- Input: genre
- Results: suggested title, BPM, key, structure, instruments, production notes
- Powered by ProducerAgent via `POST /ai/brief`

**Ollama status badge** in header — click "Check Ollama" to verify connectivity.

---

## Setup & Usage

### 1. Start Ollama

```bash
# Install from https://ollama.ai
ollama serve

# Pull a model (mistral recommended)
ollama pull mistral
# or
ollama pull gemma2
ollama pull llama3.2
```

### 2. Install optional MIDI dependency

```bash
pip install midiutil
```

### 3. Start backend

```bash
cd packages/backend
source venv/bin/activate
uvicorn aimusic.main:app --reload
```

### 4. Use AI endpoints

```bash
# Check Ollama status
curl http://localhost:8000/api/v1/ai/health

# List available models
curl http://localhost:8000/api/v1/ai/models

# Generate lyrics
curl -X POST http://localhost:8000/api/v1/ai/lyrics \
  -H "Content-Type: application/json" \
  -d '{
    "section": "chorus",
    "count": 4,
    "genre": "neo-soul",
    "mood": "romantic",
    "theme": "late night city",
    "rhyme": true,
    "model": "mistral"
  }'

# Generate chord progression
curl "http://localhost:8000/api/v1/ai/chords?key=C+Minor&genre=neo-soul&mood=romantic&bars=4"

# Create song brief
curl -X POST http://localhost:8000/api/v1/ai/brief \
  -H "Content-Type: application/json" \
  -d '{"genre": "jazz", "mood": "melancholic"}'

# Export MIDI
curl -X POST http://localhost:8000/api/v1/export/midi \
  -H "Content-Type: application/json" \
  -d '{"genre":"pop","mood":"happy","key":"G Major","bpm":120,"bars":8}' \
  --output composition.mid
```

---

## Running Tests

```bash
cd packages/backend
pytest tests/ -v
```

**Expected: 27 tests pass** (was 21 in Phase 2)

Tests include mocked Ollama — no real Ollama needed for the test suite.

---

## Model Recommendations

| Model | Size | Best for |
| --- | --- | --- |
| `mistral` | 4.1 GB | General text, lyrics (best balance) |
| `gemma2` | 5.4 GB | Creative writing, strong poetry |
| `llama3.2` | 2.0 GB | Fast generation, smaller RAM |
| `qwen2.5` | 4.7 GB | Multi-language lyrics |
| `deepseek-r1` | 4.7 GB | Logical composition planning |

```bash
ollama pull mistral    # Recommended first
ollama pull gemma2     # Best for creative lyrics
```

---

## JSON Robustness

BaseAgent handles common Ollama response issues:
- Strips ```` ```json ```` markdown fences
- Regex-extracts first `{...}` or `[...]` block if direct parse fails
- Retries up to 2 times with fresh generation on failure
- Logs each attempt for debugging

---

## File Summary

**Backend new files: 12**  
**Frontend new files: 4**  
**New API endpoints: 10**  
**Total tests: 27** (was 21)  
**Total files: ~145**

---

## What's Next (Phase 4)

- **FluidSynth integration** — render MIDI tracks to audio using SF2 soundfonts
- **Audio mixer** — volume, pan, EQ per track
- **Piano roll UI** — visual MIDI note editor
- **Waveform display** — rendered audio visualisation
- **Track playback** — in-app audio preview
- **Stem export** — individual track WAV files

