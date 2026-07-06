# Somancer Studio — Phase 5 Implementation Guide

**Status:** ✅ Complete  
**Version:** 0.5.0  
**Timeline:** Weeks 19–22

---

## Phase 5 Overview

Phase 5 delivers **AI Mixing, Mastering, Stem Export, and Vocal Synthesis Foundation** — the complete production pipeline from composition to a platform-ready master.

---

## Architecture: Complete Production Pipeline

```
AI Studio (Phase 3)          Audio Studio (Phase 4)
      │                              │
      ▼                              ▼
  AI Composer             FluidSynth Render
      │                              │
      └──────────┬───────────────────┘
                 │ CompositionResult
                 ▼
    ┌─────────────────────────────────┐
    │        Mixing Console           │  ← NEW Phase 5
    │                                 │
    │  ┌──────────┐  ┌─────────────┐  │
    │  │ Mix Plan │  │  Mastering  │  │
    │  │  Agent   │  │   Chain     │  │
    │  └──────────┘  └─────────────┘  │
    │  ┌──────────┐  ┌─────────────┐  │
    │  │  Stems   │  │   Vocals    │  │
    │  │  Export  │  │ (TTS stub)  │  │
    │  └──────────┘  └─────────────┘  │
    └─────────────────────────────────┘
                 │
                 ▼
          Platform Master
    (Spotify / Apple / YouTube / CD)
```

---

## What's New

### Backend

#### New Agents

**`MixEngineerAgent`** — generates complete per-track mix plans:
- `plan_mix(genre, mood, tracks)` → `MixPlan` with EQ, compression, panning, reverb per track
- `analyse_frequency_balance(genre, description)` → frequency correction suggestions
- `suggest_stereo_placement(tracks, genre)` → pan positions for all instruments

**`MasteringEngineerAgent`** — generates mastering chains targeting platform standards:
- `create_mastering_chain(genre, mood, platform, dynamic_range)` → full signal chain
- Supports: Spotify (−14 LUFS), Apple Music (−16), YouTube (−14), CD (−9), Vinyl (−12), Broadcast (−23)
- `compare_platform_targets()` → all platforms explained
- `review_master(genre, measured_lufs, measured_peak_db, platform)` → pass/fail + corrections

#### New Services

**`StemExportService`** — renders individual stems as separate WAV files:
- Auto-groups tracks into: drums, bass, keys, guitar, strings, brass, fx, other
- Renders each group as an isolated WAV + full mix
- Custom `StemGroup` definitions supported
- Uses FluidSynth + midiutil pipeline internally

**`VocalSynthesisService`** — text-to-singing pipeline foundation:
- `synthesise(vocal_lines, bpm)` → `VocalSynthesisResult`
- `get_available_engines()` → list with availability + install instructions
- Phase 5 engine: `tts_stub` (pyttsx3 text-to-speech for development)
- Phase 6 engines: `diffsinger`, `rvc` (stubs, `NotImplementedError`)
- `text_to_phonemes(text)` — English → IPA approximation
- `align_phonemes_to_notes(text, notes)` — beat-aligned phoneme segmentation

#### New API Endpoints — 10 total (`/api/v1/mix/`)

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/mix/plan` | POST | Generate AI mix plan for all tracks |
| `/mix/stereo-placement` | POST | Suggest stereo panning for instruments |
| `/mix/platforms` | GET | List loudness standards for all platforms |
| `/mix/master` | POST | Generate mastering chain for platform |
| `/mix/master/review` | POST | Review a completed master |
| `/mix/stems/export` | POST | Export composition to individual stems |
| `/mix/vocals/engines` | GET | List available vocal synthesis engines |
| `/mix/vocals/synthesise` | POST | Synthesise lyrics to audio |
| `/mix/vocals/phonemes` | POST | Convert text to phonemes |

#### New Tests

- `tests/test_mixing.py` — 9 tests (platforms, vocal engines, phonemes, mix plan, mastering)
- `tests/test_vocal_phonemes.py` — 8 tests (phoneme conversion, note alignment, engine stubs)
- **Total: 58 tests** (was 41)

---

### Frontend

#### New Page: `MixingConsolePage` (`/mixing`)

4 tabs:

**Tab 1 — Mix Plan**
- Input: genre, mood, track list (comma separated)
- Output: per-track cards with EQ chips, pan bar visualiser, compressor settings, reverb send
- AI-generated mix notes banner

**Tab 2 — Mastering**
- Input: genre, mood, platform (Spotify/Apple/YouTube/CD/Vinyl/Broadcast), dynamic range
- Output: LUFS/peak targets, stage-by-stage chain cards (EQ → multiband comp → stereo widener → limiter)
- Expected character summary

**Tab 3 — Stems**
- Info panel explaining the API workflow
- Lists automatic stem group names

**Tab 4 — Vocals**
- Engine selection cards (available/coming soon status)
- Multi-line lyrics textarea
- Download link for rendered audio
- Clear Phase 6 upgrade path note

#### Updated Pages

**`DashboardPage`** — rebuilt with:
- 4 feature shortcut cards (AI Studio, Audio Studio, Mixing Console, Genre Browser)
- Recent projects with genre/type chips
- Build progress tracker (Phases 0–8)

**`App.tsx`** — `/mixing` route added

**`Sidebar.tsx`** — "Mixing Console" nav item added (v0.5.0 version label)

---

## API Quick Reference

```bash
# Mix plan for a neo-soul track
curl -X POST http://localhost:8000/api/v1/mix/plan \
  -H "Content-Type: application/json" \
  -d '{
    "genre": "neo-soul",
    "mood": "romantic",
    "tracks": [
      {"name": "Piano", "instrument": "piano"},
      {"name": "Bass",  "instrument": "bass"},
      {"name": "Drums", "instrument": "drums"}
    ]
  }'

# Mastering chain for Spotify
curl -X POST http://localhost:8000/api/v1/mix/master \
  -H "Content-Type: application/json" \
  -d '{"genre":"neo-soul","mood":"romantic","platform":"spotify","dynamic_range":"medium"}'

# Platform loudness targets
curl http://localhost:8000/api/v1/mix/platforms

# Vocal engines
curl http://localhost:8000/api/v1/mix/vocals/engines

# Phoneme conversion
curl -X POST "http://localhost:8000/api/v1/mix/vocals/phonemes?text=I+love+the+night+sky"

# Synthesise vocals (TTS stub)
curl -X POST http://localhost:8000/api/v1/mix/vocals/synthesise \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics": [
      {"text": "I love the night sky", "section": "verse"},
      {"text": "Stars burn bright above", "section": "verse"}
    ],
    "bpm": 90,
    "engine": "tts_stub"
  }'
```

---

## Platform Loudness Standards

| Platform | Integrated LUFS | True Peak |
| --- | --- | --- |
| Spotify | −14.0 | −1.0 dBTP |
| Apple Music | −16.0 | −1.0 dBTP |
| YouTube | −14.0 | −1.0 dBTP |
| Amazon Music | −14.0 | −1.0 dBTP |
| Tidal | −14.0 | −1.0 dBTP |
| SoundCloud | −14.0 | −1.0 dBTP |
| CD | −9.0 | −0.1 dBTP |
| Vinyl | −12.0 | −1.0 dBTP |
| Broadcast | −23.0 | −1.0 dBTP |

---

## Vocal Synthesis Roadmap

| Phase | Engine | Quality | Status |
| --- | --- | --- | --- |
| 5 | `tts_stub` (pyttsx3) | Low — speech only | ✅ Available |
| 6 | DiffSinger | High — neural singing | 🔜 Planned |
| 6 | RVC (voice conversion) | High — voice cloning | 🔜 Planned |
| 7 | VITS | High — end-to-end | 📋 Future |

---

## File Summary

| File | Type | New/Updated |
| --- | --- | --- |
| `agents/mix_engineer_agent.py` | Backend | New |
| `agents/mastering_engineer_agent.py` | Backend | New |
| `services/stem_export_service.py` | Backend | New |
| `services/vocal_synthesis_service.py` | Backend | New |
| `schemas/mixing.py` | Backend | New |
| `api/mixing.py` | Backend | New |
| `main.py` | Backend | Updated (v0.5.0) |
| `tests/test_mixing.py` | Backend | New |
| `tests/test_vocal_phonemes.py` | Backend | New |
| `pages/MixingConsolePage.tsx` | Frontend | New |
| `pages/DashboardPage.tsx` | Frontend | Updated |
| `App.tsx` | Frontend | Updated |
| `Sidebar.tsx` | Frontend | Updated |

**Total new files: 11**  
**Total files: ~170**  
**Total tests: 58**

---

## What's Next (Phase 6)

- **DiffSinger integration** — neural singing synthesis from phonemes + MIDI
- **RVC voice conversion** — clone a voice from a short audio sample
- **Vocal harmonies** — auto-generate 2–4 part harmonies from lead vocal
- **Advanced EQ/compression** — apply mix plan settings to audio programmatically
- **Plugin SDK** — VST3/CLAP/LV2 host for third-party instruments and effects
- **Real-time mix preview** — hear mix changes without full re-render

