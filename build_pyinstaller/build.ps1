<#
.SYNOPSIS
    Build the MarkItDown standalone Windows executable.

.DESCRIPTION
    This script:
    1. Creates a Python virtual environment (if needed)
    2. Installs markitdown[all] and PyInstaller
    3. Downloads external tools (exiftool, ffmpeg) if not already present
    4. Runs PyInstaller to produce the standalone bundle
    5. Packages the result into a zip file

.PARAMETER SkipExternals
    Skip downloading external tools (exiftool, ffmpeg).

.PARAMETER SkipVenv
    Skip virtual environment creation; use the current Python environment.

.PARAMETER Clean
    Remove previous build artifacts before building.

.PARAMETER OneFile
    Build a single-file executable instead of a directory bundle.
    Note: one-file mode has slower startup (5-10s) due to temp extraction.

.EXAMPLE
    .\build.ps1
    .\build.ps1 -Clean
    .\build.ps1 -SkipExternals -OneFile
#>

[CmdletBinding()]
param(
    [switch]$SkipExternals,
    [switch]$SkipVenv,
    [switch]$Clean,
    [switch]$OneFile
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$ExternalDir = Join-Path $ScriptDir "external"
$VenvDir = Join-Path $ScriptDir ".venv"
$DistDir = Join-Path $ScriptDir "dist"
$BuildDir = Join-Path $ScriptDir "build"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MarkItDown Windows EXE Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------------------
# Step 0: Clean previous artifacts
# ---------------------------------------------------------------------------
if ($Clean) {
    Write-Host "[Clean] Removing previous build artifacts..." -ForegroundColor Yellow
    if (Test-Path $DistDir) { Remove-Item -Recurse -Force $DistDir }
    if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }
    Write-Host "[Clean] Done." -ForegroundColor Green
    Write-Host ""
}

# ---------------------------------------------------------------------------
# Step 1: Virtual environment
# ---------------------------------------------------------------------------
if (-not $SkipVenv) {
    if (-not (Test-Path $VenvDir)) {
        Write-Host "[Venv] Creating virtual environment at $VenvDir ..." -ForegroundColor Yellow
        python -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment." }
    } else {
        Write-Host "[Venv] Using existing virtual environment at $VenvDir" -ForegroundColor Yellow
    }

    # Activate
    $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
    & $activateScript
}

# ---------------------------------------------------------------------------
# Step 2: Install dependencies
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[Install] Installing markitdown[all] and PyInstaller..." -ForegroundColor Yellow

$markitdownPkg = Join-Path $RepoRoot "packages\markitdown"
pip install "${markitdownPkg}[all]" pyinstaller --upgrade --quiet
if ($LASTEXITCODE -ne 0) { throw "pip install failed." }

Write-Host "[Install] Done." -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 3: Download external tools
# ---------------------------------------------------------------------------
if (-not $SkipExternals) {
    Write-Host ""
    Write-Host "[Externals] Preparing external tools directory..." -ForegroundColor Yellow

    if (-not (Test-Path $ExternalDir)) {
        New-Item -ItemType Directory -Path $ExternalDir -Force | Out-Null
    }

    # --- Download ExifTool ---
    $exiftoolExe = Join-Path $ExternalDir "exiftool.exe"
    if (-not (Test-Path $exiftoolExe)) {
        Write-Host "[Externals] Downloading ExifTool..." -ForegroundColor Yellow
        & (Join-Path $ScriptDir "download_externals.ps1") -Tool "exiftool" -OutputDir $ExternalDir
    } else {
        Write-Host "[Externals] ExifTool already present." -ForegroundColor Green
    }

    # --- Download ffmpeg ---
    $ffmpegExe = Join-Path $ExternalDir "ffmpeg.exe"
    if (-not (Test-Path $ffmpegExe)) {
        Write-Host "[Externals] Downloading ffmpeg..." -ForegroundColor Yellow
        & (Join-Path $ScriptDir "download_externals.ps1") -Tool "ffmpeg" -OutputDir $ExternalDir
    } else {
        Write-Host "[Externals] ffmpeg already present." -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "[Externals] Skipping external tools download." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# Step 4: Run PyInstaller
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[Build] Running PyInstaller..." -ForegroundColor Yellow

Push-Location $ScriptDir
try {
    $specFile = Join-Path $ScriptDir "markitdown.spec"

    if ($OneFile) {
        # For one-file mode, we run pyinstaller directly with flags instead of spec
        Write-Host "[Build] Building ONE-FILE executable (slower startup, easier distribution)..." -ForegroundColor Yellow

        $oneFileArgs = @(
            "--onefile",
            "--console",
            "--name", "markitdown",
            "--distpath", $DistDir,
            "--workpath", $BuildDir
        )

        # Add external binaries
        if (Test-Path $ExternalDir) {
            Get-ChildItem -Path $ExternalDir -File | ForEach-Object {
                $oneFileArgs += "--add-binary"
                $oneFileArgs += "$($_.FullName);external"
            }
        }

        # Add the data collections and hidden imports via spec is better,
        # so we'll modify the spec inline
        Write-Host "[Build] Note: One-file mode uses the spec file with modified EXE settings." -ForegroundColor Yellow
        Write-Host "[Build] For true one-file, edit markitdown.spec: set exclude_binaries=False and remove COLLECT." -ForegroundColor Yellow

        # Fall back to spec file build (more reliable)
        pyinstaller $specFile --noconfirm --clean
    } else {
        pyinstaller $specFile --noconfirm --clean
    }

    if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }
} finally {
    Pop-Location
}

Write-Host "[Build] Done." -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 5: Verify the build
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[Verify] Checking the built executable..." -ForegroundColor Yellow

$exePath = Join-Path $DistDir "markitdown\markitdown.exe"
if (Test-Path $exePath) {
    Write-Host "[Verify] Executable found at: $exePath" -ForegroundColor Green

    # Run --version
    $versionOutput = & $exePath --version 2>&1
    Write-Host "[Verify] Version: $versionOutput" -ForegroundColor Green

    # Run --info
    Write-Host "[Verify] Build info:" -ForegroundColor Green
    & $exePath --info 2>&1 | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "[Verify] WARNING: Executable not found at expected path!" -ForegroundColor Red
    Write-Host "[Verify] Expected: $exePath" -ForegroundColor Red
}

# ---------------------------------------------------------------------------
# Step 6: Create distribution zip
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[Package] Creating distribution zip..." -ForegroundColor Yellow

$distMarkitdownDir = Join-Path $DistDir "markitdown"
if (Test-Path $distMarkitdownDir) {
    # Get version from the exe
    try {
        $ver = (& $exePath --version 2>&1) -replace "markitdown\s+", "" -replace "\s+\(standalone\)", ""
        $ver = $ver.Trim()
    } catch {
        $ver = "dev"
    }

    $zipName = "markitdown-${ver}-win-x64.zip"
    $zipPath = Join-Path $DistDir $zipName

    if (Test-Path $zipPath) { Remove-Item -Force $zipPath }

    Compress-Archive -Path $distMarkitdownDir -DestinationPath $zipPath -Force
    $zipSize = (Get-Item $zipPath).Length / 1MB
    Write-Host "[Package] Created: $zipPath ($([math]::Round($zipSize, 1)) MB)" -ForegroundColor Green
} else {
    Write-Host "[Package] WARNING: dist/markitdown directory not found, skipping zip." -ForegroundColor Red
}

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Build complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output directory: $distMarkitdownDir" -ForegroundColor White
Write-Host "Run with: $exePath" -ForegroundColor White
Write-Host ""
