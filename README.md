### Somancer Studio

> A cross-platform, offline-first AI-powered music production suite built with specialized AI agents.

AI Music Studio is an integrated desktop application designed to help creators generate complete songs using a collaborative team of AI agents. Rather than relying on a single general-purpose language model, the application uses multiple specialized agents that work together to produce lyrics, melodies, arrangements, harmonies, and final audio.

The project is designed to be modular, extensible, and privacy-focused, with support for running entirely offline using local AI models.

---

# Vision

The goal of AI Music Studio is to create an end-to-end music production environment where a user can describe an idea and receive a complete production—from concept to exported audio.

The application combines:

- AI songwriting
- MIDI composition
- Arrangement generation
- Audio rendering
- Plugin support
- Local AI inference
- Optional cloud synchronization

while remaining fully usable without an internet connection.

---

# Core Principles

- Offline-first architecture
- Privacy-focused local AI
- Modular plugin ecosystem
- Cross-platform desktop application
- Extensible AI agent framework
- Professional music production workflow

---

# AI Agent Architecture

Instead of one monolithic AI model, the application is built around specialized agents.

## Planned Agents

| Agent | Responsibility |
|---------|----------------|
| Producer | Coordinates project planning and generation |
| Songwriter | Lyrics, themes, structure |
| Composer | Melody and harmony generation |
| Arranger | Instrument placement and song structure |
| Drummer | Rhythm and percussion |
| Bassist | Bassline generation |
| Sound Designer | Instrument selection and synthesis |
| Vocal Director | Vocal performance planning |
| Mixing Engineer | Mixing and mastering assistance |

Each agent has focused context, allowing more consistent and controllable results than a single general-purpose model.

---

# Technology Stack

## Desktop

- Tauri
- React
- TypeScript
- Vite

## Backend

- FastAPI
- Python
- SQLite (initially)
- SQLAlchemy

## AI

- Ollama
- Local LLMs
- Specialized prompt pipelines

## Audio

- MIDI
- FluidSynth
- SoundFonts (SF2)
- Future VST3 support

---

# Project Architecture

```
AI Music Studio
│
├── packages/
│   ├── desktop/
│   │   ├── React
│   │   └── Tauri
│   │
│   ├── backend/
│   │   ├── FastAPI
│   │   ├── AI Agents
│   │   └── Audio Engine
│   │
│   └── shared/
│       ├── Types
│       ├── Schemas
│       └── Shared Utilities
│
├── docs/
├── plugins/
├── models/
└── .github/
```

---

# Development Philosophy

The project follows a modular architecture where each major subsystem can evolve independently.

- Desktop UI
- Backend API
- AI Agent Framework
- Audio Engine
- Plugin System

Each component communicates through clean interfaces to simplify future expansion.

---

# Development Roadmap

## Phase 0

Project Foundation

- Repository setup
- Monorepo structure
- Development tooling
- CI/CD
- Documentation
- Coding standards

---

## Phase 1

Core Desktop Application

- Tauri shell
- React interface
- Project management
- Settings
- Navigation

---

## Phase 2

Backend API

- FastAPI
- Database models
- Project CRUD
- Background jobs
- Configuration

---

## Phase 3

AI Agent Framework

- Producer
- Songwriter
- Composer

Initial integration with Ollama.

---

## Phase 4

Music Generation

- MIDI generation
- Chord progression
- Melody generation
- Tempo
- Key signatures

---

## Phase 5

Audio Rendering

- FluidSynth
- SF2 playback
- WAV export
- MP3 export

---

## Phase 6

Mixing Engine

- Multi-track mixer
- Volume
- Pan
- Effects
- Bus routing

---

## Phase 7

Plugin Framework

- Plugin API
- Extension loading
- Third-party integrations

---

## Phase 8+

Future Development

- Genre intelligence
- Vocal synthesis
- Harmony generation
- VST3 support
- Cloud synchronization
- Collaboration
- Marketplace
- Stable v1.0 release

---

# Initial Milestone (v0.1)

The first public release focuses on one complete workflow.

User Prompt

↓

Producer

↓

Songwriter

↓

Composer

↓

Basic MIDI

↓

FluidSynth Rendering

↓

Export WAV / MP3

This vertical slice establishes the complete generation pipeline before expanding feature scope.

---

# Cross-Platform Support

Supported platforms include:

- Windows 10+
- Windows 11
- Ubuntu LTS
- Other Linux distributions (planned)

Future support:

- macOS

---

# Local AI

AI Music Studio is designed to work offline.

Primary inference engine:

- Ollama

Initial models may include:

- Llama
- Mistral
- Qwen
- Gemma

The application should function without requiring cloud services.

---

# Audio Roadmap

Initial rendering engine:

- MIDI
- FluidSynth
- SF2 SoundFonts

Future additions:

- VST3 Hosting
- LV2 Plugins
- Advanced synthesis
- Real-time effects
- Professional mastering

---

# Project Goals

- Privacy-first
- Offline capable
- Cross-platform
- Extensible
- AI-assisted rather than AI-controlled
- Open architecture
- Plugin ecosystem
- Professional music production

---

# Inspiration

This project builds upon lessons learned from previous AI music experimentation involving:

- multi-track composition
- MIDI generation
- SoundFont rendering
- AI-assisted songwriting
- offline music generation pipelines

Those experiences directly inform the architecture of AI Music Studio.

---

# Contributing

The project is currently in active development.

Contributions, ideas, testing, and feedback will be welcomed as the project matures.

---

# License

License information will be added upon the first public release.
