# Code Audit — v1.0.2

Static analysis plus targeted probing of the bug classes that matter for
this codebase: parsing untrusted model output, handling user-supplied file
paths, and resource lifecycle.

**11 real bugs found and fixed.** Three would have caused data loss or
silent corruption; one was a security hole.

---

## Security

### Arbitrary file read — `POST /advanced-export/audio/convert`

**Severity: high** (mitigated by localhost-only default, but the backend
binds `0.0.0.0` in docker-compose)

The endpoint accepted any filesystem path and passed it to ffmpeg:

```json
{"source_wav": "/etc/passwd", "target_format": "mp3"}
```

ffmpeg would fail on that particular file, but `/proc/self/environ`,
`~/.ssh/id_rsa`, or any readable file could be converted and downloaded.
The same flaw existed in `batch_export` and `stems-zip`.

**Fixed** — new `aimusic/utils/paths.py` constrains all caller-supplied
paths to the project's own directories (`exports/`, `projects/`, `tmp/`,
`soundfonts/`, `logs/`, `plugins/`). Verified:

```
/etc/passwd                 -> HTTP 400
/proc/self/environ          -> HTTP 400
../../../../etc/passwd      -> HTTP 400
~/.ssh/id_rsa               -> HTTP 400
```

### Path traversal defence was OS-dependent

Download endpoints used `Path(filename).name`. On POSIX a backslash is a
legal filename character, so `..\..\windows\system32\config\sam` passed
through unchanged — safe on Linux by accident, not by design.

**Fixed** — `safe_filename()` normalises both separators explicitly and
rejects NUL bytes, drive-letter prefixes, and Windows reserved device names
(`CON`, `NUL`, `COM1`…).

---

## Data loss and corruption

### JSON extractor silently corrupted content

The old extractor stripped ``` globally:

```python
text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("```").strip()
```

That removed backticks from *inside* JSON string values:

```
{"note":"use ``` fences"}   ->   {'note': 'use fences'}
```

A lyric or production note containing backticks was silently altered.

It also used a greedy `\{.*\}` regex, which fails whenever prose contains
braces — and models say things like *"Structure {verse, chorus}: {...}"*.

**Fixed** — rewritten with balanced-delimiter scanning that tracks string
state and escapes, preferring fenced blocks and then the outermost
structure. Now handles 18/18 test cases, including four the old version
failed outright:

| Input | Old | New |
| --- | --- | --- |
| `{"note":"use ``` fences"}` | corrupted | preserved |
| `Consider {this} then: {"a":1}` | failed | parsed |
| `{'a': 1}` (single quotes) | failed | parsed |
| `{"a":1,}` (trailing comma) | failed | parsed |

The last two are extremely common local-model output and are a likely
cause of the composer failures reported in production.

Also added tolerant repair for Python literals (`True`/`None`) and smart
quotes.

### Tracks silently dropped from mixes

`mix_wav_files` used `zip(wav_paths, settings)`. Passing 3 WAVs with 2 mix
settings silently discarded the third track — very hard to notice in a
rendered mix.

**Fixed** — settings are padded to match, extras are logged, and the `zip`
is now `strict=True` so any future mismatch raises instead of truncating.

---

## Resource management

### httpx connection pool leaked on every AI request

14 endpoints each constructed `OllamaService()`, which creates an
`httpx.AsyncClient` owning a connection pool. `aclose()` was never called.
Sustained use exhausts file descriptors.

**Fixed** — a single shared instance via `get_ollama()`, closed by
`close_ollama()` in the FastAPI shutdown hook. Verified the client is
genuinely reused across calls.

---

## Correctness

### `JSONResponse(500, {...})` had reversed arguments

Both global exception handlers passed `500` as the *content* and the dict
as the *status code*. **Every unhandled exception raised a `TypeError`
instead of returning a 500 response.** Found only because a test happened
to trigger the handler.

### Deprecated `datetime.utcnow()` — 36 call sites

Returns a naive datetime that misrepresents UTC, and is scheduled for
removal. Replaced with timezone-aware `datetime.now(timezone.utc)` and a
`_utcnow()` helper for SQLAlchemy column defaults.

### Plugin errors vanished silently

`discover_and_register` swallowed every exception with `except: pass`, so a
malformed plugin simply never appeared with no explanation. Now logs the
plugin path and the specific error.

It also scanned every plugin directory **twice** — calling `discover()` and
discarding the result, then re-scanning.

### Undefined name in the Plugin SDK

`plugin_service.py` annotated `np.ndarray` without importing numpy. Harmless
at runtime (string annotations), but breaks `typing.get_type_hints()` and
any tooling that resolves them. Now guarded with `TYPE_CHECKING`, keeping
numpy optional.

---

## Also fixed

- Narrowed a bare `except Exception` when reading an HTTP error body
- Made `subprocess.run(..., check=False)` explicit where the return code is
  inspected deliberately
- `ClassVar` annotations on class-level constants in the harmony service
- 96 unused imports removed, import order normalised
- Exception chaining (`raise ... from exc`) added where it was missing
- JSX entity escaping in `OnboardingPage`

---

## An honest note

My first attempt at the exception-chaining fix was itself buggy — a script
added `from exc` outside the `except` scope, creating 12 undefined names
and breaking 8 tests. Ruff caught it immediately and it was reverted.

That is the argument for running static analysis rather than trusting a
careful-looking edit.

---

## Final state

```
ruff check aimusic/      All checks passed
pytest tests/            246 passed
tsc --noEmit             0 errors
eslint src               0 errors, 32 warnings (unused imports)
vite build               built in 21s
```

**54 new regression tests** (`test_audit_regressions.py`) covering JSON
extraction edge cases, path safety, endpoint hardening, shared-client
lifecycle, and timestamp correctness — so none of these classes can
silently return.

Test count: 192 → **246**.

---

## Deliberately not changed

Documented in `pyproject.toml` with reasons:

| Rule | Why |
| --- | --- |
| `B008` | FastAPI's `Depends()` in defaults is the documented pattern |
| `S104` | Binding `0.0.0.0` is intentional for docker-compose |
| `S603` | subprocess args are constructed internally, never from user strings |
| `PLW0603` | Module-level singletons for the shared client and caches |
| `S110` | One case: diagnostics must never mask the original error |
| `UP042` | `str, Enum` is used for Pydantic/SQLAlchemy compatibility |

---

## Not covered by this audit

- **Rust** — cannot compile here (toolchain blocked, Ubuntu ships 1.75 vs
  the 1.85 Tauri needs). Source parses with zero syntax errors; API usage is
  compiler-unverified.
- **Concurrency under load** — no load testing was performed. The job queue
  uses a lock correctly on inspection, but that is not the same as proven.
- **Real model output quality** — parsing robustness is now well covered;
  whether a given model produces *good music* is not something static
  analysis can answer.
