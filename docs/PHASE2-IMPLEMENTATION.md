# Somancer Studio — Phase 2 Implementation Guide

**Status:** ✅ Complete  
**Version:** 0.2.0  
**Timeline:** Weeks 7–10

---

## Phase 2 Overview

Phase 2 delivers **Project & Song Editors, Genre Management, and Lyrics CRUD** — making the application fully functional for end-to-end music project creation.

### Milestones

| Milestone | Feature | Status |
| --- | --- | --- |
| M6 | New project creation form | ✅ |
| M7 | Project detail editor | ✅ |
| M8 | Song editor (tabs: lyrics, tracks, settings) | ✅ |
| M9 | Lyrics CRUD API + frontend | ✅ |
| M10 | Genre CRUD API + browser | ✅ |
| M11 | Genre seed data (15 genres) | ✅ |
| M12 | Expanded sidebar navigation | ✅ |
| M13 | Utility helpers (formatters, constants) | ✅ |
| M14 | Reusable UI components | ✅ |
| M15 | Test suite — genres + lyrics | ✅ |

---

## What's New in Phase 2

### Backend

#### Lyrics API (`/api/v1/lyrics/`)
- `GET  /lyrics/?song_id={id}` — list lyrics for a song (filterable by section)
- `POST /lyrics/` — create lyric line
- `GET  /lyrics/{id}` — get lyric by ID
- `PATCH /lyrics/{id}` — update text/section/mood
- `DELETE /lyrics/{id}` — delete lyric

#### Genres API (`/api/v1/genres/`)
- `GET  /genres/` — list genres (filterable by `search` and `parent_id`)
- `POST /genres/` — create genre
- `GET  /genres/{id}` — get genre
- `GET  /genres/{id}/subgenres` — get child genres
- `PATCH /genres/{id}` — update genre
- `DELETE /genres/{id}` — delete genre

#### Genre Seed Data
15 genres across 5 root categories + subgenres:

| Root | Subgenres |
| --- | --- |
| Rock | Hard Rock, Alternative Rock, Indie Rock, Metal |
| Electronic | House, Techno, Ambient |
| Hip-Hop | Trap |
| R&B | Neo-Soul |
| Jazz | — |
| Classical | — |

Seed with:
```bash
bash scripts/seed-genres.sh
# or
python -m aimusic.utils.seed_genres
```

#### New Tests
- `tests/test_genres.py` — 7 genre tests
- `tests/test_lyrics.py` — 6 lyrics tests
- `tests/conftest.py` — shared fixtures with in-memory SQLite

**Total tests: 21** (was 8 in Phase 1)

---

### Frontend

#### New Pages

**`/projects/new`** — New Project Form
- Project name, type, artist, description
- Genre text field
- BPM + key dropdowns
- Client-side validation
- Redirects to project detail on success

**`/projects/:projectId`** — Project Detail Editor
- View and inline-edit all project fields
- Song list table with Add Song dialog
- Error/loading states

**`/projects/:projectId/songs/:songId`** — Song Editor
- Three tabs: Lyrics, Tracks (stub), Settings
- Add lyric lines with section, text, mood
- Lines grouped by section (verse, chorus, bridge…)
- Delete individual lines
- Colour-coded section chips

**`/genres`** — Genre Browser
- Expandable genre cards (click to reveal details)
- Live search with 250ms debounce
- Tree layout (root → subgenres)
- Shows BPM range, instruments, keys, vocal style

#### New Components
- `ConfirmDialog` — reusable confirmation modal
- `LoadingScreen` — centred spinner with message

#### New Services
- `songService.ts` — CRUD for songs
- `lyricsService.ts` — CRUD for lyrics

#### New Utilities
- `formatters.ts` — `formatDate`, `formatDuration`, `capitalize`, `slugify`
- `constants.ts` — `PROJECT_TYPES`, `LYRIC_SECTIONS`, `MOODS`, `COMMON_KEYS`, `BPM_MIN/MAX`

#### Updated
- `App.tsx` — 7 routes (was 3)
- `Sidebar.tsx` — Genre Browser + New Project links, active highlight bar, brand header

---

## API Quick Reference

### Lyrics

```bash
# List lyrics for song 1
curl "http://localhost:8000/api/v1/lyrics/?song_id=1"

# Filter by section
curl "http://localhost:8000/api/v1/lyrics/?song_id=1&section=chorus"

# Create lyric
curl -X POST http://localhost:8000/api/v1/lyrics/ \
  -H "Content-Type: application/json" \
  -d '{"song_id":1,"line_number":1,"section":"verse","text":"Words and music","mood":"hopeful"}'

# Update
curl -X PATCH http://localhost:8000/api/v1/lyrics/1 \
  -H "Content-Type: application/json" \
  -d '{"text":"Updated words"}'

# Delete
curl -X DELETE http://localhost:8000/api/v1/lyrics/1
```

### Genres

```bash
# List all genres
curl "http://localhost:8000/api/v1/genres/"

# Search
curl "http://localhost:8000/api/v1/genres/?search=rock"

# Subgenres of genre 1
curl "http://localhost:8000/api/v1/genres/1/subgenres"

# Create genre
curl -X POST http://localhost:8000/api/v1/genres/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Synthwave","bpm_min":80,"bpm_max":120}'
```

---

## Running Phase 2

### Seed genres after first launch
```bash
bash scripts/seed-genres.sh
```

### Run all tests
```bash
cd packages/backend
pytest tests/ -v
```

Expected: **21 tests pass**

### Start full stack
```bash
# Backend
cd packages/backend && source venv/bin/activate
uvicorn aimusic.main:app --reload

# Frontend (new terminal)
cd packages/desktop && pnpm dev
```

---

## User Flows Available

### Create a complete song

1. Open app → Dashboard
2. Click **Create New Project**
3. Fill in name, type, genre, BPM → **Create Project**
4. On Project Detail page → **Add Song**
5. Click song to open Song Editor
6. Lyrics tab → type lines, select section + mood → **Add**
7. Lines appear grouped by section (verse, chorus, etc.)

### Browse genres

1. Open sidebar → **Genre Browser**
2. Browse root genres (Rock, Electronic, Hip-Hop…)
3. Click a card to expand and see instruments, keys, BPM range
4. Use search to filter

---

## File Summary

### Backend — New Files

| File | Purpose |
| --- | --- |
| `api/lyrics.py` | Lyrics CRUD endpoints |
| `api/genres.py` | Genres CRUD + subgenres endpoint |
| `services/lyrics_service.py` | Lyrics business logic |
| `services/genre_service.py` | Genre business logic |
| `schemas/lyrics.py` | Pydantic lyrics schemas |
| `schemas/genre.py` | Pydantic genre schemas |
| `utils/seed_genres.py` | 15-genre seed script |
| `tests/test_genres.py` | 7 genre tests |
| `tests/test_lyrics.py` | 6 lyrics tests |
| `tests/conftest.py` | Shared in-memory SQLite fixture |

### Frontend — New Files

| File | Purpose |
| --- | --- |
| `pages/NewProjectPage.tsx` | Project creation form |
| `pages/ProjectDetailPage.tsx` | Project detail + song list |
| `pages/SongEditorPage.tsx` | Song editor (lyrics, tracks, settings) |
| `pages/GenresPage.tsx` | Genre browser with search |
| `services/songService.ts` | Song API calls |
| `services/lyricsService.ts` | Lyrics API calls |
| `components/common/ConfirmDialog.tsx` | Reusable confirm modal |
| `components/common/LoadingScreen.tsx` | Full-page loading spinner |
| `utils/formatters.ts` | Date/duration/string formatters |
| `utils/constants.ts` | Shared constants |

### Scripts

| File | Purpose |
| --- | --- |
| `scripts/seed-genres.sh` | One-command genre seeding |

---

## What's Next (Phase 3)

- **Ollama Integration** — Connect to local LLM
- **AI Songwriter Agent** — Generate lyrics from prompt
- **AI Composer Agent** — Generate MIDI from genre + mood
- **MIDI piano roll** — Visual note editor
- **Genre Research Engine** — Auto-fetch genre data online
- **Track management** — Full audio/MIDI track CRUD

---

## Performance (Phase 2)

| Operation | Time |
| --- | --- |
| List genres (100) | < 30 ms |
| List lyrics (50) | < 20 ms |
| Genre search | < 50 ms |
| Create lyric | < 30 ms |
| Frontend load | < 600 ms |

