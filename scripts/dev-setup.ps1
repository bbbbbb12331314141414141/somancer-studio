# Somancer Studio - Development Setup (Windows)

Write-Host "`n🎵 Somancer Studio — Development Setup (Windows)" -ForegroundColor Cyan
Write-Host "=============================================="
a
# Check for required tools
function Check-Command {
    param([string]$Command)
    if (Get-Command $Command -ErrorAction SilentlyContinue) {
        return $true
    } else {
        Write-Host "❌ $Command not found. Please install $Command first." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Checking prerequisites..." -ForegroundColor Yellow
Check-Command "node" | Out-Null
Check-Command "python" | Out-Null
Check-Command "git" | Out-Null

# Install pnpm if not present
if (!(Get-Command pnpm -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing pnpm..." -ForegroundColor Yellow
    npm install -g pnpm
}

# Create .env if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "📋 Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "   Edit .env to configure your environment"
}

# Install Python dependencies
Write-Host "📚 Installing Python dependencies..." -ForegroundColor Yellow
cd packages\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e ".[dev]"
deactivate
cd ..\..

# Install Node dependencies
Write-Host "📦 Installing Node dependencies..." -ForegroundColor Yellow
pnpm install

# Setup pre-commit hooks
Write-Host "🪝 Setting up pre-commit hooks..." -ForegroundColor Yellow
pnpm install husky -D 2>$null
npx husky install 2>$null
npx husky add .husky/pre-commit "pnpm lint-staged" 2>$null

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Start backend: cd packages\backend && .\venv\Scripts\Activate.ps1 && uvicorn aimusic.main:app --reload"
Write-Host "  2. Start frontend: pnpm dev:desktop"
Write-Host "  3. Or start full stack: docker-compose up -d"
Write-Host ""
Write-Host "For more info, see docs/SETUP.md"
