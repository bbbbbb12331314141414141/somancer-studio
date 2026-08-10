# Linux Setup Fixes — v0.8.1

## Why the original script failed

| # | Problem | Fix |
|---|---|---|
| 1 | Script hard-coded `python3.11`; most systems ship 3.12/3.13 | Auto-detects `python3.13 → 3.12 → 3.11 → python3` |
| 2 | Used `source venv/bin/activate`, which fails under `/bin/sh` | Calls `venv/bin/pip` and `venv/bin/python` directly — no activation needed |
| 3 | `set -e` aborted on pnpm's harmless `ERR_PNPM_IGNORED_BUILDS` exit code | pnpm call made non-fatal; real failure detected by checking `node_modules` exists |
| 4 | pnpm 10/11 moved settings out of `package.json` | `onlyBuiltDependencies` moved to `pnpm-workspace.yaml` + lockfile settings |
| 5 | `@tauri-apps/plugin-http@^0.1.0` doesn't exist | Upgraded all Tauri deps to v2.x |
| 6 | Vite config required `terser` (optional dep) and wrote outside project root | Switched to `esbuild` minifier, `outDir: dist` |
| 7 | `tsconfig.json` referenced missing `tsconfig.node.json` | Reference removed, `types: ["vite/client"]` added |
| 8 | SQLAlchemy 2.0 reserves `metadata` on declarative models → app wouldn't import | Renamed attribute to `meta`, DB column still `"metadata"` |
| 9 | `declarative_base()` deprecated | Now uses `class Base(DeclarativeBase)` |
| 10 | `Lyrics` model missing `created_at`/`updated_at` its schema required → 404s | Timestamps added |
| 11 | Test fixtures broke under SQLAlchemy 2.0 (service commits ended outer transaction) | Shared `conftest.py` with per-test in-memory SQLite + `StaticPool` |
| 12 | Tests imported `engine` from `models.entities` where it doesn't live | Imports corrected to `aimusic.db` |

## Version updates

| Component | Before | After |
|---|---|---|
| Python | 3.11 | **3.12** (accepts 3.11–3.13) |
| Node.js | 18 | **22 LTS** |
| pnpm | 8 | **10+** |
| Tauri | 1.5 | **2.9** |
| FastAPI | 0.109 | 0.115+ |
| uvicorn | 0.27 | 0.32+ |
| numpy | 1.24 | 2.0+ |
| pytest | 7 | 8+ |
| TypeScript target | ES2020 | **ES2022** |
| Docker base | `python:3.11-slim` | **`python:3.12-slim`** |
| CI Node / Python | 18 / 3.11 | **22 / 3.12** |

## Verified working

```
✓ bash scripts/dev-setup.sh          → exit 0
✓ Backend imports                    → v0.8.0
✓ pytest tests/                      → 112 passed
✓ uvicorn boots + /health responds   → 200 OK
✓ 66 API endpoints registered
✓ tsc --noEmit                       → 0 errors
✓ vite build                         → 643 kB bundle, built in 18s
```

## Quick start

```bash
unzip sonmancer-studio-v0.8.1-fixed.zip
cd sonmancer-studio-phase0
bash scripts/dev-setup.sh
bash scripts/start-dev.sh
```

If Python or Node are missing, the script now tells you the exact install command for your OS instead of failing silently.
