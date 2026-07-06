# Somancer Studio — Phase 8 Implementation Guide

**Status:** ✅ Complete  
**Version:** 0.8.0  
**Timeline:** Weeks 31–34

---

## Phase 8 Overview

Phase 8 delivers **Performance Optimisation, Dark Mode, Keyboard Shortcuts, Accessibility, and Cross-Platform Polish** — the final steps before the v0.9 release candidate.

---

## What's New

### Backend

#### `services/cache_service.py` — In-Memory Response Cache

LRU-style cache with TTL for frequently accessed data:

```python
from aimusic.services.cache_service import get_cache, TTL_GENRE

cache = get_cache()

# Cache genre data for 5 minutes
cache.set("genres:all", genres, ttl=TTL_GENRE)

# Get or compute pattern
genres = cache.get_or_compute(
    key="genres:all",
    fn=lambda: db.query(Genre).all(),
    ttl=TTL_GENRE,
)
```

**TTL presets:**
| Constant | Seconds | Used for |
| --- | --- | --- |
| `TTL_GENRE` | 300 | Genre lookups |
| `TTL_MODELS` | 60 | Ollama model list |
| `TTL_PLATFORM` | 86400 | Platform loudness targets |
| `TTL_SONG` | 30 | Song metadata |
| `TTL_DEFAULT` | 120 | Everything else |

**Features:**
- `get/set/delete` with TTL
- `invalidate_prefix("genres:")` — bulk invalidation
- `get_or_compute(key, fn, ttl)` — compute-and-cache pattern
- `purge_expired()` — cleanup expired entries
- LRU eviction when `max_size` reached
- Hit rate statistics

#### `api/system.py` — System Management API

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/system/info` | GET | Version, Python, platform, uptime, config |
| `/system/health/detail` | GET | DB + cache + job queue status |
| `/system/cache/stats` | GET | Cache hit rate + size |
| `/system/cache/purge` | POST | Remove expired entries |
| `/system/cache/clear` | POST | Clear entire cache |
| `/system/cache/invalidate` | POST | Invalidate by prefix |
| `/system/settings` | GET | Current application settings |
| `/system/directories` | GET | Important paths + existence |
| `/system/directories/init` | POST | Create missing directories |

**v0.8.0 startup improvements:**
- Auto-creates all required directories on startup
- Logs Python version and environment
- Pre-initialises job queue and cache singletons

#### Tests

- `tests/test_cache_service.py` — 10 tests
- `tests/test_system_api.py` — 11 tests
- **Total: 113 tests** (was 92)

---

### Frontend

#### Dark Mode (`context/ThemeContext.tsx`)

Three-way theme: `light | dark | system`

```tsx
import { useThemeMode } from '../context/ThemeContext';

const { mode, effectiveMode, setMode, toggleMode } = useThemeMode();

// Set specific mode
setMode('dark');

// Toggle between light and dark
toggleMode();

// Detect actual mode (system resolves to light/dark)
console.log(effectiveMode); // 'light' | 'dark'
```

- Persisted to `localStorage` as `sonmancer-theme`
- Respects system `prefers-color-scheme` media query
- MUI theme rebuilds automatically on change

#### Keyboard Shortcuts (`hooks/useKeyboardShortcuts.ts`)

```tsx
useKeyboardShortcuts([
  { key: 'k', meta: true, action: () => navigate('/projects/new'), label: 'New Project' },
  { key: ' ', action: togglePlayback, label: 'Play / Pause' },
]);
```

- Registered globally on `window`
- Automatically ignored when typing in `<input>` / `<textarea>`
- Cleaned up on component unmount
- Meta = Cmd (macOS) / Ctrl (Windows/Linux)

**Default global shortcuts (active on all pages):**

| Shortcut | Action |
| --- | --- |
| ⌘K | New Project |
| ⌘P | Go to Projects |
| ⌘G | Genre Browser |
| ⌘A | AI Studio |
| ⌘M | Mixing Console |
| ⌘E | Export |
| ⌘, | Settings |
| `?` | Show shortcuts dialog |

#### `Header.tsx` — Phase 8 updates

- Dark/light toggle button with tooltip
- Keyboard shortcuts (⌨) button → modal table
- Version chip `v0.8.0`
- Full ARIA labels on all icon buttons

#### `Layout.tsx` — Phase 8 updates

- Global keyboard shortcuts registered via `useKeyboardShortcuts`
- `<main role="main" aria-label="Main content">` for screen readers
- Sidebar now `variant="temporary"` (accessible close on overlay click/Escape)

#### `SettingsPage.tsx` — Phase 8 updates

- **Appearance section** — Light / Dark / System buttons
- **System Information card** — version, Python, platform, uptime, config
- Refresh button fetches from `/api/v1/system/info`
- Settings saved to `localStorage` on Save button

#### `App.tsx` — Phase 8 updates

- `AppThemeProvider` wraps everything at the root
- ThemeProvider now inside `AppThemeProvider` (no duplicate)

---

## Architecture Summary (v0.8.0)

```
packages/desktop/src/
├── context/
│   ├── ProjectContext.tsx      ← global project state
│   └── ThemeContext.tsx        ← dark/light/system theme  ← NEW
├── hooks/
│   ├── useAI.ts
│   ├── useProjects.ts
│   └── useKeyboardShortcuts.ts ← global hotkeys           ← NEW
├── components/
│   ├── layout/
│   │   ├── Header.tsx          ← dark toggle, shortcuts    ← UPDATED
│   │   ├── Sidebar.tsx         ← accessible, v0.8.0
│   │   └── Layout.tsx          ← shortcuts, ARIA           ← UPDATED
│   ├── audio/
│   │   ├── WaveformDisplay.tsx
│   │   └── PlaybackControls.tsx
│   ├── midi/
│   │   └── PianoRoll.tsx
│   └── common/
│       ├── ConfirmDialog.tsx
│       └── LoadingScreen.tsx
└── pages/
    ├── DashboardPage.tsx       ← build progress tracker
    ├── ProjectsPage.tsx
    ├── NewProjectPage.tsx
    ├── ProjectDetailPage.tsx
    ├── SongEditorPage.tsx
    ├── GenresPage.tsx
    ├── AIStudioPage.tsx
    ├── AudioStudioPage.tsx
    ├── MixingConsolePage.tsx
    ├── PluginManagerPage.tsx
    ├── ExportPage.tsx
    └── SettingsPage.tsx        ← dark mode UI, system info ← UPDATED
```

```
packages/backend/aimusic/
├── api/
│   ├── projects.py, songs.py, lyrics.py, genres.py
│   ├── ai.py, export.py, audio.py, mixing.py
│   ├── plugins.py (+ harmony_router)
│   ├── advanced_export.py
│   └── system.py              ← NEW
├── services/
│   ├── ollama_service.py
│   ├── audio_service.py
│   ├── stem_export_service.py
│   ├── vocal_synthesis_service.py
│   ├── vocal_harmony_service.py
│   ├── plugin_service.py
│   ├── export_service.py
│   ├── job_queue.py
│   └── cache_service.py       ← NEW
├── agents/
│   ├── base_agent.py
│   ├── songwriter_agent.py
│   ├── composer_agent.py
│   ├── producer_agent.py
│   ├── mix_engineer_agent.py
│   ├── mastering_engineer_agent.py
│   └── genre_researcher_agent.py
├── models/, schemas/, utils/
└── main.py (v0.8.0)
```

---

## Total API Endpoints (v0.8.0)

| Router | Endpoints |
| --- | --- |
| projects | 5 |
| songs | 5 |
| lyrics | 5 |
| genres | 6 + 2 AI |
| ai | 7 |
| export (MIDI) | 1 |
| audio | 4 |
| mixing | 9 |
| plugins | 7 |
| harmony | 4 |
| advanced_export | 12 |
| system | 9 |
| **Total** | **~76** |

---

## File Summary

| File | Type | Status |
| --- | --- | --- |
| `services/cache_service.py` | Backend | New |
| `api/system.py` | Backend | New |
| `main.py` | Backend | Updated (v0.8.0) |
| `tests/test_cache_service.py` | Backend | New (10 tests) |
| `tests/test_system_api.py` | Backend | New (11 tests) |
| `context/ThemeContext.tsx` | Frontend | New |
| `hooks/useKeyboardShortcuts.ts` | Frontend | New |
| `components/layout/Header.tsx` | Frontend | Updated |
| `components/layout/Layout.tsx` | Frontend | Updated |
| `pages/SettingsPage.tsx` | Frontend | Updated |
| `App.tsx` | Frontend | Updated |

**Total new/updated files: 11**  
**Total project files: ~200**  
**Total tests: 113**  
**Total API endpoints: ~76**

---

## What's Next (Phase 9: v0.9 Release Candidate)

- User documentation site (MkDocs or Docusaurus)
- Comprehensive end-to-end test suite
- Windows 11 + Ubuntu 24.04 + macOS 14 release builds
- Plugin marketplace starter
- Error reporting / crash log export
- Final v1.0 stable release preparation

