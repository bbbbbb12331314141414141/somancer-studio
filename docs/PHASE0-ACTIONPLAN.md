# Somancer Studio — Phase 0 Immediate Action Plan

## Start Now (Next 30 Minutes)

### 1. Initialize Repository
```bash
mkdir sonmancer-studio && cd sonmancer-studio
git init
git config user.name "Your Name"
git config user.email "your@email.com"

# Create initial structure
mkdir -p packages/{desktop,backend,shared}
mkdir -p docker .github/workflows docs scripts
```

### 2. Copy Phase 0 Files
Copy these files into your project root:
- `pnpm-workspace.yaml` → Root
- `package.json` → Root
- `.eslintrc.json` → Root
- `.prettierrc.json` → Root
- `.editorconfig` → Root
- `.gitignore` → Root
- `.env.example` → Root
- `docker-compose.yml` → Root
- `README.md` → Root
- `SETUP.md` → `docs/`
- `ARCHITECTURE.md` → `docs/`
- `API.md` → `docs/`
- `CODING_STANDARDS.md` → `docs/`
- `PHASES.md` → `docs/`

### 3. Initial Commit
```bash
git add .
git commit -m "chore: Phase 0 - project foundation scaffolding"
git branch -M main
git remote add origin https://github.com/yourusername/sonmancer-studio.git
git push -u origin main
```

### 4. Install Dependencies
```bash
npm install -g pnpm
pnpm install
```

---

## Week 1 Deliverables Checklist

### Day 1-2: Repository & Architecture

- [ ] **Repository Setup**
  - [ ] Git initialized with main/develop branches
  - [ ] Remote added and first commit pushed
  - [ ] `.gitignore` configured properly

- [ ] **Directory Structure**
  - [ ] `packages/desktop/` created
  - [ ] `packages/backend/` created
  - [ ] `packages/shared/` created
  - [ ] `docs/` created with all .md files
  - [ ] `.github/workflows/` created
  - [ ] `docker/` created
  - [ ] `scripts/` created

- [ ] **Monorepo Configuration**
  - [ ] `pnpm-workspace.yaml` created
  - [ ] Root `package.json` with shared devDeps
  - [ ] `pnpm install` runs without errors

**Verification:**
```bash
pnpm --version  # Should show pnpm 8+
pnpm install && pnpm lint  # Should pass
```

---

### Day 3-4: Development Environment

- [ ] **Linting & Formatting**
  - [ ] `.eslintrc.json` configured (ESLint + Prettier)
  - [ ] `.prettierrc.json` configured
  - [ ] `pnpm lint` command works
  - [ ] `pnpm format` command works

- [ ] **Pre-Commit Hooks**
  - [ ] Husky installed (`pnpm install husky -D`)
  - [ ] Pre-commit hook created: `npx husky add .husky/pre-commit "pnpm lint-staged"`
  - [ ] `.lintstagedrc.json` configured
  - [ ] Test: Make a change, commit → hooks should run

- [ ] **Backend Foundation**
  - [ ] `packages/backend/pyproject.toml` created
  - [ ] Python venv setup locally for testing
  - [ ] `aimusic/models/` created with SQLAlchemy models
  - [ ] `aimusic/main.py` created with FastAPI app
  - [ ] `aimusic/api/` created with router stubs

- [ ] **Frontend Foundation**
  - [ ] `packages/desktop/package.json` created
  - [ ] `packages/desktop/vite.config.ts` created
  - [ ] `packages/desktop/tsconfig.json` created
  - [ ] `packages/desktop/src/` created with React stubs
  - [ ] `packages/desktop/src-tauri/tauri.conf.json` created

**Verification:**
```bash
# Test frontend build
cd packages/desktop && pnpm build

# Test backend
cd packages/backend && pip install -e . && python -m pytest tests/ --co

# Should both succeed (or show proper structure)
```

---

### Day 5: CI/CD & Documentation

- [ ] **GitHub Actions**
  - [ ] `.github/workflows/test.yml` created
  - [ ] CI passes on main branch
  - [ ] Branch protection rule added (require status checks)

- [ ] **Docker**
  - [ ] `docker-compose.yml` created and tested
  - [ ] `docker/backend.Dockerfile` created
  - [ ] `docker-compose up -d` brings up services
  - [ ] Health check endpoint responds

- [ ] **Documentation**
  - [ ] `README.md` complete and links to docs
  - [ ] `SETUP.md` tested (first-time setup works)
  - [ ] `ARCHITECTURE.md` complete with diagrams
  - [ ] `API.md` complete with endpoint stubs
  - [ ] `CODING_STANDARDS.md` complete
  - [ ] `PHASES.md` complete with timeline

- [ ] **Environment Configuration**
  - [ ] `.env.example` created and documented
  - [ ] All services can read from environment variables
  - [ ] Development .env can start full stack

**Verification:**
```bash
# Full stack startup
docker-compose up -d

# Health check
curl http://localhost:8000/api/v1/health

# Should respond with health status JSON
```

---

## Week 2 Deliverables Checklist

### Day 1-2: GitHub Actions CI/CD

- [ ] **Test Workflow**
  - [ ] `.github/workflows/test.yml` created
  - [ ] Frontend linting step passes
  - [ ] Backend linting step passes
  - [ ] Backend unit tests run (empty initially)
  - [ ] Triggered on: push to main/develop, PR to main

- [ ] **Build Workflow**
  - [ ] `.github/workflows/build.yml` created
  - [ ] Desktop build for Linux (Tauri)
  - [ ] Backend Docker image build
  - [ ] Artifacts uploaded on success

- [ ] **Branch Protection**
  - [ ] Main branch requires CI to pass
  - [ ] Main branch requires PR review (optional for solo dev)
  - [ ] Main branch no force pushes

**Verification:**
```bash
# Make a PR with a small change
git checkout -b test/ci
echo "# Test" >> README.md
git add README.md
git commit -m "docs: test CI"
git push origin test/ci

# Should trigger CI pipeline
# Check Actions tab in GitHub
```

---

### Day 3-4: Local Development Environment

- [ ] **Docker Compose**
  - [ ] `docker-compose.yml` defines backend, database, Ollama
  - [ ] `docker-compose up -d` works without errors
  - [ ] All services healthy: `docker-compose ps`
  - [ ] Volume mounts work (hot reload)
  - [ ] Network connectivity between services works

- [ ] **Backend Local Setup**
  - [ ] `packages/backend/pyproject.toml` complete
  - [ ] Python 3.11 venv created
  - [ ] Dependencies installed: `pip install -e ".[dev]"`
  - [ ] FastAPI runs: `uvicorn aimusic.main:app --reload`
  - [ ] Health endpoint responds: `curl http://localhost:8000/api/v1/health`

- [ ] **Frontend Local Setup**
  - [ ] Node.js 18+ installed
  - [ ] `packages/desktop/` dependencies: `pnpm install`
  - [ ] Vite dev server runs: `pnpm dev:desktop`
  - [ ] React app loads in browser
  - [ ] TypeScript compiles without errors

- [ ] **Setup Scripts**
  - [ ] `scripts/dev-setup.sh` (Linux/Mac) created and tested
  - [ ] `scripts/dev-setup.ps1` (Windows) created and tested
  - [ ] Both scripts can set up entire dev environment

**Verification:**
```bash
# Full dev environment startup
bash scripts/dev-setup.sh  # Or .ps1 on Windows

# Terminal 1: Backend
cd packages/backend && uvicorn aimusic.main:app --reload

# Terminal 2: Desktop
cd packages/desktop && pnpm dev

# Should have working backend + frontend
```

---

### Day 5: Final Documentation & Polish

- [ ] **All Documentation Complete**
  - [ ] README.md links to all docs
  - [ ] SETUP.md tested and verified
  - [ ] ARCHITECTURE.md complete with diagrams
  - [ ] API.md complete with all endpoints
  - [ ] CODING_STANDARDS.md complete with examples
  - [ ] PHASES.md complete with timeline
  - [ ] CONTRIBUTING.md created with PR process

- [ ] **Repository Quality**
  - [ ] No console.log or print statements
  - [ ] No TODO comments (create GitHub issues instead)
  - [ ] Proper .gitignore (no secrets, build files, node_modules)
  - [ ] Code follows ESLint rules
  - [ ] Code formatted with Prettier/Black

- [ ] **Final Testing**
  - [ ] `pnpm lint` passes
  - [ ] `pnpm format` leaves no changes
  - [ ] `pnpm type-check` passes
  - [ ] `pnpm build` succeeds
  - [ ] `docker-compose up -d` succeeds
  - [ ] First-time dev setup works from README

**Verification:**
```bash
# Quality gate
pnpm lint && pnpm format:check && pnpm type-check && pnpm build

# Should all pass with no changes needed
```

---

## Phase 0 Success Criteria

### Absolute Requirements (Must Have)
- [ ] Repository initialized and hosted
- [ ] Monorepo working (pnpm install succeeds)
- [ ] CI/CD pipeline passing
- [ ] Docker Compose brings up full stack
- [ ] Backend API responds to health check
- [ ] Frontend loads in browser
- [ ] Documentation complete and accurate
- [ ] Code follows standards (linting, formatting)

### Nice to Have (Should Have)
- [ ] Pre-commit hooks prevent bad commits
- [ ] Setup scripts automate dev environment
- [ ] Database migrations automated
- [ ] Ollama integration working
- [ ] Example API endpoints returning stub data

### Not Required for Phase 0
- [ ] Feature implementation
- [ ] UI polish
- [ ] Performance optimization
- [ ] Production readiness

---

## File Checklist

### Root Level
- [ ] `pnpm-workspace.yaml` — Monorepo config
- [ ] `package.json` — Root scripts and shared deps
- [ ] `.eslintrc.json` — ESLint config
- [ ] `.prettierrc.json` — Prettier config
- [ ] `.editorconfig` — Editor formatting
- [ ] `.gitignore` — Git exclusions
- [ ] `.env.example` — Environment template
- [ ] `docker-compose.yml` — Local dev services
- [ ] `README.md` — Project overview
- [ ] `CONTRIBUTING.md` — Contribution guide

### Documentation (`docs/`)
- [ ] `SETUP.md` — Development setup
- [ ] `ARCHITECTURE.md` — System design
- [ ] `API.md` — API reference
- [ ] `CODING_STANDARDS.md` — Code style
- [ ] `PHASES.md` — Roadmap and timeline
- [ ] `DATABASE.md` — Schema reference (optional)

### Docker (`docker/`)
- [ ] `backend.Dockerfile` — Backend container

### CI/CD (`.github/workflows/`)
- [ ] `test.yml` — Linting and testing
- [ ] `build.yml` — Build and publish

### Backend (`packages/backend/`)
- [ ] `pyproject.toml` — Python config
- [ ] `aimusic/main.py` — FastAPI app
- [ ] `aimusic/models/entities.py` — Database models
- [ ] `aimusic/api/projects.py` — API stubs
- [ ] `aimusic/config.py` — Configuration
- [ ] `aimusic/db.py` — Database setup

### Frontend (`packages/desktop/`)
- [ ] `package.json` — Frontend deps
- [ ] `vite.config.ts` — Vite config
- [ ] `tsconfig.json` — TypeScript config
- [ ] `src/App.tsx` — Root component
- [ ] `src/main.tsx` — Entry point
- [ ] `src-tauri/tauri.conf.json` — Tauri config

---

## Immediate Next Steps (After Phase 0)

### Phase 1 Kickoff
1. **Week 3:** Desktop shell
   - [ ] Implement main layout (header, sidebar)
   - [ ] Add routing (Dashboard, Projects, Settings)
   - [ ] Material-UI theme setup

2. **Week 4:** Project management
   - [ ] Project list page
   - [ ] Project creation form
   - [ ] API integration

3. **Week 5:** Database & API
   - [ ] Implement project endpoints
   - [ ] Database migrations
   - [ ] Error handling

4. **Week 6:** Frontend integration
   - [ ] API client setup
   - [ ] State management
   - [ ] Loading/error states

---

## Questions to Answer Before Starting

1. **GitHub Setup:** Have you created a GitHub repository?
2. **Team:** Are you working solo or with a team?
3. **Timeline:** Can you commit 10+ hours/week?
4. **Platform Priority:** Windows first, or cross-platform?
5. **AI Models:** Do you have Ollama running locally?

---

## Command Reference

```bash
# Monorepo commands
pnpm install                    # Install all dependencies
pnpm lint                       # Lint all packages
pnpm format                     # Format all packages
pnpm build                      # Build all packages
pnpm test                       # Test all packages

# Frontend only
pnpm --filter @sonmancer/desktop dev     # Dev server
pnpm --filter @sonmancer/desktop build   # Build

# Backend only
pnpm --filter @sonmancer/backend dev     # Dev server (uvicorn)
pnpm --filter @sonmancer/backend test    # Tests

# Docker
docker-compose up -d            # Start services
docker-compose down             # Stop services
docker-compose logs -f          # View logs
docker-compose build --no-cache # Rebuild

# Git
git checkout -b feature/name    # Create feature branch
git push origin feature/name    # Push branch
# Create PR on GitHub
```

---

## Success Looks Like...

**End of Week 1:**
✅ Repository initialized, all files created, linting works, Docker runs

**End of Week 2:**
✅ CI/CD passing, full dev environment documented, first developer can set up in 30 minutes

**Phase 0 Complete:**
✅ Production-ready foundation, team ready to build Phase 1

---

**🎵 Let's build something amazing. Start with Phase 0.**

