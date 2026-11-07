# Development Helper Script
# Provides quick commands for common development tasks

param(
    [Parameter(Position=0)]
    [ValidateSet('dev', 'build', 'clean', 'install', 'python', 'test', 'help')]
    [string]$Command = 'help'
)

function Show-Help {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host " Development Helper Script" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\dev.ps1 <command>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Green
    Write-Host "  dev       - Start development mode (React + Python + Electron)" -ForegroundColor White
    Write-Host "  build     - Build for production (full build)" -ForegroundColor White
    Write-Host "  clean     - Clean all build artifacts" -ForegroundColor White
    Write-Host "  install   - Install all dependencies (Node + Python)" -ForegroundColor White
    Write-Host "  python    - Build Python backend only" -ForegroundColor White
    Write-Host "  test      - Test the Python backend" -ForegroundColor White
    Write-Host "  help      - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\dev.ps1 dev      # Start development" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 build    # Build installer" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 clean    # Clean builds" -ForegroundColor Gray
    Write-Host ""
}

function Start-Dev {
    Write-Host "🚀 Starting development mode..." -ForegroundColor Cyan
    Write-Host ""
    npm run electron:dev
}

function Start-Build {
    Write-Host "📦 Starting production build..." -ForegroundColor Cyan
    Write-Host ""
    .\build.ps1
}

function Clean-Build {
    Write-Host "🧹 Cleaning build artifacts..." -ForegroundColor Cyan
    Write-Host ""
    
    $folders = @("dist", "build", "backend\dist", "backend\build", "release")
    
    foreach ($folder in $folders) {
        if (Test-Path $folder) {
            Write-Host "  Removing $folder..." -ForegroundColor Yellow
            Remove-Item -Recurse -Force $folder
            Write-Host "  ✓ Removed $folder" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "✓ Clean complete!" -ForegroundColor Green
}

function Install-Dependencies {
    Write-Host "📥 Installing dependencies..." -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Node.js install failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Python install failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ PyInstaller install failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ PyInstaller installed" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "✓ All dependencies installed!" -ForegroundColor Green
}

function Build-Python {
    Write-Host "🐍 Building Python backend..." -ForegroundColor Cyan
    Write-Host ""
    
    if (-not (Test-Path "backend")) {
        New-Item -ItemType Directory -Path "backend" | Out-Null
    }
    if (-not (Test-Path "backend\dist")) {
        New-Item -ItemType Directory -Path "backend\dist" | Out-Null
    }
    
    if (Test-Path "main.spec") {
        pyinstaller main.spec --distpath backend\dist --workpath backend\build --clean
    } else {
        pyinstaller --onefile --windowed --add-data ".env;." --name main --distpath backend\dist --workpath backend\build --clean main.py
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Python build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "✓ Python backend built successfully!" -ForegroundColor Green
    Write-Host "  Output: backend\dist\main.exe" -ForegroundColor Gray
}

function Test-Backend {
    Write-Host "🧪 Testing Python backend..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Starting Flask server (press Ctrl+C to stop)..." -ForegroundColor Yellow
    Write-Host ""
    python main.py
}

# Main execution
switch ($Command) {
    'dev' { Start-Dev }
    'build' { Start-Build }
    'clean' { Clean-Build }
    'install' { Install-Dependencies }
    'python' { Build-Python }
    'test' { Test-Backend }
    'help' { Show-Help }
    default { Show-Help }
}
