# Architecture

Sonmancer Studio is a local-first AI music production environment. It
composes, renders, sings, mixes, masters, and files complete songs without
sending anything to a cloud service.

This document explains how it is put together and — more usefully — **why**,
including the decisions that turned out to be wrong and were reversed.

---

## The shape of it

```
┌──────────────────────────────────────────────────────────────┐
│  Tauri 2 desktop shell (Rust)                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  React 18 + TypeScript + MUI      15 pages, ~8.6k LOC  │  │
│  └───────────────────────┬────────────────────────────────┘  │
└──────────────────────────┼───────────────────────────────────┘
                           │  HTTP, localhost:8000
┌──────────────────────────┼───────────────────────────────────┐
│  FastAPI backend         ▼            109 endpoints          │
│                                                              │
│  api/         16 routers — HTTP shape only, no logic         │
│  services/    21 services — everything that actually happens  │
│  agents/      6 LLM agents over one base                     │
│  models/      12 SQLAlchemy entities                         │
│  utils/       MIDI, loudness, path safety                    │
│                                    ~16.6k LOC, 628 tests     │
└──────────────────────────┬───────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   Ollama             FluidSynth         SQLite
   (local LLM)        ffmpeg             (project data)
                      espeak / Piper
                      ONNX Runtime
```

Everything below the backend is **optional**. The app starts and runs with
none of it installed; features report themselves unavailable rather than
crashing. That constraint shapes most of what follows.

---

## Principles

### 1. Local-first, and it has to mean something

No account, no telemetry, no cloud inference. The only outbound traffic is
genre research, which is **off by default** and sends nothing but a genre
name.

This is easy to claim and easy to violate accidentally. The test suite
asserts it: research disabled means providers are never called, and the
diagnostics service redacts credentials and home paths before writing
anything to disk.

### 2. Degrade, don't crash

Every optional dependency is missing on someone's machine. The pattern is
consistent:

```python
def available(self) -> bool:
    """Whether this can run right now, checked live."""

def _install(self) -> str:
    """The exact command that would enable it."""
```

A feature that cannot run says so, says how to fix it, and the rest of the
app carries on. Song generation with nothing installed still produces a MIDI
file.

**This was learned the hard way.** For four releases the Windows setup script
did not install espeak-ng, so song generation reached the vocal stage and
failed outright at 80% — a finished instrumental thrown away because one
optional stage could not run. The pipeline now survives `RuntimeError`,
`MemoryError`, `OSError`, and subprocess timeouts at every stage after
composition.

### 3. Say what actually happened

Two bugs made this a principle rather than a preference:

```python
job.error = str(exc)          # every httpx timeout stringifies to ""
```

A failed job reported an empty string. Users saw a blank error with nothing
to act on. Errors now always lead with the exception type and name the stage:

```
Failed during 'Synthesising vocals' — ReadTimeout
```

Similarly, genre research and vocal engines report **provenance**:
`web-grounded` versus `model-knowledge`, and every model's licence. A
MusicGen track cannot legally be sold, and that fact travels with the audio
rather than sitting in documentation nobody reads.

### 4. Long work belongs in a job queue

Composition takes minutes. Neural synthesis on CPU takes longer. Anything
that would hold an HTTP connection open returns **202 Accepted** with a job
id and a progress-reporting callback.

---

## Backend layers

### `api/` — 16 routers

HTTP shape only: request validation, status codes, error mapping. No
business logic. A router that grew logic would make that logic untestable
without spinning up the app.

Error mapping is deliberate rather than a blanket 500:

| Status | Meaning |
| --- | --- |
| **504** | Model too slow for the configured timeout |
| **503** | Ollama not running, or a required service down |
| **502** | Model responded, but the output was unusable |
| **501** | Optional dependency not installed |
| **403** | Refused — currently only voice-cloning without consent |

Endpoints by area: mix 13, advanced-export 12, genres 11, system 9,
neural 9, studio 9, library 8, ai 7, plugins 7, diagnostics 7.

!!! warning "Route ordering"
    FastAPI matches in registration order. `/genres/{genre_id}` declared
    before `/genres/resolve` makes the latter unreachable — `resolve` is
    parsed as an integer id and every request 422s. Static paths go first,
    and a test enforces it.

### `services/` — 21 services

Where everything actually happens. Each is independently testable and takes
its dependencies as constructor arguments, so tests inject stubs rather than
patching module globals.

**Generation**
`song_generator` orchestrates the full pipeline · `song_library` handles
on-disk storage · `genre_fusion_service` blends genres · `research_service`
does optional web lookup

**Audio**
`audio_service` renders MIDI via FluidSynth · `export_service` converts
formats via ffmpeg · `stem_export_service` · `vocal_engines` (nine engines) ·
`neural_audio_service` (Hugging Face models) · `sound_library_service` (SF2
parsing, sample search)

**Infrastructure**
`ollama_service` · `job_queue` · `cache_service` · `diagnostics_service` ·
`plugin_service`

### `services/agents/` — 6 LLM agents

Producer, Songwriter, Composer, Genre Researcher, Mix Engineer, Mastering
Engineer. All extend `BaseAgent`, which owns the part that matters: **getting
JSON out of a local model**.

Local models do not reliably return clean JSON. The extractor handles fenced
blocks, prose preambles, trailing commentary, single quotes, trailing commas,
Python literals (`True`/`None`), and smart quotes — 18 cases in the test
suite.

It uses **balanced-delimiter scanning that tracks string state**, not a
regex. The original `\{.*\}` regex broke whenever prose contained braces, and
models say things like *"Structure {verse, chorus}: {...}"* constantly. An
earlier version also stripped ``` globally, which silently deleted backticks
from inside JSON string values — corrupting lyrics rather than failing
loudly.

Retry policy distinguishes cause: **parse failures retry, timeouts do not.**
Retrying a 600-second timeout twice meant thirty minutes before the user saw
an error.

### `models/` — 12 entities

SQLAlchemy 2.0 with `Mapped[]` annotations. SQLite by default; PostgreSQL via
the `[production]` extra.

Alembic handles migrations. This matters more than it sounds: `init_db()`
calls `create_all()`, which creates missing tables but **never alters
existing ones**. Without migrations, any schema change silently fails to
apply on an existing database. `render_as_batch` is enabled because SQLite
cannot `ALTER` most columns.

### `utils/`

`midi_writer` / `midi_import` (midiutil is write-only, so mido handles
reading) · `loudness` (ITU-R BS.1770-4 via pyloudnorm) · `paths` (traversal
prevention)

---

## How a song gets made

```
POST /studio/generate  →  202 + job_id
        │
        ├─ 2%   Producer agent          tempo, key, instrumentation
        ├─ 6%   Structure planning      sections sized to target length
        ├─ 10%  Songwriter agent        lyrics, or parse the user's
        ├─ 15%  Composer agent          ONE CALL PER SECTION
        │       └─ spliced onto a timeline by start bar
        ├─ 62%  MIDI writer             .mid
        ├─ 68%  FluidSynth              .wav
        ├─ 80%  Vocal engine            vocals/lead.wav
        ├─ 88%  pyloudnorm              measured LUFS
        ├─ 93%  ffmpeg                  .mp3
        └─ 98%  Manifest                every parameter, for regeneration
```

**Per-section composition is the central design decision.** Asking a model
for eight minutes in one call returns eight minutes of the same eight bars.
Composing each section separately, with its own energy driving
instrumentation, is what makes a chorus feel like an arrival:

```
intro      30% energy  →  1 instrument
verse      55%         →  3
chorus    100%         →  6
```

Longer songs get **more sections, not longer ones** — a four-minute chorus is
not a longer chorus, it is a worse one. Eight minutes produces 17 sections
including post-chorus, solo, and breakdown.

Every stage after composition degrades rather than aborting. A vocal failure
yields an instrumental with an explanation attached, not a lost song.

---

## Frontend

React 18 + TypeScript + MUI in a Tauri 2 shell. 43 files, ~8.6k LOC,
15 pages.

- **`services/tauri.ts`** — typed bridge with graceful browser fallback, so
  the app runs in a plain browser during development
- **`ErrorBoundary`** at the root, reporting to the diagnostics backend
- Long operations poll `/advanced-export/jobs/{id}` and display the current
  stage

!!! warning "A feature you cannot reach is not shipped"
    The sidebar was a temporary drawer starting closed. On a desktop window
    **every** navigation link was hidden behind a hamburger — Song Studio was
    fully built, every endpoint worked, and it was undiscoverable. It is now
    permanent above ~900 px, and tests assert that every sidebar path has a
    matching route.

---

## Security

The app binds localhost by default, but `docker-compose` binds `0.0.0.0`, so
the boundaries are enforced rather than assumed.

**Path traversal.** Endpoints accepting file paths constrain them to project
directories. `Path(x).name` is not sufficient — on POSIX a backslash is a
legal filename character, so `..\..\windows\system32` passes straight
through. `utils/paths.py` normalises both separators and rejects NUL bytes,
drive prefixes, and Windows reserved device names.

This matters most in the song library, where `delete_song` calls
`shutil.rmtree`: a traversal bug there destroys data rather than leaking it.
Tests confirm a directory outside the library survives every escape attempt.

**Arbitrary file read.** `/advanced-export/audio/convert` once accepted any
path and handed it to ffmpeg — `/proc/self/environ` and `~/.ssh/id_rsa` were
both readable. Found in an audit and closed.

**Consent.** Voice conversion returns **403** without explicit
acknowledgement. Cloning a voice without permission causes real harm and is
increasingly unlawful; this is enforced in the engine, not just documented.

---

## Testing

628 tests across 24 files, ~6.3k LOC. Roughly 40% of the codebase.

The suite is weighted toward the classes of bug that actually occurred:

- **JSON extraction** — 18 cases of real local-model output
- **Path safety** — traversal against read *and* destructive operations
- **Graceful degradation** — every optional dependency, absent
- **Error reporting** — empty exceptions, lost stages, dropped metadata
- **Setup script parity** — 14 features asserted present in *both* scripts,
  because espeak-ng went missing from PowerShell for four releases and broke
  Windows generation
- **Frontend wiring** — routes registered, sidebar reachable, no orphan links

Verified where possible rather than mocked: MIDI round-trips through real
`midiutil` and `mido`, audio renders through real FluidSynth, LUFS is
measured by real `pyloudnorm`, SF2 presets are parsed from the actual
installed soundfonts.

Mocked only where the sandbox cannot reach: Ollama (a mock server returning
six styles of messy output), Hugging Face weights, Freesound, Wikipedia.

---

## Dependencies

Core is deliberately small: FastAPI, SQLAlchemy, Pydantic, httpx, numpy,
soundfile. Everything heavy is an extra.

| Extra | Adds |
| --- | --- |
| `audio` | MIDI in/out, LUFS measurement — small pure wheels |
| `export` | PDF charts, richer tagging |
| `vocals` | Piper, ONNX Runtime, voice-bank downloads |
| `analysis` | librosa (separate: pulls numba) |
| `neural` | PyTorch, transformers — ~2 GB |
| `server` | Rate limiting, real resource reporting |
| `production` | PostgreSQL, Redis, gunicorn |

System packages pip cannot provide: **ffmpeg**, **fluidsynth**, a **GM
soundfont**, **espeak-ng**. The setup scripts install all four.

Python 3.11–3.13. Enforced rather than claimed: every source file is parsed
with `ast.parse(feature_version=(3, 11))`, and a check rejects stdlib APIs
newer than the declared minimum.

---

## Known limits

**Rust is compiler-unverified.** The Tauri source parses with zero syntax
errors, but the toolchain is unavailable in the development sandbox, so the
API usage has never been compiled. Native installers require a machine with
Rust 1.85+.

**DiffSinger and RVC are implemented but unverified end-to-end.** Both need
user-supplied weights, and every voice bank export differs. DiffSinger
reports the actual input tensor names it found so the mapping can be
completed for a specific bank.

**Neural synthesis has never run.** Hugging Face is unreachable from the
sandbox. The code paths, device detection, and memory management are
tested against mocks; whether `MusicgenForConditionalGeneration.generate()`
accepts exactly the arguments passed is not confirmed.

**The in-process job queue and cache are per-process.** They stop being
coherent with more than one uvicorn worker. Redis is not optional at that
point.

**No authentication.** This is a localhost desktop backend. Exposing it
publicly requires auth that does not exist yet.

**General MIDI is a 1991 instrument list.** No theremin, no Mellotron, no
modular synth. Unresolved instruments route to sample search rather than
being forced onto a wrong program.

---

## Where to start reading

| Interest | File |
| --- | --- |
| The full pipeline | `services/song_generator.py` |
| Getting JSON from local models | `services/agents/base_agent.py` |
| Graceful degradation | `services/vocal_engines.py` |
| Path safety | `utils/paths.py` |
| What the app can do right now | `api/diagnostics.py` → `/readiness` |

`AUDIT.md` documents a full security and correctness audit, including the
bugs it found and the reasoning behind each fix.
