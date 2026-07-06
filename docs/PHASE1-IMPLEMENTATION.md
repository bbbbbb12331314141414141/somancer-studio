# Somancer Studio — Phase 1 Implementation Guide

**Status:** 🔨 Ready for Development  
**Version:** 0.1.0  
**Timeline:** Weeks 3-6

---

## Phase 1 Overview

Phase 1 delivers the **Core Platform** - a fully functional desktop application with project management and basic API integration.

### Milestones

| Milestone | Focus | Status |
| --- | --- | --- |
| M1 | Desktop Shell & Routing | ✅ Complete |
| M2 | Project Management UI | ✅ Complete |
| M3 | Backend API (CRUD) | ✅ Complete |
| M4 | Database Integration | ✅ Complete |
| M5 | Frontend-Backend Integration | ✅ Complete |

---

## What's Implemented

### Backend (FastAPI)

#### Database Layer
- [x] SQLAlchemy ORM with 14 models
- [x] Database configuration (SQLite/PostgreSQL ready)
- [x] Connection pooling
- [x] Session management

#### API Routes
- [x] `GET /projects/` — List projects
- [x] `POST /projects/` — Create project
- [x] `GET /projects/{id}` — Get project
- [x] `PATCH /projects/{id}` — Update project
- [x] `DELETE /projects/{id}` — Delete project
- [x] `GET /songs/` — List songs
- [x] `POST /songs/` — Create song
- [x] `GET /songs/{id}` — Get song
- [x] `PATCH /songs/{id}` — Update song
- [x] `DELETE /songs/{id}` — Delete song

#### Service Layer
- [x] `ProjectService` — Project business logic
- [x] `SongService` — Song business logic
- [x] Error handling
- [x] Validation

#### Schemas (Pydantic)
- [x] `ProjectCreate`, `ProjectUpdate`, `ProjectResponse`
- [x] `SongCreate`, `SongUpdate`, `SongResponse`
- [x] List responses with pagination

#### Testing
- [x] Project endpoint tests
- [x] Database tests
- [x] Error handling tests

### Frontend (React/Tauri)

#### Components
- [x] Layout (Header + Sidebar)
- [x] Header with navigation
- [x] Sidebar with menu
- [x] Responsive design

#### Pages
- [x] Dashboard page
- [x] Projects list page
- [x] Settings page
- [x] Routing with React Router

#### State Management
- [x] Project Context (global state)
- [x] Error handling
- [x] Loading states
- [x] Actions (create, read, update, delete)

#### Services
- [x] API client (axios)
- [x] Project service functions
- [x] Error handling
- [x] Request/response types

#### Types
- [x] TypeScript interfaces
- [x] Project, Song, Track types
- [x] API response types

#### Styling
- [x] Material-UI theme
- [x] Responsive grid layout
- [x] Card-based design

---

## File Structure

### Backend

```
packages/backend/
├── aimusic/
│   ├── __init__.py
│   ├── main.py              ✅ FastAPI app with routers
│   ├── config.py            ✅ Settings from env
│   ├── db.py                ✅ Database setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── entities.py      ✅ 14 ORM models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── project.py       ✅ Project schemas
│   │   └── song.py          ✅ Song schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── project_service.py ✅ Project logic
│   │   └── song_service.py    ✅ Song logic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── projects.py      ✅ Project routes
│   │   └── songs.py         ✅ Song routes
│   └── utils/ (ready for Phase 2)
├── tests/
│   ├── __init__.py
│   └── test_projects.py     ✅ Project tests
├── migrations/ (ready for Alembic)
├── pyproject.toml           ✅ Python dependencies
└── README.md                ✅ Backend guide
```

### Frontend

```
packages/desktop/src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx       ✅ App header
│   │   ├── Sidebar.tsx      ✅ Navigation menu
│   │   └── Layout.tsx       ✅ Main layout
│   ├── project/ (ready for Phase 2)
│   └── common/ (ready for Phase 2)
├── pages/
│   ├── DashboardPage.tsx    ✅ Dashboard
│   ├── ProjectsPage.tsx     ✅ Projects list
│   └── SettingsPage.tsx     ✅ Settings
├── services/
│   ├── api.ts               ✅ Axios client
│   └── projectService.ts    ✅ Project API calls
├── context/
│   └── ProjectContext.tsx   ✅ Global state
├── types/
│   └── index.ts             ✅ Interfaces
├── hooks/ (ready for Phase 2)
├── utils/ (ready for Phase 2)
├── App.tsx                  ✅ Root component
├── main.tsx                 ✅ Entry point
└── index.css                ✅ Styles
```

---

## How to Use

### 1. Start Backend

```bash
cd packages/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Initialize database (auto-runs on startup)
# Then run:
uvicorn aimusic.main:app --reload --port 8000
```

### 2. Start Frontend

```bash
cd packages/desktop

# Install dependencies (if not already done)
pnpm install

# Start dev server
pnpm dev
```

### 3. Verify

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Swagger docs
open http://localhost:8000/api/v1/docs

# Frontend
open http://localhost:5173
```

---

## API Endpoints

All endpoints are available at `http://localhost:8000/api/v1/`

### Projects
```
GET    /projects/              # List all projects
POST   /projects/              # Create new project
GET    /projects/{id}          # Get project by ID
PATCH  /projects/{id}          # Update project
DELETE /projects/{id}          # Delete project
```

### Songs
```
GET    /songs/                 # List songs
POST   /songs/                 # Create song
GET    /songs/{id}             # Get song by ID
PATCH  /songs/{id}             # Update song
DELETE /songs/{id}             # Delete song
```

### Health
```
GET    /health                 # Health check
```

---

## Testing

### Run Backend Tests

```bash
cd packages/backend
pytest tests/ -v --cov=aimusic
```

### Test Coverage

Current coverage:
- `test_projects.py` — 8 tests (list, create, get, update, delete, errors)
- More tests can be added for songs and other services

---

## Environment Variables

See `.env.example` for all available variables. Key ones for Phase 1:

```env
# Database
DATABASE_URL=sqlite:///./sonmancer.db

# Ollama (not used until Phase 3)
OLLAMA_HOST=http://localhost:11434

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend
VITE_API_URL=http://localhost:8000
```

---

## Key Technologies

### Backend
- **FastAPI** — Modern, fast web framework
- **SQLAlchemy 2.0** — ORM with async support
- **Pydantic v2** — Data validation
- **pytest** — Testing framework

### Frontend
- **React 18** — UI framework
- **TypeScript** — Type safety
- **Material-UI** — Component library
- **React Router v6** — Client-side routing
- **Axios** — HTTP client
- **Tauri** — Desktop framework

---

## Common Tasks

### Add a New API Endpoint

1. **Create schema** in `packages/backend/aimusic/schemas/`
2. **Create service** in `packages/backend/aimusic/services/`
3. **Create router** in `packages/backend/aimusic/api/`
4. **Include router** in `main.py`
5. **Add tests** in `packages/backend/tests/`

### Add a New Page

1. **Create component** in `packages/desktop/src/pages/`
2. **Add route** in `App.tsx`
3. **Add navigation** in `Sidebar.tsx`

### Add a New Component

1. **Create in** `packages/desktop/src/components/`
2. **Export from** `App.tsx` or page component
3. **Style with Material-UI**

---

## Next Steps (Phase 2)

When Phase 1 is stable, proceed to Phase 2:

### Project Detail Editor
- View/edit song list for a project
- Add/delete songs
- Edit project metadata

### Song Editor
- View/edit tracks
- Add/delete tracks
- Basic track controls (volume, pan, mute)

### Lyrics Management
- View lyrics for song
- Generate lyrics (Phase 3 AI)
- Manual lyric entry

### Genre Database
- Browse genres
- View genre characteristics
- Genre research (Phase 3)

---

## Troubleshooting

### Backend won't start
```bash
# Reset database
rm sonmancer.db

# Check Python version
python3.11 --version

# Verify dependencies
pip list | grep fastapi
```

### Frontend can't connect to backend
```bash
# Check backend running
curl http://localhost:8000/api/v1/health

# Check .env has correct URL
grep VITE_API_URL .env
```

### Tests failing
```bash
# Run specific test
pytest tests/test_projects.py::test_create_project -v

# Check database state
rm sonmancer.db  # Reset for tests
```

---

## Success Criteria

✅ Backend API fully functional  
✅ Frontend routing working  
✅ Project CRUD operations complete  
✅ Database persisting data  
✅ All tests passing  
✅ Documentation complete  
✅ Error handling robust  

---

## Performance Notes

- Database queries: < 100ms
- API responses: < 200ms
- Frontend load: < 1s
- Memory usage: < 500MB

Optimize further in Phase 2+ if needed.

---

**Phase 1 is complete and ready for testing!**

