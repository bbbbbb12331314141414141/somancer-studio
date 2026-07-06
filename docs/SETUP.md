# Somancer Studio — Development Setup Guide

## Prerequisites

### Windows
- Windows 10/11 (build 19042+)
- WSL 2 (optional but recommended)
- Git for Windows
- Node.js 18+ (via nvm-windows or direct)
- Python 3.11+ (from python.org or Windows Store)
- Rust 1.70+ (via rustup)
- Visual Studio 2022 Community or Build Tools (for C++ dependencies)

### macOS
- macOS 11+ (Intel or Apple Silicon)
- Xcode Command Line Tools: `xcode-select --install`
- Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Node.js 18+: `brew install node`
- Python 3.11+: `brew install python@3.11`
- Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

### Linux (Ubuntu 22.04 LTS)
```bash
sudo apt-get update && sudo apt-get install -y \
    curl \
    git \
    build-essential \
    libssl-dev \
    pkg-config \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nodejs \
    npm
```

Then install Rust:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

---

## Quick Start (All Platforms)

### 1. Clone Repository
```bash
git clone https://github.com/bbbbbb12331314141414141/somancer-studio.git
cd somancer-studio
```

### 2. Install Node Package Manager
```bash
npm install -g pnpm@latest
```

### 3. Install Dependencies
```bash
pnpm install
```

### 4. Set Up Environment
```bash
# Copy example env
cp .env.example .env

# Edit .env with your settings (optional)
nano .env
```

### 5. Start Docker Services
```bash
# Start backend, database, and Ollama
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 6. Run Development Environment
```bash
# Terminal 1: Backend (FastAPI with hot reload)
pnpm dev:backend

# Terminal 2: Desktop (Tauri + React with hot reload)
pnpm dev:desktop
```

---

## Individual Service Development

### Backend Only
```bash
cd packages/backend

# Create Python venv
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run with uvicorn (hot reload)
uvicorn aimusic.main:app --reload --port 8000

# Or run tests
pytest tests/ -v --cov=aimusic
```

### Desktop Only
```bash
cd packages/desktop

# Start Vite dev server + Tauri window
pnpm dev

# Build for production
pnpm build
```

### Ollama (Optional Local Installation)
If you want to run Ollama outside Docker:
1. Download from https://ollama.ai
2. Install and run: `ollama serve`
3. In another terminal, pull a model: `ollama pull mistral`
4. Update `.env` to point to your local Ollama: `OLLAMA_HOST=http://localhost:11434`

---

## Docker Development Workflow

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f ollama
```

### Stop Services
```bash
docker-compose down
```

### Clean Everything (Warning: deletes data)
```bash
docker-compose down -v
```

### Rebuild Backend Container
```bash
docker-compose build --no-cache backend
docker-compose up -d backend
```

---

## Code Quality Checks

### Lint Everything
```bash
pnpm lint
```

### Format Everything
```bash
pnpm format
```

### Type Check
```bash
pnpm type-check
```

### Run Tests
```bash
pnpm test
```

---

## Environment Variables

Create `.env` in project root (copy from `.env.example`):

```env
# Backend
DATABASE_URL=sqlite:///./sonmancer.db
OLLAMA_HOST=http://localhost:11434
LOG_LEVEL=INFO
ENVIRONMENT=development

# Frontend
VITE_API_URL=http://localhost:8000

# GPU Support
CUDA_ENABLED=true
GPU_MEMORY_GB=8
```

---

## Troubleshooting

### Issue: "pnpm command not found"
**Solution:**
```bash
npm install -g pnpm
pnpm --version
```

### Issue: Backend fails to start with "module not found"
**Solution:**
```bash
# Rebuild Docker container
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Issue: Frontend can't connect to backend API
**Solution:** Check `.env` and `vite.config.ts`:
- `VITE_API_URL` should match backend port (default: 8000)
- Verify backend is running: `curl http://localhost:8000/api/v1/health`

### Issue: Python version mismatch
**Solution:**
```bash
python3.11 --version  # Should be 3.11+
python3.11 -m venv venv
source venv/bin/activate
```

### Issue: Tauri build fails on Windows
**Solution:** Install Visual Studio 2022 Community with C++ build tools, then restart IDE.

---

## VS Code Setup (Recommended)

### Extensions
- ESLint
- Prettier
- Python
- Pylance
- Tauri
- Thunder Client (API testing)

### Settings (.vscode/settings.json)
```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true
  },
  "[typescript]": {
    "editor.formatOnSave": true
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true
}
```

---

## Making Changes

### Branching
```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes, commit regularly
git add .
git commit -m "feat: add thing"

# Push and create PR
git push origin feature/my-feature
```

### Pre-Commit Hooks
Linting and formatting run automatically before commit. If they fail:
```bash
# Fix issues manually, or:
pnpm format  # Auto-format
pnpm lint    # Report lint errors
```

### Running Tests Before PR
```bash
pnpm test
pnpm build
```

---

## Building for Distribution

### Desktop (All Platforms)
```bash
cd packages/desktop
pnpm build
# Output: src-tauri/target/release/
```

### Backend (Docker)
```bash
docker build -f docker/backend.Dockerfile -t sonmancer-backend:latest .
docker run -p 8000:8000 sonmancer-backend:latest
```

---

## Next Steps

- Read `ARCHITECTURE.md` for system design
- Read `CODING_STANDARDS.md` for code guidelines
- Check `API.md` for backend endpoints
- Review `PHASES.md` for roadmap

Happy coding! 🎵

