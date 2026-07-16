# Complete setup from scratch for local development

param(
    [switch]$SkipDbClean = $false
)

$ROOT_DIR = "C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager"
$BACKEND_DIR = "$ROOT_DIR\backend"

Write-Host "🚀 AI Document Manager - Complete Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Clean old database
if (-not $SkipDbClean) {
    Write-Host ""
    Write-Host "📋 Step 1: Cleaning old database..." -ForegroundColor Yellow
    $dbFile = "$BACKEND_DIR\dms_backend.db"
    if (Test-Path $dbFile) {
        Remove-Item $dbFile -Force
        Write-Host "✅ Old database removed" -ForegroundColor Green
    }
}

# Step 2: Create database schema
Write-Host ""
Write-Host "📋 Step 2: Creating database schema..." -ForegroundColor Yellow
Push-Location $BACKEND_DIR
python setup_db.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create database schema" -ForegroundColor Red
    exit 1
}
Pop-Location

# Step 3: Seed default data
Write-Host ""
Write-Host "📋 Step 3: Seeding default roles and privileges..." -ForegroundColor Yellow
Push-Location $BACKEND_DIR
python -c "
from app.core.db import session_scope
from app.modules.iam.application.seed import seed_default_roles
try:
    with session_scope() as session:
        seed_default_roles(session)
        print('✅ Default roles and privileges seeded')
except Exception as e:
    print(f'⚠️  Seeding note: {e}')
"
Pop-Location

# Step 4: Start backend
Write-Host ""
Write-Host "📋 Step 4: Starting backend server..." -ForegroundColor Yellow
Write-Host "✅ Backend ready at http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Green
Push-Location $BACKEND_DIR
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
