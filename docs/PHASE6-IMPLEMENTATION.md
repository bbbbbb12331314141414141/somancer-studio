# Somancer Studio — Phase 6 Implementation Guide

**Status:** ✅ Complete  
**Version:** 0.6.0  
**Timeline:** Weeks 23–26

---

## Phase 6 Overview

Phase 6 delivers the **Plugin SDK** and **Vocal Harmony System** — making Sonmancer Studio extensible by third-party developers while adding rule-based multi-part harmony generation.

---

## What's New

### Backend

#### Plugin SDK (`services/plugin_service.py`)

The Sonmancer Plugin SDK v1.0 defines a complete plugin architecture:

**Plugin Types:**
| Type | Purpose |
| --- | --- |
| `effect` | Audio DSP: EQ, compressor, reverb, distortion |
| `generator` | Instruments and synthesizers |
| `ai` | Custom AI model integrations |
| `exporter` | Additional export formats (AIFF, DSD, etc.) |
| `visualizer` | Waveform, spectrum, and meter displays |
| `theme` | UI colour schemes |
| `voice_model` | Custom singing or speaking voices |
| `genre_pack` | Additional genre data and presets |

**Base Classes for Plugin Authors:**
```python
from aimusic.services.plugin_service import EffectPlugin, GeneratorPlugin, AIPlugin

class Plugin(EffectPlugin):
    @property
    def name(self) -> str:
        return "My Effect"

    def process(self, audio_data, sample_rate, parameters=None):
        # audio_data: np.ndarray shape (frames, channels)
        # Return processed audio with same shape
        return audio_data * 0.5
```

**PluginService capabilities:**
- `discover()` — scan `./plugins/` and `~/.sonmancer/plugins/`
- `discover_and_register()` — discover + cache all found plugins
- `load_plugin(id)` — dynamically import Python entry point
- `unload_plugin(id)` — remove from sys.modules
- `list_plugins(type?)` — list all or filtered by type
- `get_loaded_effect(id)` — return `EffectPlugin` instance
- `create_example_plugin_dir(path)` — write SDK example for developers

**Plugin Manifest (`manifest.json`):**
```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "type": "effect",
  "author": "Your Name",
  "description": "What this plugin does",
  "entry_point": "plugin.py",
  "api_version": "1.0",
  "tags": ["effect", "utility"],
  "permissions": ["audio"],
  "config_schema": {
    "gain_db": {
      "type": "float", "default": 0.0,
      "min": -24.0, "max": 12.0, "label": "Gain (dB)"
    }
  }
}
```

---

#### Vocal Harmony Service (`services/vocal_harmony_service.py`)

Rule-based voice leading — no AI/Ollama required:

**Features:**
- 2–4 part harmonies (duet, trio, quartet)
- Voice range enforcement (soprano, mezzo, alto, tenor, baritone, bass)
- Smooth voice leading (minimal pitch movement between consecutive notes)
- Diatonic scale harmonization (major, minor, Dorian)
- Parallel harmony at fixed intervals (thirds, fifths, etc.)
- MIDI track output compatible with `CompositionResult`

**API:**
```python
svc = VocalHarmonyService()

# Full 4-part harmony
result = svc.generate_harmonies(
    lead_notes=[{"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 80}, ...],
    key="A Minor",
    voice_count=3,     # lead + 3 voices = quartet
)

# Simple parallel fifth
notes = svc.generate_parallel_harmony(lead_notes, interval_semitones=7, key="C Major")

# Export as MIDI tracks
midi_tracks = svc.voices_to_midi_tracks(result, include_lead=True)
```

---

#### New API Endpoints

**Plugins (`/api/v1/plugins/`)** — 7 endpoints:

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/plugins/` | GET | List all plugins (filterable by type) |
| `/plugins/types` | GET | List valid types with descriptions |
| `/plugins/discover` | POST | Rescan plugin directories |
| `/plugins/{id}/load` | POST | Load a plugin module |
| `/plugins/{id}/unload` | POST | Unload a plugin |
| `/plugins/example` | POST | Create example gain plugin |
| `/plugins/sdk/template` | GET | Plugin SDK documentation + template |

**Harmony (`/api/v1/harmony/`)** — 4 endpoints:

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/harmony/generate` | POST | Generate 2–4 part harmonies |
| `/harmony/parallel` | POST | Generate parallel harmony at fixed interval |
| `/harmony/voice-ranges` | GET | MIDI ranges per voice type |
| `/harmony/intervals` | GET | Common intervals + guidance |

---

#### Tests

- `tests/test_plugins.py` — 18 tests:
  - Plugin discovery (valid, invalid type, missing manifest)
  - Example plugin creation and loading
  - Python module dynamic import
  - EffectPlugin processing with numpy
  - Plugin unloading and memory cleanup

- **Total: 76 tests** (was 58)

---

### Frontend

#### `PluginManagerPage` (`/plugins`) — 2 tabs:

**Tab 1 — Installed Plugins:**
- Live plugin list with type chips, version, author, description, tags
- Loaded/Unloaded status badge
- Load / Unload buttons per plugin
- Rescan and Create Example buttons in header
- Plugin type reference guide

**Tab 2 — Plugin SDK:**
- Step-by-step quick start guide
- Base class import examples
- manifest.json template viewer (fetched from API)
- Example EffectPlugin code block
- One-click "Generate Example Plugin" button

---

## Usage

### Create your first plugin

```bash
# Option A: API
curl -X POST http://localhost:8000/api/v1/plugins/example

# Option B: Manual
mkdir -p plugins/my-plugin
cat > plugins/my-plugin/manifest.json << 'JSON'
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "type": "effect",
  "author": "You",
  "description": "My first plugin",
  "entry_point": "plugin.py",
  "api_version": "1.0"
}
JSON
```

### Discover and load plugins

```bash
# List all plugins
curl http://localhost:8000/api/v1/plugins/

# Rescan directories
curl -X POST http://localhost:8000/api/v1/plugins/discover

# Load a plugin
curl -X POST http://localhost:8000/api/v1/plugins/my-plugin/load
```

### Generate harmonies

```bash
# 4-part harmony
curl -X POST http://localhost:8000/api/v1/harmony/generate \
  -H "Content-Type: application/json" \
  -d '{
    "lead_notes": [
      {"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 80},
      {"pitch": 62, "start": 1.0, "duration": 1.0, "velocity": 80},
      {"pitch": 64, "start": 2.0, "duration": 1.0, "velocity": 80}
    ],
    "key": "C Major",
    "voice_count": 3
  }'

# Voice ranges
curl http://localhost:8000/api/v1/harmony/voice-ranges

# Common harmony intervals
curl http://localhost:8000/api/v1/harmony/intervals
```

---

## File Summary

| File | Type | New/Updated |
| --- | --- | --- |
| `services/plugin_service.py` | Backend | New (320 lines) |
| `services/vocal_harmony_service.py` | Backend | New (270 lines) |
| `schemas/plugins.py` | Backend | New |
| `api/plugins.py` | Backend | New (260 lines — plugin + harmony routers) |
| `main.py` | Backend | Updated (v0.6.0) |
| `tests/test_plugins.py` | Backend | New (18 tests) |
| `pages/PluginManagerPage.tsx` | Frontend | New (280 lines) |
| `App.tsx` | Frontend | Updated |
| `Sidebar.tsx` | Frontend | Updated (v0.6.0) |

**Total new files: 7**  
**Total files: ~175**  
**Total tests: 76**  
**Total API endpoints: ~55**

---

## What's Next (Phase 7)

- **Advanced export formats** — AIFF, DSD, stems ZIP bundle
- **Project archive** — full project export (.sonmancer archive format)
- **Cloud sync** — optional project sync
- **Performance optimisation** — async render queue, caching
- **Cross-platform testing** — Windows 11, Ubuntu 24.04, macOS 14
- **UI polish** — dark mode, keyboard shortcuts, accessibility

