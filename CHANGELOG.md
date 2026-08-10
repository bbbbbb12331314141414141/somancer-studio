# Changelog

All notable changes to Sonmancer Studio.
Format follows [Keep a Changelog](https://keepachangelog.com/).

---

## [1.6.1] — Unfamiliar genres are researched and offered

Custom genres already appeared in Song Studio — both pages share one
selector that reads the library. What was missing was the other half: an
unknown genre typed there was passed straight through with no research and
no prompt.

### Added
- **`GET /genres/resolve`** — checks the library, researches the name if it
  is not there, and returns the profile with `needs_confirmation` set.
  **Nothing is saved.** Researching a name should not fill someone's library
  with every typo and passing idea.
- **Confirmation card** in the selector, showing the researched tempo, keys,
  instrumentation, and citations, with **Add to my library** or **Just use it
  this once**. Either choice uses the genre for the current song; adding it
  keeps the profile for next time.
- **Confidence labels** — `library`, `web-researched`, `from model knowledge`,
  or `uncertain` — so a recollection is never mistaken for a sourced answer.
- Degrades cleanly: with Ollama down an unknown genre is still usable as a
  style description, with a message explaining why there is no profile.

### Fixed
- **`/genres/resolve` was unreachable.** FastAPI matches in registration
  order, and `/genres/{genre_id}` was declared first, so `resolve` was parsed
  as an integer id and every request returned 422. Moved above the
  parameterised route, with a comment and a test guarding the whole class of
  ordering bug.
- **Research answering about a different genre would be saved under its
  name.** Asked about an obscure name, a model sometimes describes a
  neighbouring genre; saving that name is confusing and collides with any
  existing entry. The requested and researched names are now kept distinct,
  the profile is saved under the user's name, and the mismatch is reported.

### Tests
13 new tests covering library hits, case-insensitive lookup, that resolve
never writes, name preservation, degradation without Ollama, the
resolve-then-add round trip, and route shadowing. **585 passing** (was 572).

---

## [1.6.0] — Genre fusion and custom genres

Most interesting music sits between genres. A single dropdown cannot express
"neo-soul with trap drums".

### Added
- **Multi-genre selection.** Pick up to five and they blend into one profile
  the composer can use. Available in both the Genre Browser and Song Studio.
- **Honest conflict handling.** Where genres disagree the fusion says so
  instead of averaging into something that sounds like neither:
  - Neo-soul 70-95 × trap 130-150 → **140-150 BPM half-time**, because
    doubling the slower range overlaps the faster one. Comparing midpoints
    would miss this (1.7 ratio, not 2.0) and it is one of the most common
    fusions there is.
  - Ballad 60-70 × disco 100-110 → **warned as incompatible**, with the
    options spelled out.
- **Weighted blending.** The dominant genre supplies harmony and vocal style;
  the others supply rhythm and texture. Adjusting the balance reorders
  instrumentation and can switch which harmony is used.
- **Instrument provenance.** Instruments shared across sources rank first,
  since the arranger takes the first few. Hovering shows which genres each
  came from.
- **Custom genres.** Enter just a name and research fills the blanks while
  keeping anything you specified. Works with Ollama down — the genre is
  created from what you gave it and research is skipped.
- Endpoints: `POST /genres/fuse`, `POST /genres/custom`. Song generation
  accepts `genres` and `genre_weights`.

### Fixed
- **A 50/50 blend described itself as "led by"** the first genre. The balance
  threshold was a fixed 0.45 rather than relative to the genre count, so an
  even split never read as even.
- **A whitespace-only genre name created a genre called `""`.** Pydantic's
  `min_length` counts spaces, so `"   "` passed validation and was then
  stripped to nothing.

### Tests
38 new tests, weighted toward the tempo logic — silently averaging
incompatible ranges produces a song that sits wrong in every source genre
with nothing explaining why. **572 passing** (was 534).

---

## [1.5.2] — Navigation visibility

Song Studio was fully implemented, every endpoint worked, and it was
unreachable in practice.

### Fixed
- **The sidebar hid every feature behind a hamburger.** It was a temporary
  drawer starting closed, so on a desktop window no navigation was visible at
  all — you had to guess to click ☰ before discovering the app had a Song
  Studio, Mixing Console, or anything else.

  It is now **permanent on windows wider than ~900 px** and falls back to a
  drawer only on narrow ones. The hamburger is hidden where it is redundant.

- **The dashboard led with "Create New Project"**, an empty container, rather
  than the feature most people actually want. It now leads with **Create a
  song**, with the project workflow as the secondary action, and Song Studio
  appears as a card in the tools grid.

### Added
- Six tests that check the frontend wiring from the backend suite: that the
  page exists, the route is registered, the sidebar links to it, the sidebar
  is permanent on desktop, the dashboard surfaces it, and — catching the
  reverse failure — that every sidebar path has a matching route rather than
  rendering a blank page.

  A feature that exists but cannot be reached is not shipped, and nothing in
  the suite was checking that.

**534 passing** (was 528).

---

## [1.5.1] — Configuration loading fix

The backend refused to start whenever a real `.env` was present.

### Fixed
- **`Settings` rejected every undeclared key in `.env`.** The class used
  Pydantic v1's `class Config`; pydantic-settings v2 defaults to
  `extra="forbid"`, so the nine frontend and tooling keys in `.env.example`
  produced a wall of validation errors at import time:

  ```
  ValidationError: 9 validation errors for Settings
  vite_api_url  Extra inputs are not permitted [type=extra_forbidden]
  ```

  This only ever appeared on a machine with a `.env` — the test suite runs
  without one, which is why it was never caught here.

  Migrated to `SettingsConfigDict(..., extra="ignore")`. One `.env` serves
  both halves of the project, so keys one side does not recognise must not
  stop the other booting.

- **Declared the 14 missing settings** rather than only ignoring them, so
  `OLLAMA_TIMEOUT`, `DEFAULT_TEXT_MODEL`, `CORS_ORIGINS`, `MODEL_TEMPERATURE`
  and the rest actually take effect. Previously they were documented in
  `.env.example` and did nothing.

- **CORS origins were hardcoded in `main.py`**, which made the `CORS_ORIGINS`
  setting misleading. Now read from configuration.

- **Run instructions did not state the working directory.** The backend
  command runs from the project root, not `packages/backend`; both setup
  scripts now print the `cd` explicitly.

### Added
- Six regression tests: that `model_config` exists rather than `class Config`,
  that extras are ignored, that unknown keys do not crash, that every
  `.env.example` key is declared, that `cors_origins` parses to a list, and
  that `main.py` reads it instead of hardcoding.
- Troubleshooting entries for the validation error and the PowerShell
  directory confusion.

**528 passing** (was 522).

---

## [1.5.0] — Song Studio

Generate a complete song, up to eight minutes, with your own lyrics or lyrics
written for you — then keep, play, and delete what you make.

### Added
- **Song generator** — composes sections separately rather than asking for
  one long generation, because a single call for eight minutes returns eight
  minutes of the same eight bars. Each section carries its own energy, which
  drives instrumentation: an intro uses one instrument, a chorus uses six.
  That contrast is what makes a chorus feel like an arrival.
- **Structure planning** to eight minutes. Longer songs get *more* sections,
  not longer ones — 8 min produces 17 sections including post-chorus, solo,
  and breakdown. Verified: 60 s → 3 sections, 480 s → 17 sections at 7:12.
- **Your own lyrics**, with optional `[verse]` / `[chorus]` markers. Plain
  text becomes a verse rather than being rejected, because that is how people
  actually paste lyrics.
- **Song library** — every song gets a date-prefixed folder holding audio,
  MIDI, lyrics, vocals, and a manifest recording every parameter, so a song
  can be regenerated or varied instead of being an orphan WAV.
- **Deletion** — single, bulk, and a cleanup that removes only interrupted
  generations. Folders with audio but no manifest are kept, since the audio
  may still be wanted.
- **Song Studio page** — genre and length are enough to start; everything
  else sits behind "More options". The arrangement previews live as the
  length slider moves, so you see the shape before committing to minutes of
  generation. Inline playback, download, and a confirmation before deleting.
- 9 endpoints under `/studio/`.

### DiffSinger and RVC
Both now have real inference paths rather than raising.

- **DiffSinger** runs ONNX inference against the standard openvpi export,
  loading the voice bank's phoneme dictionary. A bank with a different layout
  fails with the actual input names it found, so the mapping can be completed.
- **RVC** uses `rvc-python`, reports whether the `.index` was found, and
  keeps the consent gate.

Neither is verified end-to-end: both need user-supplied weights, and every
export differs.

### Security
`delete_song` calls `shutil.rmtree`, so a traversal bug destroys data rather
than merely leaking it. Song ids are validated against the library root, path
separators rejected outright, and tests confirm a directory outside the
library survives every attempted escape.

### Tests
66 new tests covering structure planning, energy-driven instrumentation,
lyric parsing, manifest round-trips, corrupt-manifest handling, and
destructive traversal. **522 passing** (was 456).

---

## [1.4.0] — Sound library

Genre research produced text. `common_instruments: ["Fuzz Guitar"]` tells you
nothing you can play. This closes that gap.

### Added
- **Soundfont index** — parses SF2 `phdr` chunks directly, so the library
  knows what a soundfont *actually contains* rather than assuming General
  MIDI. FluidR3 carries a bank-8 "Funk Guitar" and "Detuned EP 1" that plain
  GM never mentions. 325 presets indexed from the two stock fonts. No
  network, no API key.
- **Instrument resolution** — a synonym vocabulary mapping how musicians
  actually write things ("Rhodes", "808", "fuzz", "upright bass") onto GM
  programs, with fuzzy fallback and per-match confidence.
- **Confidence threshold.** Fuzzy matching always returns something:
  "theremin" scores 0.55 against "Telephone Ring" and "Mellotron" 0.60
  against "Melodic Tom" — both wrong. Below 0.70 a match is treated as
  unresolved and routed to sample search, because a wrong sound loaded
  silently is worse than an honest gap.
- **Percussion kit matching by name**, with stem matching so "brushed drums"
  finds the Brush kit rather than whichever kit is indexed first.
- **Freesound provider** for what soundfonts cannot give you — room tone,
  vinyl crackle, field recordings. Free API key; every result carries its
  Creative Commons licence, and `commercial_only` restricts to CC0 and CC-BY.
- **Modernisation guidance** — eight production areas mapping period
  technique to contemporary practice, each with its rationale. Relevant areas
  are selected from the genre profile rather than dumping all eight.
- **`POST /library/palette`** — feed it a researched profile, get back
  presets, samples, vocal engines, and production notes. Closes the loop from
  research to sound.
- 8 endpoints under `/library/`.

### Fixed
- `read_presets()` called `os.path.getmtime()` before checking the file
  existed, crashing on a soundfont that vanished between discovery and read
  (removable drive, dangling symlink).

### Tests
50 new tests. SF2 parsing is verified against both synthetic fixtures and the
real installed soundfonts — bank/program decoding, percussion detection,
symlink deduplication, and malformed-file handling. **456 passing**
(was 406).

---

## [1.3.3] — Python version support verified

### Verified
Python 3.12 compatibility confirmed rather than assumed. All 17 core and
optional dependencies import cleanly and the full suite passes:

```
Python 3.12.3 — 406 passed, 0 skipped
fastapi 0.141 · sqlalchemy 2.0.51 · pydantic 2.13 · numpy 2.4.6
soundfile 0.14 · scipy 1.18 · librosa 0.11 · onnxruntime 1.28
midiutil · mido · pyloudnorm · reportlab · mutagen · pyttsx3
```

All 64 source files also parse under 3.11 grammar, and no stdlib API newer
than 3.11 is used — so `requires-python = ">=3.11"` is accurate.

### Added
- **Compatibility tests.** `ast.parse(feature_version=(3, 11))` across every
  source file, plus a check for stdlib APIs added in 3.12+ (`itertools.batched`,
  `pathlib.Path.walk`, `typing.override`, `copy.replace`) that grammar parsing
  would not catch. A fourth test fails if `requires-python` is raised without
  updating the checks — so the claim cannot drift.
- **CI matrix across 3.11, 3.12, and 3.13.** Previously only 3.12 was tested.
- `--with-analysis` verified end-to-end: librosa installs and imports cleanly.

### Changed
- **Both CI workflows now install the optional extras.** They previously
  installed `[dev]` plus three loose packages, so the integration and E2E
  suites skipped in CI exactly as they did locally — the tests written to
  catch third-party API drift were not running in the pipeline either.

---

## [1.3.2] — Setup installs optional dependencies

The setup script previously installed only `[dev]`, so a default install left
most advertised features silently unavailable — and **44 tests skipped**
because the code paths they cover had no dependencies to exercise.

### Changed
- **Default install now includes `[audio,export,vocals]`** — MIDI import and
  export, LUFS measurement, PDF lyric sheets. Small pure wheels, no reason to
  withhold them.
- **System packages installed too.** ffmpeg, fluidsynth, a GM soundfont, and
  espeak-ng cannot come from pip, and without them format conversion, audio
  rendering, and guide vocals do nothing. Handles apt, dnf, pacman, and brew;
  downloads a soundfont directly where no package exists.
- Feature availability went from **2 of 11** to **8 of 11** on a default
  install, and the previously-skipped tests now execute: **402 passing, 0
  skipped** (was 358 passed, 44 skipped).

### Added
- Flags on both scripts: `--minimal`, `--with-analysis`, `--with-neural`,
  `--with-ollama`, `--with-rust`, `--all`, `--no-system`, `--force`,
  and `--help`. PowerShell gains the matching `-Minimal`, `-WithNeural`,
  `-All`, and so on.
- **Availability report** at the end of setup listing each feature as
  present or missing, with the command to enable it.
- Graceful degradation: if installing with extras fails — likely on Python
  3.14, which lacks wheels for several packages — it retries with the core
  set and says which features that costs.
- `--no-system` for machines where apt/brew should not be touched.

---

## [1.3.1] — Setup robustness

Fixes a setup failure reported on Debian/Ubuntu with Node 22.

### Fixed
- **The setup script declared a broken pnpm working.** It used
  `command -v pnpm`, which passes because the corepack *shim file* exists —
  while every actual invocation crashed. The script printed `✓ pnpm:` with an
  empty version, then failed 40 lines later with a misleading
  "node_modules missing" error. It now verifies pnpm genuinely executes and
  returns a version.
- **Corepack incompatibility handled.** Debian and Ubuntu ship a corepack
  build that crashes on Node 22 with
  `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING`. The script now disables corepack
  and installs pnpm directly, then checks npm's global bin in case PATH has
  not refreshed.

### Added
- **npm workspaces** declared alongside pnpm's, so the monorepo installs and
  builds with either package manager. Verified: `npm install` (409 packages)
  and `npm run build` both succeed.
- `start-dev.sh` picks whichever package manager actually works.
- **Python 3.14 warning.** It is accepted, but several optional packages have
  no wheels for it yet. `PYTHON=python3.12 bash scripts/dev-setup.sh` pins a
  known-good interpreter.
- Failure messages now name the specific fix, including clearing a corepack
  cache left in `/root` by an earlier sudo run.

---

## [1.3.0] — Vocal synthesis engines

Replaces three "Coming Soon" placeholders — TTS stub, DiffSinger, RVC — with
a pluggable engine registry and six implementations.

### Added
- **eSpeak engine (default)** — a *pitched* guide vocal. Each line's average
  MIDI pitch maps onto espeak's pitch parameter and lines are placed at their
  own start beats, so the result follows the melody and sits in time.
  Robotic, but that is what a scratch vocal is for. No download, works
  headless.
- **pyttsx3 engine** — the OS voice, worth having on Windows and macOS.
- **Bark engine** — MIT licensed, so commercially usable. Attempts singing
  with ♪ markers, though pitch is not controllable so it will not follow
  your melody.
- **Parler-TTS engine** — Apache-2.0, 44.1 kHz, the best-sounding speech.
- **DiffSinger engine** — real singing synthesis via ONNX Runtime. Locates
  and loads a user-supplied voice bank, and reports the actual input tensor
  names so the mapping can be completed for that bank.
- **RVC engine** — voice conversion for an existing vocal, with a
  `POST /mix/vocals/convert` endpoint.
- Engines report licence, commercial-use status, download size, and whether
  they actually sing — so nobody builds a release on a voice bank whose terms
  forbid it.
- `[vocals]` dependency extra.

### Consent gate
Voice conversion returns **403** unless `consent_acknowledged` is true.
Cloning a voice without permission causes real harm and is unlawful in a
growing number of jurisdictions. This is enforced in the engine, not just
documented.

### Changed
- Default engine is now `espeak` rather than `tts_stub`. The old name still
  resolves as an alias, so existing calls keep working.
- `get_available_engines()` reads live availability from the registry, so an
  engine that becomes usable is reported without a restart.

### Fixed
- `synthesise()` accepted `**options` in the wrong signature, raising
  `NameError` on every call. Caught by the existing test suite.

### Honest limits
Only DiffSinger sings to your melody, and it needs a voice bank you supply.
Bark sings inconsistently and ignores pitch. eSpeak is a timing guide, not a
vocal. None of this replaces a singer, and the docs say so.

### Tests
36 new tests including real espeak rendering verified to land on the correct
beats with silence between lines, pitch-mapping monotonicity, and the consent
gate. **402 passing** (was 366).

---

## [1.2.1] — Dependency audit

An audit of the declared requirements found four things that were listed,
documented, or advertised but not actually working.

### Fixed
- **The `[neural]` extra was never added.** A string replacement in the 1.2.0
  work targeted `torch>=2.4.0` while the file said `torch>=2.0.0`, so it
  silently no-opped and reported success. `pip install "…[neural]"` would
  have failed for anyone who tried it.
- **Alembic was entirely non-functional.** Declared as a dependency,
  `alembic.ini` present, `versions/` empty — but no `env.py` and
  `script_location` pointed at a path that didn't exist. Any `alembic
  upgrade` failed. Now wired to application settings with an initial
  migration, verified to build all 13 tables on a fresh database.
- **LUFS was targeted but never measured.** The mastering agent produced
  chains aiming at -14 LUFS for Spotify; nothing measured the result, so
  "targeting -14 LUFS" meant writing -14 into a JSON field.
- **MIDI could only leave, never enter.** `midiutil` is write-only, so an
  existing `.mid` file could not be imported — ruling out the most common
  workflow of sketching in a DAW and developing here.
- **Key signatures were never written to MIDI**, so an export/import round
  trip always came back as C major.

### Added
- **`utils/loudness.py`** — ITU-R BS.1770-4 measurement via `pyloudnorm`:
  integrated LUFS, loudness range, true peak with 4x oversampling, and
  per-platform verdicts explaining the consequence ("Spotify will turn this
  down, so the extra loudness buys nothing"). Normalisation hits the target
  exactly while respecting the true-peak ceiling.
- **`utils/midi_import.py`** — `.mid` import via `mido`, producing the same
  `CompositionResult` the composer agent does, so imported and generated
  compositions are interchangeable. Optional quantisation, GM instrument
  mapping, percussion-channel detection, and a cheap `inspect_midi()` for
  previewing a file before committing to it. Lossy conversions are returned
  as warnings rather than silently discarded.
- **Restructured extras**: `[audio]`, `[export]`, `[analysis]`, `[neural]`,
  `[neural-diffusion]`, `[server]`, `[production]`, `[all]` — each with
  inline justification for why a package is there.
- `docs/dependencies.md` covering every group and what breaks without it.

### Changed
- `librosa` moved out of core into `[analysis]`: it pulls `numba`, which is
  a large compilation dependency the core app never needed.
- Generated migrations excluded from linting.

### Tests
34 new tests for loudness and MIDI import, including a full export/import
round trip across four key signatures. **366 passing** (was 332).

---

## [1.2.0] — Neural audio synthesis

FluidSynth renders MIDI accurately but sounds like MIDI. Hugging Face models
generate audio that sounds recorded rather than sequenced.

### Added
- **`services/neural_audio_service.py`** — 8 models across text-to-music,
  melody conditioning, text-to-audio, and vocals.
- **Melody conditioning** (`POST /neural/render-composition`) — the reason
  this is worth having. A FluidSynth render becomes the melodic guide for
  MusicGen-Melody, so you keep the harmony and structure you composed and
  gain timbre a soundfont cannot produce.
- **Job-queue-backed generation** — every request returns 202 with a job id.
  A 10-second clip is ~8s on a 4090 and ~4 minutes on CPU; no HTTP client
  should wait through that.
- **Licence propagation** — MusicGen weights are CC-BY-NC, so audio made
  with them cannot be sold. `commercial_use` travels with every model
  listing *and* every generated result rather than sitting in documentation
  nobody reads. Commercial-safe alternatives are flagged.
- **Memory management** — one model resident by default; loading a second
  evicts the first rather than exhausting VRAM mid-generation.
- **Device detection** — CUDA, MPS, and CPU with VRAM reporting and honest
  speed warnings.
- **Time estimates** (`GET /neural/estimate`) before committing to a run.
- 9 endpoints under `/neural/`, plus a readiness check.

### Design
Entirely optional. torch and transformers are imported only when a model is
requested, so the core app starts unchanged on a machine with neither. With
the extra absent, generation returns **501** with the install command and
everything else keeps working.

Melody files are resampled to the model's rate and downmixed to mono — a
stereo 48 kHz file fed straight in produces meaningless conditioning.

### Tests
46 new tests with mocked torch/transformers: device detection across
cuda/mps/cpu, model dispatch, eviction, melody resampling, clipping
prevention, licence propagation, and path traversal on the download and
melody parameters. **332 passing** (was 286).

---

## [1.1.0] — Web-grounded genre research

Asked about an obscure genre, a local model invents a fluent and entirely
false answer — a made-up BPM range, instruments never used, an origin decade
off by years. Genre research can now be grounded in retrieved sources.

**Off by default.** Sonmancer remains offline-first; this is opt-in via
`ENABLE_WEB_RESEARCH=true`, and with it off everything works exactly as
before, just flagged as *model knowledge*.

### Added
- **`services/research_service.py`** — provider-based retrieval:
  - **Wikipedia** (no key) — genre prose, CC BY-SA, URLs returned for attribution
  - **MusicBrainz** (no key) — genre taxonomy, rate-limited to their documented
    1 req/sec with a compliant User-Agent
  - **SearXNG** (no key) — self-hosted private meta-search
  - **Generic search API** — Tavily/Brave/Serper via bearer token
- **Grounded prompting** — retrieved text is injected before the question,
  with instructions to prefer it over recollection and never copy verbatim.
  Temperature drops 0.5 → 0.3 since the task becomes extraction, not recall.
- **Provenance on every result** — `web_researched`, `confidence`, and
  `citations`, surfaced in the UI as a green *Web-grounded* or grey
  *Model knowledge* chip with expandable sources.
- **New endpoints**
  - `GET  /genres/research/status` — providers and configuration
  - `POST /genres/research/lookup` — raw sources, no model invocation
  - `POST /genres/research/discover` — research a genre by name, optionally save
  - `POST /genres/{id}/research?use_web=` — per-request override
- **`GenreResearchPanel`** in the Genre Browser
- **`GenreService.get_genre_by_name()`** — case-insensitive, prevents duplicates
- Readiness check reporting research status

### Privacy
Only genre **names** are sent outward — never project data, lyrics, or audio.
Names are sanitised (control characters stripped, length capped) and results
cached 24 hours to minimise network traffic.

### Reliability
Research never breaks generation. A disabled service, missing internet, dead
provider, or unexpected exception all degrade to model knowledge with the
result flagged accordingly.

### Tests
40 new tests covering provider parsing, rate limiting, caching, aggregation,
failure isolation, context budgeting, and prompt grounding — all with mocked
HTTP. **286 passing** (was 246).

---

## [1.0.2] — Code audit

Static analysis plus targeted probing of parsing, path handling, and
resource lifecycle. **11 real bugs fixed.** Full report in `AUDIT.md`.

### Security
- **Arbitrary file read.** `/advanced-export/audio/convert` accepted any
  filesystem path and passed it to ffmpeg, so `/proc/self/environ` or
  `~/.ssh/id_rsa` could be read and downloaded. Same flaw in `batch_export`
  and `stems-zip`. All caller-supplied paths are now constrained to the
  project's own directories.
- **Path traversal defence was OS-dependent.** `Path(x).name` does not strip
  backslashes on POSIX. Replaced with an explicit normaliser that also
  rejects NUL bytes, drive prefixes, and Windows reserved device names.

### Fixed — data loss
- **JSON extractor corrupted content.** Global ``` stripping removed
  backticks from inside JSON string values, silently altering lyrics.
  Rewritten with balanced-delimiter scanning that tracks string state.
- **Extractor failed on common model output.** Single quotes, trailing
  commas, Python literals, smart quotes, and prose containing braces all
  failed to parse — a likely cause of the composer errors. Now 18/18 cases
  pass, with tolerant repair.
- **Tracks silently dropped from mixes.** `zip(paths, settings)` discarded
  extra tracks when fewer mix settings were supplied. Settings are now
  padded and the zip is `strict=True`.

### Fixed — correctness
- **`JSONResponse(500, {...})` had reversed arguments** in both global
  exception handlers, so every unhandled error raised a `TypeError` instead
  of returning a 500 response.
- **httpx connection pool leaked per request.** 14 endpoints each built
  their own `OllamaService`; none were closed. Now a shared client with a
  shutdown hook.
- **Deprecated `datetime.utcnow()`** at 36 call sites → timezone-aware
  `datetime.now(timezone.utc)`.
- **Plugin load errors vanished silently** (`except: pass`), and plugin
  directories were scanned twice per discovery.
- **Undefined `np` annotations** in the Plugin SDK, now `TYPE_CHECKING`-guarded.

### Housekeeping
- 96 unused imports removed; import order normalised
- `ruff` config modernised, with every remaining ignore justified inline
- Exception chaining restored where it had been dropped
- JSX entity escaping in `OnboardingPage`

### Tests
54 new regression tests (`test_audit_regressions.py`). **246 passing**
(was 192).

---

## [1.0.1] — AI error handling

Fixes found from a real Ollama run that produced a truncated log line:

    WARNING [composer] JSON parse attempt 1 failed:
            [composer] Ollama error: Generation failed:

### Fixed
- **Error messages were being silently truncated.** Every httpx timeout and
  connection exception stringifies to an empty string, so
  `f"failed: {exc}"` produced a colon followed by nothing. All messages now
  lead with the exception type.
- **Timeouts were retried three times.** A 600 s timeout retried twice meant
  30 minutes of waiting before the user saw an error. Timeouts and
  connection failures now surface immediately; only JSON parse failures
  retry.
- **Default timeout raised 120 s → 600 s.** 120 s was too short for local
  CPU composition and was the most common cause of the failure above.
  Configurable via `OLLAMA_TIMEOUT`.
- **`JSONResponse(500, {...})` had its arguments reversed** in both global
  exception handlers, so *every* unhandled error raised a `TypeError`
  instead of returning a 500 response.
- **One bad track destroyed a whole composition.** The composer now keeps
  the tracks that succeeded and reports which failed. It only raises if
  every track fails.
- **A failed planning call aborted the request.** It now falls back to a
  diatonic progression appropriate to the key.

### Added
- `OllamaTimeout` and `OllamaUnavailable` exception types so callers can
  distinguish "too slow" from "not running".
- HTTP status mapping: **504** timeout, **503** Ollama down, **502**
  unusable model output.
- Parse failures now log what the model actually returned, so you can see
  whether it emitted prose, a fence, or nothing.
- Empty model responses are detected and reported rather than parsed.
- `OLLAMA_TIMEOUT` documented in `.env.example`; 504/502 troubleshooting
  added to the docs.

### Tests
28 new regression tests (`test_ai_error_handling.py`) covering empty
exception messages, error classification, retry policy, and composer
resilience. **179 passing** (was 162).

---

## [1.0.0] — Release

First stable release. The full pipeline is verified end to end.

### Added
- **Code signing pipeline** — release workflow with macOS Developer ID +
  notarization, Windows Authenticode, and Tauri updater signatures. Every
  credential is optional: absent them the build succeeds and produces
  unsigned artifacts with a warning rather than failing.
- **`docs/SIGNING.md`** — how to obtain each certificate, what it costs, and
  what users see if you ship unsigned.
- **macOS entitlements** — hardened runtime with JIT and unsigned executable
  memory, both required by the WebView.
- **`scripts/set-version.sh`** and **`set-version.ps1`** — set the version
  across all 11 files that declare it. Verified byte-identical output, so a
  release cut on Windows matches one cut on Linux.
- **`scripts/preflight.sh`** and **`preflight.ps1`** — run the full CI gate
  locally: version consistency, changelog, icons, Rust project, tests, types,
  build, signing secrets, git state.

### Fixed
- `set-version.sh` left three version strings stale: the `main.py` module
  docstring, its startup log line, and the browser-mode fallback in
  `services/tauri.ts`. That last one meant the web build reported the wrong
  version from `getAppInfo()`. Found while writing the PowerShell port.
- **SHA256SUMS** generated and attached to every release.
- Signature verification steps in CI that warn loudly when a binary is
  unsigned rather than shipping it silently.

### Verified this release
- All 7 AI agents run against a mock Ollama returning deliberately messy
  output — markdown fences, preambles, trailing commentary, malformed JSON.
- FluidSynth renders real audio: 24 s, RMS 0.11, confirmed audible.
- Full chain: brief → research → lyrics → compose → harmony → mix plan →
  master chain → MIDI → WAV → MP3/FLAC/OGG.
- 162 tests passing.

---

## [0.9.0] — Release Candidate

Phase 9. Focus: diagnostics, first-run experience, and release automation.

### Added
- **Diagnostics service** — local-only error log with a ring buffer and
  rotating JSONL file. No telemetry, no analytics, nothing leaves the machine.
- **Crash report export** — one-click redacted bundle for bug filing.
  Home paths become `~`; credential-shaped fields are replaced.
- **Readiness checks** (`/diagnostics/readiness`) — probes every optional
  subsystem (ffmpeg, FluidSynth, soundfonts, Ollama, midiutil, reportlab)
  and returns the exact install command for anything missing.
- **System Check page** (`/welcome`) — first-run screen showing what works,
  with copy-to-clipboard fix commands.
- **ErrorBoundary** — React crashes now show a recoverable screen with stack
  trace instead of a white page, and are logged alongside backend errors.
- **Release workflow** — cross-platform installers via GitHub Actions:
  Linux (deb, AppImage), Windows (msi, nsis), macOS (dmg, Intel + Apple Silicon).
- **Documentation site** — MkDocs Material config.
- **Troubleshooting guide** — every issue hit during development, with causes.

### Changed
- Unhandled backend exceptions now route into the diagnostics log.
- Version assertions in tests read `app.version` rather than a hard-coded
  string, so releases no longer require editing tests.
- Ollama reachability uses a raw socket probe instead of an HTTP client —
  HTTP libraries honour proxy env vars and can hang past their timeout.

### Tests
137 passing (was 112).

---

## [0.8.1] — Client build fixes

### Fixed
- **`src-tauri/` had no Rust project.** Only `tauri.conf.json` existed, so
  `tauri build` failed immediately. Added `Cargo.toml`, `build.rs`,
  `src/main.rs`, `src/lib.rs`, and `capabilities/default.json`.
- **`pnpm-workspace.yaml` contained pnpm's literal placeholder text**
  (`esbuild: set this to true or false`). Because pnpm 11 runs a dependency
  check before every script, this broke `pnpm build`, `pnpm lint`, and
  `pnpm type-check` — all with a stack trace pointing at pnpm internals.
- Rust plugins registered without their JS counterparts installed.
- `packages/shared/src/` was empty → `TS18003`.
- ESLint 9 can't read `.eslintrc.json` → migrated to flat config.
- `eslint-plugin-react-hooks@4.x` crashes on ESLint 9 → bumped to v5.
- 643 kB single bundle → vendor chunking, app code isolated at ~140 kB.

### Changed
- `pnpm build` is now web-only (no Rust needed);
  `pnpm build:desktop` produces native installers.

---

## [0.8.0] — Polish & Performance

Phase 8.

### Added
- LRU cache with TTL for genres, models, and platform targets.
- System API: info, detailed health, cache management, directory init.
- Dark / light / system theme with persistence.
- Global keyboard shortcuts (⌘K, ⌘P, ⌘G, ⌘A, ⌘M, ⌘E, ⌘,).
- Complete icon and brand asset set — 40 files generated from code, with
  optical sizing so 16px icons stay legible.

---

## [0.7.0] — Advanced Export

Phase 7.

### Added
- Multi-format audio export: WAV, FLAC, MP3, OGG, AAC, AIFF via ffmpeg.
- `.sonmancer` project archives (ZIP with metadata, audio, MIDI, lyrics).
- Lyrics export to TXT and formatted PDF.
- Stems ZIP bundling.
- Background job queue with progress tracking and cancellation.

---

## [0.6.0] — Plugin SDK & Harmonies

Phase 6.

### Added
- Plugin SDK v1.0 with 8 plugin types and dynamic Python loading.
- `EffectPlugin`, `GeneratorPlugin`, `AIPlugin` base classes.
- Rule-based vocal harmony generation (2–4 parts) with voice-range
  enforcement and smooth voice leading.

---

## [0.5.0] — Mix & Mastering

Phase 5.

### Added
- Mix Engineer agent — per-track EQ, compression, panning, sends.
- Mastering Engineer agent — chains targeting 9 platform loudness standards.
- Stem export service with automatic track grouping.
- Vocal synthesis foundation (TTS stub; DiffSinger/RVC planned).

---

## [0.4.0] — Audio Rendering

Phase 4.

### Added
- FluidSynth MIDI → WAV rendering with SF2 soundfonts.
- Canvas piano roll editor with draw/select/erase tools.
- SVG waveform display with click-to-seek.
- In-app playback transport.

---

## [0.3.0] — AI Core

Phase 3.

### Added
- Ollama client with streaming, chat, and model management.
- Four AI agents: Songwriter, Composer, Producer, Genre Researcher.
- AI Studio page with lyrics, composition, and song-brief tabs.
- MIDI file export.

---

## [0.2.0] — Editors & Genres

Phase 2.

### Added
- Project creation form, detail editor, song editor.
- Lyrics CRUD with section grouping.
- Genre browser with 15 seeded genres and live search.

---

## [0.1.0] — Core Platform

Phase 1. Project/song CRUD, React shell, database integration.

---

## [0.0.1] — Foundation

Phase 0. Monorepo, CI/CD, database schema, documentation.
