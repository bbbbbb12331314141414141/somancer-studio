# Client Build Fixes — v0.9.1

## Root cause

`src-tauri/` contained **only** `tauri.conf.json`. The entire Rust side of the
desktop app had never been generated in any of the eight phases, so:

```
$ pnpm build
✓ vite build succeeds
✗ tauri build → failed to watch .../src-tauri/Cargo.toml: No path was found
```

The web build was always fine. The desktop wrapper simply didn't exist.

---

## What was missing / broken

| # | Problem | Fix |
|---|---|---|
| 1 | No `Cargo.toml` — no Rust crate at all | Created with Tauri 2 deps + release profile tuning |
| 2 | No `build.rs` | Added (`tauri_build::build()`) |
| 3 | No `src/main.rs` / `src/lib.rs` | Added, with `windows_subsystem` guard so no console window appears on Windows |
| 4 | No `capabilities/` — Tauri 2 **requires** this or every command fails at runtime with opaque permission errors | Added `capabilities/default.json` scoped to `localhost:8000` |
| 5 | Rust plugins registered with **no matching JS packages** → runtime errors on call | Added `@tauri-apps/plugin-{dialog,fs,opener,shell}` |
| 6 | `pnpm-workspace.yaml` contained pnpm's literal placeholder `esbuild: set this to true or false` | Replaced with real booleans — **this alone broke every `pnpm <script>`** (see below) |
| 7 | `packages/shared/src/` was empty → `TS18003: No inputs were found` | Populated with real shared types |
| 8 | ESLint 9 can't read `.eslintrc.json` | Migrated to flat `eslint.config.js` |
| 9 | `eslint-plugin-react-hooks@4.x` crashes on ESLint 9 (`context.getSource is not a function`) | Bumped to `^5.0.0` |
| 10 | `pnpm build` ran `tauri build`, so the web build needed Rust unnecessarily | Split: `build` = web only, `build:desktop` = full native |
| 11 | 643 kB single bundle, chunk-size warning | Vendor chunking → largest chunk 341 kB, app code isolated at 133 kB |

### The one that broke everything

pnpm 11 runs an automatic dependency check before *any* script. That check runs
`pnpm install` internally, which exited **1** because of the malformed
`allowBuilds` block. Result: `pnpm build`, `pnpm lint`, `pnpm type-check` — all
dead, with a stack trace that pointed at pnpm internals rather than the config.

```yaml
# before — pnpm's own placeholder text, left in the file
allowBuilds:
  esbuild: set this to true or false

# after
allowBuilds:
  esbuild: true
  '@tauri-apps/cli': true
  lightningcss: true
```

---

## New Rust layer

Deliberately thin — all music/AI logic stays in the Python backend.

```
src-tauri/
├── Cargo.toml              Tauri 2, 5 plugins, reqwest (rustls)
├── build.rs
├── capabilities/
│   └── default.json        permission scope (required by Tauri 2)
├── src/
│   ├── main.rs             entry point
│   └── lib.rs              window setup + 3 commands
└── tauri.conf.json         bundle metadata, icon refs
```

**Commands exposed to the frontend:**

| Command | Returns |
|---|---|
| `app_info` | name, version, Tauri version, OS, arch |
| `backend_url` | backend base URL (env-overridable) |
| `check_backend` | health-check the FastAPI server, with a message telling the user how to start it |

`reqwest` uses **rustls**, not native-tls — no system OpenSSL headers needed,
which is a very common Linux build failure.

**Frontend bridge:** `src/services/tauri.ts` wraps all of it and degrades
gracefully in a plain browser, so `pnpm dev` (web) never throws.

---

## Commands

| Command | Needs Rust? | What it does |
|---|---|---|
| `pnpm dev` | no | Vite dev server on :5173 |
| `pnpm build` | no | Production web build |
| `pnpm type-check` | no | `tsc --noEmit` across packages |
| `pnpm lint` | no | ESLint 9 flat config |
| `pnpm dev:desktop` | **yes** | Native window with hot reload |
| `pnpm build:desktop` | **yes** | Installers: deb, AppImage, msi, nsis, dmg |

---

## Desktop build prerequisites

Only needed for `dev:desktop` / `build:desktop`.

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Linux system libraries
sudo apt-get install -y \
  libwebkit2gtk-4.1-dev \
  libgtk-3-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  patchelf \
  build-essential curl wget file libssl-dev
```

macOS: Xcode Command Line Tools. Windows: MSVC Build Tools + WebView2.

Check status any time with:
```bash
pnpm --filter @sonmancer/desktop exec tauri info
```

---

## Verified

```
pnpm install       exit 0   (esbuild postinstall now runs)
pnpm type-check    exit 0   clean, both packages
pnpm lint          exit 0   0 errors, 32 cosmetic warnings
pnpm build         exit 0   built in 23s
tauri info                  Rust project + all 5 plugins detected
```

Bundle after chunking:

```
index.html    1.67 kB │ gzip   0.70 kB
index.css     0.20 kB │ gzip   0.17 kB
icons.js      8.71 kB │ gzip   3.51 kB
index.js    133.13 kB │ gzip  40.16 kB   ← app code
react.js    160.53 kB │ gzip  52.41 kB   ← cached across app edits
mui.js      341.17 kB │ gzip 102.74 kB   ← cached across app edits
```

The remaining 32 lint warnings are unused imports. They're warnings, not errors,
and don't block anything — left alone deliberately rather than risk breaking
aliased imports with an automated sweep.
