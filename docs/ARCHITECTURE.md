# Sonmancer Studio — System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TAURI DESKTOP (React)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Dashboard | Project | Lyrics | Composition | Mixer      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          ↕ HTTP/IPC                             │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (Python)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ┌─────────────┐  ┌────────────┐  ┌──────────────────┐   │   │
│  │ │ Project Svc │  │  AI Svc    │  │  Audio Svc       │   │   │
│  │ └─────────────┘  └────────────┘  └──────────────────┘   │   │
│  │ ┌─────────────┐  ┌────────────┐  ┌──────────────────┐   │   │
│  │ │ Plugin Svc  │  │ Export Svc │  │  Database Svc    │   │   │
│  │ └─────────────┘  └────────────┘  └──────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                    ↕           ↕           ↕                    │
└─────────────────────────────────────────────────────────────────┘
         │                  │                  │
         ↓                  ↓                  ↓
    ┌─────────┐      ┌──────────┐      ┌─────────────┐
    │ SQLite  │      │  Ollama  │      │ File System │
    │Database │      │  Models  │      │(MIDI/Audio) │
    └─────────┘      └──────────┘      └─────────────┘
```

---

## Layered Architecture

### Presentation Layer (Frontend)
- **Framework:** Tauri 2 + React 18 + TypeScript
- **Responsibilities:**
  - User interface rendering
  - User input handling
  - State management (React Context or Redux)
  - API communication via Axios
  - File dialog integration with Tauri
  - Audio playback visualization

- **Key Pages:**
  - Dashboard (recent projects, statistics)
  - Project creation/management
  - Song editor (multi-track view)
  - Lyrics editor
  - MIDI composition
  - Mix console
  - Settings (audio, UI, models)
  - Model manager
  - Plugin manager

### API Layer (Backend)
- **Framework:** FastAPI + Uvicorn
- **Responsibilities:**
  - HTTP request routing
  - Request validation (Pydantic)
  - Authentication/authorization (future)
  - Error handling and logging
  - Rate limiting (future)
  - API versioning (/api/v1/)

- **Endpoints:**
  - `/api/v1/projects/*` — Project CRUD
  - `/api/v1/songs/*` — Song management
  - `/api/v1/tracks/*` — Track management
  - `/api/v1/lyrics/*` — Lyrics operations
  - `/api/v1/genres/*` — Genre database
  - `/api/v1/ai/...` — AI agent endpoints
  - `/api/v1/models/*` — Model management
  - `/api/v1/jobs/*` — Job queue
  - `/api/v1/export/*` — Export operations
  - `/api/v1/audio/*` — Audio rendering

### Service Layer (Business Logic)
- **Project Service:** Project lifecycle management
- **AI Service:** Ollama integration, agent coordination
- **Audio Service:** Rendering, mixing, effects
- **Database Service:** SQLAlchemy ORM, migrations
- **Plugin Service:** Plugin loading, lifecycle
- **Export Service:** WAV, MP3, FLAC, stems export
- **Job Service:** Background task queue

### Data Access Layer (Database)
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Database:** SQLite (dev), PostgreSQL (production-ready)

- **Core Entities:**
  - Projects (albums, EPs, singles, demos)
  - Songs
  - Tracks (audio/MIDI)
  - Lyrics
  - Genres
  - AI Conversations
  - Jobs (background tasks)
  - Exports
  - Plugins
  - Settings
  - History (undo/redo)

### External Integrations
- **Ollama:** Local LLM inference (text generation, planning)
- **File System:** MIDI files, audio files, project archives
- **Audio Libraries:**
  - librosa (analysis)
  - SoundFile (I/O)
  - scipy (DSP)
  - FluidSynth (instrument rendering)

---

## Data Flow Examples

### Creating a Song from Scratch

```
User Input (Desktop UI)
    ↓
React Component State Update
    ↓
POST /api/v1/songs (with project_id, name, genre)
    ↓
FastAPI Endpoint
    ↓
Pydantic Validation
    ↓
Project Service (check project exists)
    ↓
Database Service (insert Song record)
    ↓
Return JSON response
    ↓
React Component Updates, Re-render
    ↓
Dashboard shows new song in project
```

### Generating Lyrics

```
User enters: "Genre: Neo-Soul, Theme: love, Mood: romantic"
    ↓
POST /api/v1/ai/lyrics (with parameters)
    ↓
AI Service routes to "Songwriter" agent
    ↓
Songwriter Agent queries Ollama with specialized prompt
    ↓
Ollama inference (Mistral/Llama)
    ↓
Response parsed, structured into verse/chorus/bridge
    ↓
Lyrics Service inserts into database
    ↓
Stream response back to frontend
    ↓
React component renders generated lyrics with edit UI
    ↓
User can accept, regenerate, or manually edit
```

### Rendering Audio

```
User clicks "Render"
    ↓
POST /api/v1/jobs (job_type: render, song_id: X)
    ↓
Job Service creates Job record (status: PENDING)
    ↓
Background worker picks up job
    ↓
Audio Service loads:
  - MIDI tracks
  - SF2 soundfonts
  - Audio tracks
  - Mixing parameters
    ↓
FluidSynth synthesizes MIDI → audio
    ↓
Audio mixing pipeline:
  1. Load all tracks
  2. Apply gain/pan/effects
  3. Mix down to stereo
  4. Normalize
    ↓
Write WAV to disk
    ↓
Job record updated (status: COMPLETED, result_path: ...)
    ↓
Frontend polls /api/v1/jobs/{job_id}, detects completion
    ↓
Desktop UI enables "Play" button with rendered audio
```

---

## File Organization

```
sonmancer-studio/
├── packages/
│   ├── desktop/
│   │   ├── src/
│   │   │   ├── components/       # React components
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── ProjectEditor.tsx
│   │   │   │   ├── MixConsole.tsx
│   │   │   │   └── ...
│   │   │   ├── pages/            # Page components
│   │   │   ├── hooks/            # Custom React hooks
│   │   │   ├── services/         # API clients
│   │   │   ├── types/            # TypeScript types (shared with backend)
│   │   │   ├── utils/            # Utility functions
│   │   │   ├── App.tsx           # Root component
│   │   │   └── main.tsx          # Entry point
│   │   ├── src-tauri/
│   │   │   └── tauri.conf.json   # Tauri config
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── tsconfig.json
│   │
│   ├── backend/
│   │   ├── aimusic/
│   │   │   ├── api/              # API routes
│   │   │   │   ├── projects.py
│   │   │   │   ├── songs.py
│   │   │   │   ├── ai.py
│   │   │   │   ├── audio.py
│   │   │   │   └── ...
│   │   │   ├── services/         # Business logic
│   │   │   │   ├── project.py
│   │   │   │   ├── ai.py
│   │   │   │   ├── audio.py
│   │   │   │   ├── plugin.py
│   │   │   │   └── ...
│   │   │   ├── models/           # SQLAlchemy ORM models
│   │   │   ├── schemas/          # Pydantic request/response schemas
│   │   │   ├── utils/            # Helper functions
│   │   │   ├── db.py             # Database connection
│   │   │   ├── config.py         # Configuration
│   │   │   └── main.py           # FastAPI app entry point
│   │   ├── tests/                # Pytest test suites
│   │   ├── migrations/           # Alembic database migrations
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   └── shared/
│       ├── src/
│       │   ├── types/            # TypeScript interfaces
│       │   └── enums/            # Shared enums
│       ├── package.json
│       └── tsconfig.json
│
├── docker/
│   ├── backend.Dockerfile
│   └── ollama.Dockerfile (optional)
│
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── build.yml
│       └── release.yml
│
├── docs/
│   ├── ARCHITECTURE.md (this file)
│   ├── SETUP.md
│   ├── API.md
│   ├── CODING_STANDARDS.md
│   ├── DATABASE.md
│   └── PHASES.md
│
├── scripts/
│   ├── dev-setup.sh
│   ├── dev-setup.ps1
│   └── migrate-db.sh
│
├── docker-compose.yml
├── pnpm-workspace.yaml
├── package.json
├── .eslintrc.json
├── .prettierrc.json
├── .editorconfig
├── .gitignore
├── .env.example
└── README.md
```

---

## Technology Stack

| Component | Technology | Rationale |
| --- | --- | --- |
| Desktop | Tauri 2 + React 18 | Small binary size, web tech, native performance |
| Frontend Build | Vite | Fast HMR, ESM native, minimal config |
| Styling | Material-UI + Emotion | Themeable, accessible, battle-tested |
| Frontend Lang | TypeScript | Type safety, dev experience |
| Backend | FastAPI | Modern, fast, async-first, auto-docs |
| Backend Lang | Python 3.11 | Rich ecosystem (audio, AI, ML) |
| ORM | SQLAlchemy 2.0 | Flexible, powerful, migrations via Alembic |
| Database | SQLite (dev), PostgreSQL (prod) | Serverless for dev, scalable for prod |
| Validation | Pydantic v2 | Best-in-class schema validation |
| Task Queue | Built-in + threading (Phase 1) | Celery/RQ later if needed |
| Audio Synthesis | FluidSynth + SF2 | GPL-friendly, multi-platform, mature |
| AI/LLM | Ollama | Local inference, privacy, offline-capable |
| Testing | pytest (Python), Vitest (TS) | Industry standard, good DX |
| Linting | ESLint, Ruff | Consistent code quality |
| Formatting | Prettier, Black | Automatic style enforcement |
| CI/CD | GitHub Actions | Native to GitHub, free for public repos |
| Containerization | Docker + docker-compose | Reproducible dev environment |

---

## API Communication

### Request/Response Pattern

**Request:**
```json
POST /api/v1/songs
Content-Type: application/json

{
  "name": "Lost in the Night",
  "project_id": 1,
  "bpm": 85,
  "key": "Cm"
}
```

**Response:**
```json
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 42,
  "name": "Lost in the Night",
  "project_id": 1,
  "bpm": 85,
  "key": "Cm",
  "created_at": "2024-06-29T14:23:00Z",
  "updated_at": "2024-06-29T14:23:00Z"
}
```

### Error Handling

**Bad Request:**
```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "validation_error",
  "details": [
    {
      "field": "name",
      "message": "Name must be between 1 and 255 characters"
    }
  ]
}
```

**Server Error:**
```json
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "request_id": "req_abc123"
}
```

---

## State Management (Frontend)

### Approach
- React Context API for global state (projects, settings)
- Component local state for UI-only state (dialogs, menus)
- Custom hooks for complex logic
- Future: Redux if state grows unmanageable

### Example Context

```typescript
// src/context/ProjectContext.tsx
interface ProjectContextType {
  currentProject: Project | null;
  projects: Project[];
  createProject: (data: CreateProjectInput) => Promise<Project>;
  updateProject: (id: number, data: UpdateProjectInput) => Promise<void>;
  deleteProject: (id: number) => Promise<void>;
}

export const ProjectContext = createContext<ProjectContextType>(...);
```

---

## Security Considerations

### Phase 0 (Development)
- SQLite with no auth (fine for local dev)
- CORS open to localhost only
- No authentication required
- Environment variables for secrets

### Phase 1+
- User authentication (JWT or sessions)
- Permission model (user owns projects)
- Input validation on all endpoints
- Rate limiting
- HTTPS in production
- Database encryption at rest (optional)

---

## Performance Targets

| Operation | Target |
| --- | --- |
| List projects (< 100) | < 100ms |
| Create song | < 200ms |
| Generate 20 lyrics lines | < 5s (Ollama dependent) |
| Render 3-minute track | < 30s |
| Load project UI | < 500ms |
| Search genres | < 100ms |

---

## Scalability (Future Phases)

- **Horizontal:** Multiple backend instances behind load balancer
- **Caching:** Redis for frequently accessed data (genres, models)
- **Jobs:** Celery + RabbitMQ for long-running tasks
- **Database:** PostgreSQL with read replicas
- **Storage:** S3-compatible for audio/MIDI files
- **CDN:** CloudFront for static assets

