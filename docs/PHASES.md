# Somancer Studio — Complete Roadmap & Phases

## Version Timeline

| Version | Phase | Timeline | Status | Focus |
| --- | --- | --- | --- | --- |
| v0.0.1 | 0 | Weeks 1-2 | 🔨 In Progress | Foundation, CI/CD, database schema |
| v0.1 | 1 | Weeks 3-6 | 📋 Planned | Desktop shell, project management, API stubs |
| v0.2 | 2 | Weeks 7-10 | 📋 Planned | Lyrics generation, genre intelligence |
| v0.3 | 3 | Weeks 11-14 | 📋 Planned | MIDI composition, arrangement editor |
| v0.4 | 4-5 | Weeks 15-18 | 📋 Planned | Instrument rendering, mixing |
| v0.5 | 6-7 | Weeks 19-22 | 📋 Planned | Vocal synthesis, AI mixing |
| v0.6 | 8-9 | Weeks 23-26 | 📋 Planned | Mastering, advanced editing |
| v0.7 | 10-11 | Weeks 27-30 | 📋 Planned | Plugin SDK, genre research engine |
| v0.8 | 12-14 | Weeks 31-34 | 📋 Planned | Cloud sync, optimization |
| v0.9 | 15-17 | Weeks 35-38 | 📋 Planned | Testing, bugfixes, documentation |
| v1.0 | 18 | Weeks 39+ | 📋 Planned | Stable release |

---

## Phase 0: Project Foundation (Weeks 1-2)

**Status:** 🔨 In Progress  
**Owner:** Infrastructure Team  
**Deliverables:** Production-ready codebase foundation

### Week 1: Repository & Architecture
- [ ] Initialize Git repository with branching strategy
- [ ] Create pnpm monorepo structure
- [ ] Configure ESLint, Prettier, code formatting
- [ ] Add pre-commit hooks (Husky)
- [ ] Document architecture in ARCHITECTURE.md

**Success Criteria:**
- `pnpm install` works without errors
- Linting runs on every commit
- Repository structure matches project organization

### Week 2: CI/CD & Documentation
- [ ] Set up GitHub Actions pipelines
  - [ ] Test frontend (lint, type check)
  - [ ] Test backend (lint, type check, unit tests)
  - [ ] Build desktop (Tauri binary)
  - [ ] Build backend (Docker image)
- [ ] Create docker-compose.yml for local dev
- [ ] Write development setup guide (SETUP.md)
- [ ] Document API endpoints (API.md)
- [ ] Create coding standards guide (CODING_STANDARDS.md)

**Success Criteria:**
- CI passes on every PR
- First-time developer can set up in < 30 minutes
- All documentation complete and tested

### Phase 0 Checklist
- [ ] Git repository initialized with proper .gitignore
- [ ] Monorepo configured (pnpm-workspace.yaml)
- [ ] ESLint, Prettier, pre-commit configured
- [ ] Docker + docker-compose working
- [ ] GitHub Actions CI/CD passing
- [ ] All documentation written and linked from README
- [ ] Database schema (SQLAlchemy models) created
- [ ] FastAPI app skeleton with basic endpoints
- [ ] React + Tauri desktop skeleton with routing
- [ ] Environment variables configured (.env.example)

---

## Phase 1: Core Platform (Weeks 3-6)

**Status:** 📋 Planned  
**Owner:** Core Team  
**Deliverables:** Functional MVP with project system

### Milestone 1: Desktop Shell & Routing
- [ ] Implement main layout (header, sidebar, content)
- [ ] Create navigation routes (Dashboard, Project, Settings)
- [ ] Add Material-UI theme and styling
- [ ] Implement basic state management (React Context)

### Milestone 2: Project Management UI
- [ ] Create project list page
- [ ] Implement project creation flow (form, validation)
- [ ] Build project detail page
- [ ] Add project settings panel

### Milestone 3: Backend API (CRUD)
- [ ] Implement project endpoints (GET, POST, PATCH, DELETE)
- [ ] Implement song endpoints
- [ ] Implement track endpoints
- [ ] Add pagination and filtering
- [ ] Add error handling and validation

### Milestone 4: Database Integration
- [ ] Set up SQLAlchemy and Alembic
- [ ] Create initial migration
- [ ] Implement database service layer
- [ ] Add connection pooling

### Milestone 5: Frontend-Backend Integration
- [ ] Create API client (Axios)
- [ ] Implement API service layer
- [ ] Connect project list to backend
- [ ] Add loading and error states

**Success Criteria:**
- Users can create, read, update, delete projects
- UI responds to API changes in real-time
- CI passes with 80%+ test coverage
- Performance target: API responses < 200ms

---

## Phase 2: AI Lyrics & Genre Intelligence (Weeks 7-10)

**Status:** 📋 Planned  
**Owner:** AI Team  
**Deliverables:** Lyrics generation, genre database

### Milestone 6: Ollama Integration
- [ ] Set up Ollama service in docker-compose
- [ ] Create Ollama client in backend
- [ ] Implement prompt routing to models
- [ ] Add error handling for Ollama failures

### Milestone 7: Songwriter Agent
- [ ] Define songwriter agent persona and prompts
- [ ] Implement lyrics generation endpoint
- [ ] Support verse/chorus/bridge generation
- [ ] Add lyric editing UI

### Milestone 8: Genre Database
- [ ] Create genre table schema
- [ ] Seed database with 100+ genres
- [ ] Implement genre lookup endpoints
- [ ] Add genre search/filter UI

### Milestone 9: Genre Research Engine
- [ ] Implement web research for unknown genres
- [ ] Extract genre metadata (BPM, keys, instruments)
- [ ] Store research results in database
- [ ] Add manual review workflow

**Success Criteria:**
- Generate 10 lyric lines in < 5 seconds
- All genres searchable and filterable
- Research engine adds 10 new genres/month
- No copyright violations in research

---

## Phase 3: MIDI Composition & Arrangement (Weeks 11-14)

**Status:** 📋 Planned  
**Owner:** Composition Team  
**Deliverables:** Melody/harmony generation, arrangement editor

### Milestone 10: Composer Agent
- [ ] Define composer agent with music theory knowledge
- [ ] Implement melody generation
- [ ] Implement harmony/chord progression generation
- [ ] Output as MIDI

### Milestone 11: Arranger Agent
- [ ] Define song structure (intro, verse, chorus, bridge, outro)
- [ ] Implement track arrangement suggestions
- [ ] Support duration and intensity customization

### Milestone 12: MIDI Editor UI
- [ ] Implement piano roll view
- [ ] Add note editing (add, remove, move, resize)
- [ ] Add velocity and timing controls
- [ ] Implement playback controls

### Milestone 13: MIDI Rendering
- [ ] Integrate FluidSynth
- [ ] Load SF2 soundfonts
- [ ] Render MIDI to audio
- [ ] Add synthesis preview

**Success Criteria:**
- Generate 8-bar melody in < 3 seconds
- MIDI editor handles 1000+ notes smoothly
- FluidSynth renders in real-time

---

## Phase 4: Instrument Rendering (Weeks 15-16)

**Status:** 📋 Planned  
**Owner:** Audio Team  
**Deliverables:** Multi-instrument synthesis

### Milestone 14: FluidSynth Integration
- [ ] Set up FluidSynth library
- [ ] Implement MIDI → audio pipeline
- [ ] Support multiple soundfonts simultaneously
- [ ] Add audio effects (reverb, delay, EQ)

### Milestone 15: Soundfont Management
- [ ] Create soundfont library UI
- [ ] Implement soundfont upload/import
- [ ] Add soundfont metadata storage
- [ ] Support SF2 and SFZ formats

**Success Criteria:**
- Render full song in < 30 seconds
- Support 8+ simultaneous instruments
- Audio quality matches professional DAWs

---

## Phase 5: Mixing Engine (Weeks 17-18)

**Status:** 📋 Planned  
**Owner:** Audio Team  
**Deliverables:** Professional mixing tools

### Milestone 16: Mix Console UI
- [ ] Implement track faders (volume, pan)
- [ ] Add mute/solo buttons
- [ ] Implement track grouping
- [ ] Add master fader

### Milestone 17: Effects & EQ
- [ ] Implement parametric EQ
- [ ] Add compression
- [ ] Add reverb and delay
- [ ] Add saturation/distortion

### Milestone 18: Automation
- [ ] Implement volume automation
- [ ] Implement effect parameter automation
- [ ] Add automation visualization
- [ ] Playback with automation

**Success Criteria:**
- Mix 10-track song smoothly in real-time
- Professional-grade audio quality

---

## Phase 6: Vocal Synthesis (Weeks 19-20)

**Status:** 📋 Planned  
**Owner:** AI Team  
**Deliverables:** Text-to-speech voice rendering

### Milestone 19: Voice Models
- [ ] Integrate singing voice model
- [ ] Support multiple voices (male, female, styles)
- [ ] Implement voice training/customization

### Milestone 20: Vocal Performance
- [ ] Convert lyrics to phonemes
- [ ] Implement expression controls (emotion, breathiness)
- [ ] Add vibrato and pitch bending
- [ ] Render vocals with prosody

**Success Criteria:**
- Generate 20-second vocal line in < 5 seconds
- Natural-sounding singing

---

## Phase 7: Vocal Harmonies (Weeks 21-22)

**Status:** 📋 Planned  
**Owner:** Composition Team  
**Deliverables:** Automatic harmony generation

### Milestone 21: Harmony Generation
- [ ] Implement harmony algorithm
- [ ] Generate chord-based harmonies
- [ ] Support parallel and inverse harmonies
- [ ] Add voice independence

### Milestone 22: Layering & Stacking
- [ ] Implement multi-vocal layering
- [ ] Add blend/mix controls
- [ ] Support vocal doubling

**Success Criteria:**
- Generate 3-part harmony in < 2 seconds
- Professional vocal arrangement

---

## Phase 8: AI-Assisted Mixing (Weeks 23-24)

**Status:** 📋 Planned  
**Owner:** AI Team  
**Deliverables:** Intelligent mixing suggestions

### Milestone 23: Mix Engineer Agent
- [ ] Analyze mix characteristics (frequency, dynamics, levels)
- [ ] Generate EQ suggestions
- [ ] Generate compression settings
- [ ] Suggest spatial (reverb, delay) effects

### Milestone 24: One-Click Mixing
- [ ] Implement smart mastering chain
- [ ] Auto-level all tracks
- [ ] Auto-gain stage
- [ ] Loudness normalization

**Success Criteria:**
- Generate professional mix in one click
- Continuously improve based on user feedback

---

## Phase 9: Mastering (Weeks 25-26)

**Status:** 📋 Planned  
**Owner:** Audio Team  
**Deliverables:** Mastering suite

### Milestone 25: Mastering Tools
- [ ] Implement linear phase EQ
- [ ] Add multiband compression
- [ ] Add metering (loudness, spectrum)
- [ ] Add dithering and peak limiting

### Milestone 26: Platform Presets
- [ ] Create presets for Spotify, Apple Music, YouTube
- [ ] Optimize for CD, Vinyl
- [ ] Optimize for Broadcast
- [ ] A/B comparison mode

**Success Criteria:**
- Master to spec for all major platforms
- Loudness standards compliance (LUFS)

---

## Phase 10: Audio Editing (Weeks 27-28)

**Status:** 📋 Planned  
**Owner:** Audio Team  
**Deliverables:** Waveform editor, time/pitch tools

### Milestone 27: Waveform Editor
- [ ] Implement waveform display
- [ ] Add region selection and editing
- [ ] Implement cut, copy, paste
- [ ] Add crossfading

### Milestone 28: Time & Pitch
- [ ] Implement time stretching
- [ ] Implement pitch shifting
- [ ] Add vibrato/tremolo
- [ ] Add formant preservation

**Success Criteria:**
- Edit 10-minute audio without latency
- Professional audio quality

---

## Phase 11: Plugin System (Weeks 29-30)

**Status:** 📋 Planned  
**Owner:** Infrastructure Team  
**Deliverables:** Plugin SDK and ecosystem

### Milestone 29: Plugin Architecture
- [ ] Define plugin interface (JS/WASM)
- [ ] Implement plugin loader
- [ ] Create plugin manifest format
- [ ] Add security sandboxing

### Milestone 30: Plugin Types
- [ ] Support effect plugins
- [ ] Support generator plugins
- [ ] Support theme plugins
- [ ] Support voice model plugins
- [ ] Support genre pack plugins

**Success Criteria:**
- Plugin development documented
- Example plugins provided

---

## Phase 12: Genre Research Engine (Weeks 31-32)

**Status:** 📋 Planned  
**Owner:** AI Team  
**Deliverables:** Intelligent genre research

### Milestone 31: Web Research
- [ ] Scrape Wikipedia for genre information
- [ ] Parse production articles
- [ ] Extract typical characteristics
- [ ] Build knowledge graph

### Milestone 32: User Interface
- [ ] Show genre characteristics
- [ ] Show influential artists (reference only)
- [ ] Show production techniques
- [ ] Add citation sources

**Success Criteria:**
- Research engine 95%+ accurate
- All sources attributed properly

---

## Phase 13: Learning Engine (Weeks 33-34)

**Status:** 📋 Planned  
**Owner:** AI Team  
**Deliverables:** Preference-based recommendations

### Milestone 33: User Profile
- [ ] Track user preferences (BPM, key, mood, style)
- [ ] Build user preference model
- [ ] Generate recommendations

### Milestone 34: Intelligent Suggestions
- [ ] Suggest genres based on preferences
- [ ] Suggest BPM ranges
- [ ] Suggest instrumentation
- [ ] Suggest production techniques

**Success Criteria:**
- Recommendations accuracy improves over time
- Users find suggestions useful

---

## Phase 14: Export & Distribution (Weeks 35-36)

**Status:** 📋 Planned  
**Owner:** Audio Team  
**Deliverables:** Multi-format export

### Milestone 35: Audio Export
- [ ] Export to WAV (primary format)
- [ ] Export to MP3 with quality options
- [ ] Export to FLAC
- [ ] Export to OGG Vorbis
- [ ] Export to AAC

### Milestone 36: Project Export
- [ ] Export project archive (JSON + audio)
- [ ] Export MIDI stems
- [ ] Export lead sheets (PDF)
- [ ] Export lyrics (TXT, PDF)
- [ ] Export chord charts

**Success Criteria:**
- All export formats high quality
- Batch export for albums

---

## Phase 15: Cross-Platform Optimization (Weeks 37-38)

**Status:** 📋 Planned  
**Owner:** Infrastructure Team  
**Deliverables:** Windows, macOS, Linux versions

### Milestone 37: Windows Build
- [ ] Build and test on Windows 10/11
- [ ] Optimize audio driver integration (WASAPI)
- [ ] Test with common Windows DAWs
- [ ] Distribute via installer

### Milestone 38: macOS & Linux
- [ ] Build and test on macOS 11+
- [ ] Build and test on Ubuntu LTS
- [ ] Optimize for native audio (CoreAudio, ALSA/PulseAudio)
- [ ] Distribute via installers

**Success Criteria:**
- App runs smoothly on all platforms
- Audio latency < 10ms on all platforms

---

## Phase 16: Testing & QA (Weeks 39-40)

**Status:** 📋 Planned  
**Owner:** QA Team  
**Deliverables:** Comprehensive test suite

### Milestone 39: Unit & Integration Tests
- [ ] 80%+ code coverage (backend)
- [ ] 60%+ code coverage (frontend)
- [ ] All critical paths tested
- [ ] Performance benchmarks

### Milestone 40: User Testing
- [ ] Beta program with 100+ testers
- [ ] Gather feedback
- [ ] Fix critical bugs
- [ ] Performance optimization

**Success Criteria:**
- Zero critical bugs
- Performance meets targets
- User satisfaction > 4.5/5

---

## Phase 17: Documentation & Learning (Weeks 41-42)

**Status:** 📋 Planned  
**Owner:** Documentation Team  
**Deliverables:** Comprehensive guides

### Milestone 41: User Documentation
- [ ] User guide (getting started, tutorials)
- [ ] Video tutorials (YouTube)
- [ ] FAQ and troubleshooting
- [ ] Keyboard shortcuts reference

### Milestone 42: Developer Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Plugin development guide
- [ ] Architecture deep-dives
- [ ] Contribution guidelines

**Success Criteria:**
- Users can get started in < 10 minutes
- Developers can extend in < 30 minutes

---

## Phase 18: Stable Release (v1.0)

**Status:** 📋 Planned  
**Owner:** Release Team  
**Deliverables:** Production-ready v1.0

### Release Checklist
- [ ] All critical bugs fixed
- [ ] Performance optimized
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Community feedback addressed
- [ ] Version tagged in Git
- [ ] Release notes published
- [ ] Announcement made

**Success Criteria:**
- Zero known critical bugs
- Performance meets production targets
- Users report stable, usable application

---

## Future Phases (Post v1.0)

### Cloud Features (Phase 19)
- [ ] Optional project cloud sync
- [ ] Collaboration features
- [ ] Cloud model hosting
- [ ] Team accounts

### Advanced AI (Phase 20)
- [ ] Fine-tuned models for user
- [ ] MIDI analysis and transcription
- [ ] Audio source separation
- [ ] Stem extraction from existing songs

### Community (Phase 21)
- [ ] Asset marketplace
- [ ] Plugin marketplace
- [ ] Template sharing
- [ ] Sample packs

### Integration (Phase 22)
- [ ] DAW plugins (VST3, AU, CLAP)
- [ ] Sync with streaming platforms
- [ ] MIDI hardware support
- [ ] Control surface mapping

---

## Success Metrics

### Phase 0
- [ ] CI/CD passing 100%
- [ ] Documentation complete
- [ ] First-time setup < 30 minutes

### Phase 1
- [ ] 100 beta testers
- [ ] Project creation/editing working
- [ ] API stable (no breaking changes)

### v0.1+
- [ ] 1,000 downloads
- [ ] 4.0+ star rating
- [ ] < 5% crash rate
- [ ] < 100ms API response time

### v1.0
- [ ] 10,000 active users
- [ ] 4.5+ star rating
- [ ] < 1% crash rate
- [ ] Feature parity with professional DAWs

---

## Dependency Chain

```
Phase 0 (Foundation)
    ↓
Phase 1 (Core Platform)
    ├─→ Phase 2 (Lyrics)
    ├─→ Phase 3 (Composition)
    │   ├─→ Phase 4 (Rendering)
    │   └─→ Phase 7 (Harmonies)
    ├─→ Phase 5 (Mixing)
    │   └─→ Phase 8 (AI Mixing)
    ├─→ Phase 6 (Vocals)
    ├─→ Phase 9 (Mastering)
    ├─→ Phase 10 (Audio Editing)
    ├─→ Phase 11 (Plugins)
    ├─→ Phase 12 (Genre Research)
    └─→ Phase 13 (Learning)
    
Phase 14 (Export) — All phases
Phase 15 (Cross-Platform) — All phases
Phase 16 (Testing) — All phases
Phase 17 (Documentation) — All phases
Phase 18 (v1.0 Release) — All phases
```

---

## Notes

- **Timing is flexible** — Each phase may take longer based on complexity and team size
- **Parallel development** — Phases can overlap (e.g., Phase 2 and 3 can run simultaneously)
- **User feedback** — Adjust roadmap based on beta tester and early user feedback
- **Quarterly reviews** — Reassess progress every 3 months
- **Backwards compatibility** — Maintain API/plugin compatibility after v1.0

