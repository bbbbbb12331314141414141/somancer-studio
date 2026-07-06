# Somancer Studio — Phase 0 Detailed Task Breakdown

## Week 1: Repository & Architecture

### Day 1–2: Repository Setup
- [ ] Create GitHub repository (or local Git with remote)
- [ ] Initialize pnpm monorepo at root
- [ ] Create directory structure:
  ```
  sonmancer-studio/
  ├── packages/
  │   ├── desktop/          (Tauri + React)
  │   ├── backend/          (FastAPI)
  │   └── shared/           (TypeScript types, Python enums)
  ├── .github/
  │   └── workflows/        (CI/CD)
  ├── docs/
  ├── docker/
  ├── scripts/
  ├── pnpm-workspace.yaml
  ├── .eslintrc.json
  ├── .prettierrc.json
  └── README.md
  ```
- [ ] Set up `.gitignore` (node_modules, dist, build, .env, venv, __pycache__)

**Deliverables:**
- Working Git repository with standard branching (main, develop, feature/*)
- Directory structure ready for development
- `.gitignore` configured

---

### Day 3–4: Monorepo & Build Infrastructure
- [ ] Create root `pnpm-workspace.yaml`
- [ ] Create root `package.json` with shared dev dependencies:
  - TypeScript, ESLint, Prettier
  - Husky, lint-staged (pre-commit hooks)
- [ ] Create `packages/backend/pyproject.toml` with:
  - FastAPI, uvicorn, SQLAlchemy, pydantic
  - pytest, black, ruff
  - python-dotenv, aiofiles
- [ ] Create `packages/desktop/package.json` with:
  - Tauri 2, React, TypeScript, Vite
  - React Router, Material-UI (or custom theme starter)
  - axios for HTTP
- [ ] Create `packages/shared/package.json` for shared types

**Deliverables:**
- Monorepo fully configured and installable via `pnpm install`
- Backend and desktop can build independently

---

### Day 5: Linting & Code Standards
- [ ] Configure `.eslintrc.json` (TypeScript strict, React rules)
- [ ] Configure `.prettierrc.json` (2-space indent, semicolons, trailing commas)
- [ ] Configure `pyproject.toml` for Black and Ruff
- [ ] Create `.editorconfig` for consistency across IDEs
- [ ] Set up Husky hooks:
  - Pre-commit: lint-staged (ESLint, Prettier, Ruff, Black)
  - Pre-push: run tests
- [ ] Add npm scripts to root `package.json`:
  - `pnpm lint` (all packages)
  - `pnpm format` (all packages)
  - `pnpm test` (all packages)
  - `pnpm build` (all packages)

**Deliverables:**
- Automated formatting and linting
- Pre-commit hooks prevent bad code from being pushed
- Consistent code style across TypeScript and Python

---

## Week 2: CI/CD & Local Development Environment

### Day 1–2: GitHub Actions CI/CD
- [ ] Create `.github/workflows/test.yml`:
  - Lint frontend (ESLint)
  - Format check frontend (Prettier)
  - Lint backend (Ruff)
  - Format check backend (Black)
  - Run backend unit tests (pytest)
  - Run desktop tests (if any)
- [ ] Create `.github/workflows/build.yml`:
  - Build desktop (Tauri desktop + web)
  - Build backend (Docker image)
  - Upload artifacts (releases, docker images)
- [ ] Add branch protection rules (require CI pass before merge)

**Deliverables:**
- GitHub Actions pipelines
- Automated testing on every PR
- Build artifacts generated automatically

---

### Day 3–4: Docker & Local Development
- [ ] Create `docker/backend.Dockerfile`:
  - Python 3.11 slim
  - Install dependencies from `pyproject.toml`
  - Expose port 8000
  - Run FastAPI with `uvicorn`
- [ ] Create `docker-compose.yml`:
  - FastAPI service (backend, port 8000)
  - SQLite service (or PostgreSQL for later)
  - Ollama service (optional, can be external)
  - Volumes for persistent data
- [ ] Create `scripts/dev-setup.sh` (Linux/Mac):
  - Install pnpm, Python venv, Rust (for Tauri)
  - Run `pnpm install`
  - Set up `.env` from `.env.example`
  - Start Docker Compose
- [ ] Create `scripts/dev-setup.ps1` (Windows):
  - Same as above but PowerShell

**Deliverables:**
- One-command local dev setup (`pnpm dev` or bash script)
- Consistent dev environment via Docker
- Ready for frontend + backend simultaneous development

---

### Day 5: Documentation Structure
- [ ] Create `docs/`:
  - `ARCHITECTURE.md` (high-level system design)
  - `SETUP.md` (how to get dev environment running)
  - `API.md` (FastAPI endpoint stubs)
  - `DATABASE.md` (schema reference)
  - `CODING_STANDARDS.md` (style guide)
  - `PHASES.md` (roadmap + current status)
- [ ] Create `CONTRIBUTING.md` (how to contribute, PR process)
- [ ] Create root `README.md` (project vision, quick start)

**Deliverables:**
- Developer onboarding complete in 30 minutes
- Clear reference for all major systems
- Contribution guidelines documented

---

## Phase 0 Deliverables Summary

| Deliverable | Responsibility | Status |
| --- | --- | --- |
| Git repo with branching strategy | Day 1–2 | ✅ |
| Monorepo structure (pnpm + workspaces) | Day 3–4 | ✅ |
| Linting, formatting, pre-commit hooks | Day 5 | ✅ |
| GitHub Actions CI/CD | Week 2 Day 1–2 | ✅ |
| Docker + docker-compose | Week 2 Day 3–4 | ✅ |
| Development documentation | Week 2 Day 5 | ✅ |

---

## Success Criteria

- [ ] Clone repo, run `pnpm install`, code runs without errors
- [ ] Create feature branch, make a change, commit → pre-commit hook runs linting
- [ ] Push to GitHub → CI pipeline passes all checks
- [ ] `docker-compose up` brings up working backend + database
- [ ] First-time developer can follow `SETUP.md` and have dev env in < 30 min
- [ ] All code has typed interfaces (TypeScript, Python type hints)
- [ ] `pnpm build` produces desktop app binary + backend Docker image

---

## Risks & Mitigations

| Risk | Mitigation |
| --- | --- |
| Tauri + pnpm compatibility issues | Test Tauri scaffolding early; use Vite as bundler |
| Docker networking issues on Windows | Use `docker-compose.yml` with explicit service names; test WSL2 backend |
| Python venv conflicts with Docker | Use Docker for backend in dev; only use local venv for scripts |
| Husky hooks slow down commits | Configure lint-staged to run only on changed files |

---

## Next Steps (Handoff to Phase 1)

Once Phase 0 is complete:
1. Backend team creates API stubs for Project, Track, Lyrics, etc. (CRUD endpoints)
2. Frontend team creates React routing and page stubs (Dashboard, Settings, etc.)
3. Database team populates initial schema and migration scripts
4. AI team sets up Ollama mock for development
5. Audio team establishes rendering pipeline architecture

