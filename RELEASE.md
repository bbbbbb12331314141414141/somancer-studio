# Releasing Sonmancer Studio

## TL;DR

**Linux / macOS**

```bash
bash scripts/set-version.sh 1.0.0     # updates all 11 files that declare a version
$EDITOR CHANGELOG.md                  # add the entry
bash scripts/preflight.sh             # runs the whole CI gate locally
git commit -am "release: v1.0.0"
git tag -a v1.0.0 -m "Sonmancer Studio v1.0.0"
git push origin main --tags
```

**Windows**

```powershell
.\scripts\set-version.ps1 1.0.0       # same 11 files, byte-identical result
notepad CHANGELOG.md
.\scripts\preflight.ps1
git commit -am "release: v1.0.0"
git tag -a v1.0.0 -m "Sonmancer Studio v1.0.0"
git push origin main --tags
```

The `.ps1` scripts are verified to produce output identical to their bash
counterparts, so a release cut on Windows is indistinguishable from one cut
on Linux.

The tag triggers `.github/workflows/release.yml`, which verifies, builds four
platforms, signs whatever it has credentials for, generates `SHA256SUMS`, and
opens a **draft** release for you to review before publishing.

---

## Signing status

**Signing is entirely optional.** Every credential is checked with a
fallback: if a secret is absent the build still succeeds and the job log
carries a warning. You get working installers either way.

| Platform | Unsigned | Signed |
| --- | --- | --- |
| Linux | No warning at all | n/a — not part of the model |
| Windows | SmartScreen once per version | Clean install |
| macOS | Gatekeeper blocks; right-click → Open | Clean install |

To sign, see **[docs/SIGNING.md](docs/SIGNING.md)** — it covers what each
certificate costs, how to obtain it, and how to convert it into a repository
secret.

The one credential worth setting up immediately is **free**: the Tauri
updater keypair. Without it the in-app updater cannot verify releases.

```bash
pnpm --filter @sonmancer/desktop exec tauri signer generate -w ~/.tauri/sonmancer.key
```

> Back that private key up offline. Lose it and every existing install will
> reject all future updates. There is no recovery.

---

## What the workflow does

| Job | Runs on | Purpose |
| --- | --- | --- |
| `verify` | ubuntu | Backend tests, type-check, lint, frontend build. **Gate** — nothing proceeds if this fails. |
| `build` | 4 platforms | Native installers, signed if credentials present, plus signature verification |
| `checksums` | ubuntu | `SHA256SUMS` for every published artifact |
| `docker` | ubuntu | Backend container image |

Build matrix:

| Runner | Output |
| --- | --- |
| ubuntu-22.04 | `.deb`, `.AppImage` |
| windows-latest | `.msi`, `-setup.exe` |
| macos-latest | `_aarch64.dmg` (Apple Silicon) |
| macos-13 | `_x64.dmg` (Intel) |

---

## Preflight

`scripts/preflight.sh` (or `preflight.ps1` on Windows) checks eight things
before you tag:

1. **Version consistency** across all 10 declaring files
2. **Changelog** has an entry for this version
3. **Bundle icons** all present
4. **Rust project** complete, and `cargo check` if the toolchain is new enough
5. **Backend tests** pass
6. **Frontend** type-checks and builds
7. **Signing secrets** present (informational)
8. **Git** tree clean and the tag unused

It exits non-zero on any failure, so it's safe to chain into other commands.

Both accept a fast mode that skips the slow steps when you only want to
check configuration:

```bash
bash scripts/preflight.sh              # full run
.\scripts\preflight.ps1 -SkipTests     # config checks only (Windows)
.\scripts\set-version.ps1 1.1.0 -DryRun  # preview changes without writing
```

---

## If you ship unsigned

Include this in the release notes:

> **Windows** — SmartScreen may warn on first run. Click **More info → Run
> anyway**. Verify your download against `SHA256SUMS` first.
>
> **macOS** — Gatekeeper will block the app. Right-click it and choose
> **Open**, or run `xattr -cr "/Applications/Sonmancer Studio.app"`.
> Verify your download against `SHA256SUMS` first.

Saying this plainly is better than users assuming the app is malware.

---

## Post-release

- [ ] Publish the draft release once artifacts are reviewed
- [ ] Confirm `SHA256SUMS` is attached
- [ ] Download and install on at least one real machine per platform
- [ ] Verify the backend starts and `/api/v1/health` responds
- [ ] Check the **System Check** screen reports subsystems correctly
- [ ] Tag the docs site if versioning documentation
