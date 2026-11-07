# ==================================
# BUILD SYSTEM FOR ELECTRON + PYTHON
# ==================================
# This script automates the build process for packaging the desktop application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sistema de Reportes - Build Script  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clean previous builds
Write-Host "[1/5] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "  ✓ Removed React dist/" -ForegroundColor Green
}
if (Test-Path "backend/dist") {
    Remove-Item -Recurse -Force "backend/dist"
    Write-Host "  ✓ Removed Python backend/dist/" -ForegroundColor Green
}
if (Test-Path "backend/build") {
    Remove-Item -Recurse -Force "backend/build"
    Write-Host "  ✓ Removed Python backend/build/" -ForegroundColor Green
}
if (Test-Path "release") {
    Remove-Item -Recurse -Force "release"
    Write-Host "  ✓ Removed Electron release/" -ForegroundColor Green
}
Write-Host ""

# Step 2: Build React frontend
Write-Host "[2/5] Building React frontend..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ React build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ React frontend built successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Create backend directory structure
Write-Host "[3/5] Creating backend directory..." -ForegroundColor Yellow
if (-not (Test-Path "backend")) {
    New-Item -ItemType Directory -Path "backend" | Out-Null
}
if (-not (Test-Path "backend/dist")) {
    New-Item -ItemType Directory -Path "backend/dist" | Out-Null
}
Write-Host "  ✓ Backend directory created" -ForegroundColor Green
Write-Host ""

# Step 4: Build Python backend with PyInstaller
Write-Host "[4/5] Building Python backend with PyInstaller..." -ForegroundColor Yellow
Write-Host "  This may take several minutes..." -ForegroundColor Gray

# Check if using spec file or direct command
if (Test-Path "main.spec") {
    # Build using spec file
    pyinstaller main.spec --distpath backend/dist --workpath backend/build --clean
} else {
    # Build using direct command
    pyinstaller --onefile `
        --windowed `
        --add-data ".env;." `
        --name main `
        --distpath backend/dist `
        --workpath backend/build `
        --clean `
        main.py
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ PyInstaller build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Python backend built successfully" -ForegroundColor Green
Write-Host ""

# Step 5: Package with electron-builder
Write-Host "[5/5] Packaging with Electron Builder..." -ForegroundColor Yellow
electron-builder --win
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Electron packaging failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Electron app packaged successfully" -ForegroundColor Green
Write-Host ""

# Success message
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✓ BUILD COMPLETED SUCCESSFULLY  " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your installer is located at:" -ForegroundColor Yellow
Write-Host "  release/Sistema de Reportes-Setup-*.exe" -ForegroundColor White
Write-Host ""
