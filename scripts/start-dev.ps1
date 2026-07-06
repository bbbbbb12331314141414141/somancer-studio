# Sonmancer Studio — Dev Startup (Windows PowerShell)

Write-Host "`n🎵 Sonmancer Studio — Development Startup (Windows)" -ForegroundColor Cyan
Write-Host "======================================================"

$Root    = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "packages\backend"
$Desktop = Join-Path $Root "packages\desktop"

# ── Check prerequisites ────────────────────────────────────────────────────────
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python 3.11+ required" -ForegroundColor Red; exit 1
}
if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ pnpm required (npm install -g pnpm)" -ForegroundColor Red; exit 1
}

# ── Backend ───────────────────────────────────────────────────────────────────
Write-Host "`n▶ Starting FastAPI backend…" -ForegroundColor Green
Set-Location $Backend

if (-not (Test-Path "venv")) {
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -e ".[dev]" -q
} else {
    .\venv\Scripts\Activate.ps1
}

$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    .\venv\Scripts\Activate.ps1
    uvicorn aimusic.main:app --reload --host 0.0.0.0 --port 8000
} -ArgumentList $Backend

Write-Host "  Backend Job ID: $($backendJob.Id)"

# ── Frontend ──────────────────────────────────────────────────────────────────
Write-Host "▶ Starting Vite dev server…" -ForegroundColor Green
Set-Location $Root

$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    pnpm --filter @sonmancer/desktop dev
} -ArgumentList $Root

Write-Host "  Frontend Job ID: $($frontendJob.Id)"

Write-Host "`n✅ All services started!" -ForegroundColor Green
Write-Host "  Backend:   http://localhost:8000"
Write-Host "  Swagger:   http://localhost:8000/api/v1/docs"
Write-Host "  Frontend:  http://localhost:5173"
Write-Host "`nPress Ctrl+C to stop all services."

try { Wait-Job $backendJob, $frontendJob }
finally { Stop-Job $backendJob, $frontendJob; Remove-Job $backendJob, $frontendJob }
