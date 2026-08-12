# 🎵 Sonmancer Studio

**Cross-platform AI music production environment — v0.8.0**

Sonmancer Studio combines AI songwriting, MIDI composition, vocal synthesis, professional mixing, mastering, and multi-format export into a single offline-capable desktop application.

---

## Features

| Phase | Feature | Status |
| --- | --- | --- |
| 0 | Repository, CI/CD, database, monorepo | ✅ |
| 1 | Projects, songs, tracks, API CRUD | ✅ |
| 2 | Song editor, lyrics, genre browser | ✅ |
| 3 | Ollama AI agents (songwriter, composer, producer, genre researcher) | ✅ |
| 4 | FluidSynth audio rendering, piano roll, waveform, playback | ✅ |
| 5 | AI mixing plans, mastering chains, stem export, vocal TTS | ✅ |
| 6 | Plugin SDK, vocal harmonies (rule-based, 4-part) | ✅ |
| 7 | Multi-format export, project archives, job queue | ✅ |
| 8 | Dark mode, keyboard shortcuts, cache, system API | ✅ |

---

## Technology Stack

| Layer | Technology |
| --- | --- |
| Desktop | Tauri 2 + React 18 + TypeScript |
| Build | Vite |
| UI | Material-UI v5 + Emotion |
| Routing | React Router v6 |
| HTTP client | Axios |
| Backend | FastAPI 0.109 + Python 3.11 |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| AI/LLM | Ollama (local inference) |
| Audio synthesis | FluidSynth + SF2 soundfonts |
| MIDI | midiutil |
| Audio I/O | soundfile + numpy |
| Audio conversion | ffmpeg |
| PDF export | reportlab |
| Testing | pytest + FastAPI TestClient |
| Linting | ESLint + Ruff |
| Formatting | Prettier + Black |
| CI/CD | GitHub Actions |
| Containerisation | Docker + docker-compose |

---

## Quick Start

### Requirements
- Node.js 18+, pnpm
- Python 3.11+
- Rust 1.70+ (for Tauri)
- Ollama (optional, for AI features)
- FluidSynth + SF2 soundfont (optional, for audio)
- ffmpeg (optional, for format conversion)

### Setup

```bash
# Install
npm install -g pnpm
pnpm install

# Run setup script
bash scripts/dev-setup.sh        # Linux/Mac
powershell scripts/dev-setup.ps1  # Windows
```

### Start

```bash
# One command (Linux/Mac)
bash scripts/start-dev.sh

# Or manually
cd packages/backend && source venv/bin/activate
uvicorn aimusic.main:app --reload &

cd packages/desktop
pnpm dev
```

### Verify

```bash
curl http://localhost:8000/api/v1/health
# → {"status":"healthy","version":"0.8.0",...}

open http://localhost:5173
```

---

## Documentation

All guides live in `docs/`:

| File | Topic |
| --- | --- |
| `SETUP.md` | Development environment setup |
| `ARCHITECTURE.md` | System design & data flow |
| `API.md` | REST API reference |
| `CODING_STANDARDS.md` | Code style guide |
| `PHASES.md` | Full 18-phase roadmap |
| `PHASE1-IMPLEMENTATION.md` | Phase 1 details |
| `PHASE2-IMPLEMENTATION.md` | Phase 2 details |
| `PHASE3-IMPLEMENTATION.md` | Phase 3 details |
| `PHASE4-IMPLEMENTATION.md` | Phase 4 details |
| `PHASE5-IMPLEMENTATION.md` | Phase 5 details |
| `PHASE6-IMPLEMENTATION.md` | Phase 6 details |
| `PHASE7-IMPLEMENTATION.md` | Phase 7 details |
| `PHASE8-IMPLEMENTATION.md` | Phase 8 details |

---

## API Endpoints (~76 total)

| Group | Prefix | Endpoints |
| --- | --- | --- |
| Projects | `/api/v1/projects` | 5 |
| Songs | `/api/v1/songs` | 5 |
| Lyrics | `/api/v1/lyrics` | 5 |
| Genres | `/api/v1/genres` | 8 |
| AI Core | `/api/v1/ai` | 7 |
| Audio | `/api/v1/audio` | 4 |
| MIDI Export | `/api/v1/export` | 1 |
| Mixing | `/api/v1/mix` | 9 |
| Plugins | `/api/v1/plugins` | 7 |
| Harmony | `/api/v1/harmony` | 4 |
| Advanced Export | `/api/v1/advanced-export` | 12 |
| System | `/api/v1/system` | 9 |

Swagger UI: `http://localhost:8000/api/v1/docs`

---

## Running Tests

```bash
cd packages/backend
pytest tests/ -v --tb=short
```

**113 tests across 11 test files.**

---

## Project Structure

```
sonmancer-studio/
├── packages/
│   ├── desktop/                    React + Tauri frontend
│   │   └── src/
│   │       ├── components/         Header, Sidebar, Layout, PianoRoll, Waveform
│   │       ├── context/            ProjectContext, ThemeContext
│   │       ├── hooks/              useAI, useProjects, useKeyboardShortcuts
│   │       ├── pages/              12 pages (Dashboard → Export → Settings)
│   │       ├── services/           api, projectService, aiService, ...
│   │       ├── types/              TypeScript interfaces
│   │       └── utils/              formatters, constants
│   ├── backend/                    FastAPI backend
│   │   └── aimusic/
│   │       ├── api/                12 API routers
│   │       ├── services/           Core services + AI agents
│   │       │   └── agents/         7 AI agents (songwriter, composer, ...)
│   │       ├── models/             14 SQLAlchemy entities
│   │       ├── schemas/            Pydantic validation
│   │       └── utils/              MIDI writer, audio helpers, seed data
│   └── shared/                     Shared TypeScript types
├── docs/                           13 guides
├── docker/                         Backend Dockerfile
├── .github/workflows/              CI/CD
└── scripts/                        dev-setup, start-dev, seed-genres
```

---

## License

 PolyForm Noncommercial License 1.0.0 — see [`LICENSE`](https://github.com/bbbbbb12331314141414141/somancer-studio/blob/main/LICENSE)
