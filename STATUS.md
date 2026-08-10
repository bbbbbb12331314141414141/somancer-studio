# Verification Status — v0.9.2

## Now actually verified

Every item below was **executed**, not just written:

| Capability | Evidence |
| --- | --- |
| **All 7 AI agents** | Run against a mock Ollama returning realistically messy output |
| **Agent JSON parsing** | Survives markdown fences, chatty preambles, trailing commentary, bare fences, and malformed JSON (retry recovers) |
| **MIDI generation** | Files that `file(1)` identifies as *Standard MIDI data (format 1)* |
| **FluidSynth rendering** | Real audio: 24 s render, RMS 0.11 — confirmed audible, not silence |
| **Waveform analysis** | Real 440 Hz sine; envelope correct, peaks normalised |
| **Audio mixing** | Two WAVs summed, no clipping |
| **Format conversion** | Real ffmpeg → MP3, FLAC, OGG |
| **Vocal harmony** | 4-part generation from an AI-composed melody |
| **Full pipeline** | brief → research → lyrics → compose → harmony → mix plan → master chain → MIDI → audio → MP3/FLAC/OGG |
| **Rust source** | Parses cleanly under `rustc` — 0 syntax errors |
| **Backend** | 162 tests pass |
| **Frontend** | 0 type errors, builds in ~20 s |

## Bugs this verification found

Five real bugs that 137 passing tests had missed:

1. **MIDI writer was completely broken.** Called `addProgramChange(track=...)`
   when midiutil's parameter is `tracknum`. *Every MIDI export would have
   crashed on first use.*
2. **Time signature encoded wrong.** The MIDI spec stores the denominator as
   a power-of-two exponent (4 → 2, 8 → 3), not the literal number.
3. **Waveform display and mixing demanded FluidSynth.** Neither uses it.
   Users without it were blocked from features needing only numpy/soundfile.
4. **Redundant `Synth()` object** opened an ALSA sequencer on every render,
   producing alarming errors on headless machines. Removed —
   **`pyfluidsynth` is no longer a dependency at all.**
5. **Empty compositions rendered to silence** instead of returning 422.

## Still unverified

| Area | Why | Risk |
| --- | --- | --- |
| **Real LLM output** | Ollama's servers are unreachable from this sandbox. Agents were tested against a mock that mimics messy formatting, but not against genuine model reasoning. | **Medium.** Parsing is proven robust; *content quality* is not. Expect prompt tuning. |
| **Rust compilation** | `static.rust-lang.org` returns 403 here. Ubuntu ships Rust 1.75; modern crates need 1.85+ (`edition2024`). | **Medium.** Source parses, but Tauri API usage is compiler-unverified. |
| **Native installers** | Requires the above. | **Medium.** Release workflow untested. |
| **Vocal synthesis** | TTS stub only; DiffSinger/RVC raise `NotImplementedError`. | **Known gap**, by design. |

## Test suite

| File | Tests | What it proves |
| --- | --- | --- |
| `test_pipeline_e2e.py` | 12 | All agents + full pipeline against messy LLM output |
| `test_integration_real.py` | 13 | Real midiutil, FluidSynth, ffmpeg, numpy — no mocks |
| `test_diagnostics.py` | 25 | Redaction, ring buffer, readiness |
| ...19 other files | 112 | API, CRUD, plugins, harmony, cache, export |
| **Total** | **162** | |

`tests/mock_ollama.py` is the important piece: it returns output in six
different messiness styles, cycling per request, because a mock that returns
perfect JSON proves nothing about a parser that must handle real models.

## Before tagging v1.0

- [ ] Run against real Ollama — verify output *quality*, tune prompts
- [ ] `cargo build` on a machine with Rust 1.85+
- [ ] Produce one installer per platform
- [ ] Code signing (Apple Developer ID, Windows certificate)
- [ ] Plugin sandboxing — `permissions` is declarative only
