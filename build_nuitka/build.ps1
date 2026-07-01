<#
.SYNOPSIS
    Build the MarkItDown standalone Windows executable using Nuitka + MSVC.

.DESCRIPTION
    This script:
    1. Creates a Python virtual environment (if needed)
    2. Installs markitdown (editable) and lean dependencies
    3. Runs Nuitka in standalone mode with MSVC to produce a native exe
    4. Copies the speech_recognition version.txt data file if needed
    5. Packages the result into a zip file

    The output is a self-contained folder named "markitdown/" containing
    the compiled markitdown.exe and all required DLLs/data files (~104 MB).

    Compared to PyInstaller: ~3x faster startup, ~55% smaller distribution.

.PARAMETER SkipVenv
    Skip virtual environment creation; use the current Python environment.

.PARAMETER Clean
    Remove previous build artifacts before building.

.PARAMETER Compiler
    C compiler backend: "msvc" (default, fastest) or "zig" (cross-platform, slower).

.EXAMPLE
    .\build.ps1
    .\build.ps1 -Clean
    .\build.ps1 -Compiler zig
#>

[CmdletBinding()]
param(
    [switch]$SkipVenv,
    [switch]$Clean,
    [ValidateSet("msvc", "zig")]
    [string]$Compiler = "msvc",
    # Parallel C-compilation jobs. Default leaves headroom so the PC stays
    # usable during the build (≈ 75% of logical CPUs, min 1). Pass 0 to let
    # Nuitka use all cores.
    [int]$Jobs = 0
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$VenvDir = Join-Path $ScriptDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$OutputDir = Join-Path $ScriptDir "output"
$DistDir = Join-Path $OutputDir "entry.dist"

# Resolve a sensible default job count: leave ~25% of cores free (min 1) so the
# machine remains responsive for other work during the long compile.
$cpuCount = [int]$env:NUMBER_OF_PROCESSORS
if ($cpuCount -lt 1) { $cpuCount = 4 }
if ($Jobs -le 0) {
    $Jobs = [Math]::Max(1, [int][Math]::Floor($cpuCount * 0.75))
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MarkItDown Nuitka Builder" -ForegroundColor Cyan
Write-Host "  Compiler: $Compiler" -ForegroundColor Cyan
Write-Host "  Jobs: $Jobs of $cpuCount CPUs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------------------
# Step 0: Clean previous artifacts
# ---------------------------------------------------------------------------
if ($Clean) {
    Write-Host "[Clean] Removing previous build artifacts..." -ForegroundColor Yellow
    if (Test-Path $OutputDir) { Remove-Item -Recurse -Force $OutputDir }
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
}

# The build ALWAYS compiles with the lean .venv interpreter, even with
# -SkipVenv. Using the bare `python`/`pip` on PATH would silently pull in the
# global environment (e.g. a system-wide torch install), bloating the binary
# and massively slowing the C compilation. Fail loudly if the venv is missing.
if (-not (Test-Path $VenvPython)) {
    throw "Lean build venv not found at $VenvPython. Run without -SkipVenv first to create it."
}
Write-Host "[Venv] Build interpreter: $VenvPython" -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 2: Install dependencies
# ---------------------------------------------------------------------------
# Installs are a SETUP step: only run when not -SkipVenv. With -SkipVenv we
# assume the lean venv is already populated (markitdown editable + lean reqs)
# and jump straight to compiling. This also avoids re-hitting any configured
# private/auth package index (e.g. corporate Artifactory) on every build.
if (-not $SkipVenv) {
    Write-Host ""
    Write-Host "[Install] Installing lean dependencies and markitdown (editable)..." -ForegroundColor Yellow

    $reqFile = Join-Path $ScriptDir "requirements.txt"
    & $VenvPython -m pip install -r $reqFile --quiet
    if ($LASTEXITCODE -ne 0) { throw "pip install requirements failed." }

    # The editable markitdown install below uses --no-build-isolation, so its
    # PEP 517 backend (hatchling) and hatchling's editable helper (editables)
    # must already be present in the venv. The configured (corporate) index does
    # not always mirror them, so install with a public-PyPI fallback.
    & $VenvPython -c "import hatchling.build, editables" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[Install] Installing editable-build backend (hatchling + editables)..." -ForegroundColor Yellow
        & $VenvPython -m pip install "hatchling>=1.25" editables --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[Install] Configured index lacks them; falling back to PyPI..." -ForegroundColor Yellow
            & $VenvPython -m pip install "hatchling>=1.25" editables --index-url https://pypi.org/simple --quiet
        }
        if ($LASTEXITCODE -ne 0) { throw "Failed to install hatchling/editables build backend." }
    }

    # --no-build-isolation: the build backend (hatchling) is resolved from the
    # current venv instead of being fetched fresh from the index, which avoids
    # interactive credential prompts against private/auth indexes.
    $markitdownPkg = Join-Path $RepoRoot "packages\markitdown"
    & $VenvPython -m pip install -e $markitdownPkg --no-deps --no-build-isolation --quiet
    if ($LASTEXITCODE -ne 0) { throw "pip install markitdown failed." }

    Write-Host "[Install] Done." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[Install] Skipped (-SkipVenv): using existing venv packages." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# Step 3: Run Nuitka
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[Build] Running Nuitka (standalone, $Compiler)..." -ForegroundColor Yellow

$entryPoint = Join-Path $ScriptDir "entry.py"

# Shared CLI core (build_common/markitdown_cli_core.py) must be importable so
# Nuitka follows and compiles it into the binary.
$BuildCommonDir = Join-Path $RepoRoot "build_common"
$env:PYTHONPATH = $BuildCommonDir

$nuitkaArgs = @(
    "-m", "nuitka",
    "--standalone",
    "--output-dir=$OutputDir",
    "--output-filename=markitdown.exe",
    "--assume-yes-for-downloads",
    "--no-deployment-flag=self-execution",
    "--include-package=markitdown",
    "--include-package=markitdown.converters",
    "--include-package=markitdown.converter_utils",
    "--include-module=markitdown_cli_core",
    "--jobs=$Jobs"
)

if ($Compiler -eq "msvc") {
    $nuitkaArgs += "--msvc=latest"
} else {
    $nuitkaArgs += "--zig"
}

$nuitkaArgs += $entryPoint

& $VenvPython @nuitkaArgs
if ($LASTEXITCODE -ne 0) { throw "Nuitka build failed." }

Write-Host "[Build] Done." -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 4: Post-build fixups
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[Fixup] Checking for missing data files..." -ForegroundColor Yellow

# speech_recognition needs version.txt at runtime
$srVersionSrc = Join-Path $VenvDir "Lib\site-packages\speech_recognition\version.txt"
$srVersionDst = Join-Path $DistDir "speech_recognition\version.txt"
if ((Test-Path $srVersionSrc) -and -not (Test-Path $srVersionDst)) {
    $srDir = Split-Path $srVersionDst
    if (-not (Test-Path $srDir)) { New-Item -ItemType Directory -Path $srDir -Force | Out-Null }
    Copy-Item $srVersionSrc $srVersionDst
    Write-Host "[Fixup] Copied speech_recognition/version.txt" -ForegroundColor Green
}

Write-Host "[Fixup] Done." -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 5: Rename dist folder
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[Rename] Renaming output folder to 'markitdown'..." -ForegroundColor Yellow

$finalDir = Join-Path $OutputDir "markitdown"
if (Test-Path $finalDir) { Remove-Item -Recurse -Force $finalDir }
Rename-Item -Path $DistDir -NewName "markitdown"

$exePath = Join-Path $finalDir "markitdown.exe"
Write-Host "[Rename] Executable: $exePath" -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 6: Verify the build
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[Verify] Checking the built executable..." -ForegroundColor Yellow

if (Test-Path $exePath) {
    $versionOutput = & $exePath --version 2>&1
    Write-Host "[Verify] Version: $versionOutput" -ForegroundColor Green
} else {
    Write-Host "[Verify] WARNING: Executable not found at expected path!" -ForegroundColor Red
    throw "Build verification failed."
}

# ---------------------------------------------------------------------------
# Step 7: Create distribution zip
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "[Package] Creating distribution zip..." -ForegroundColor Yellow

try {
    $ver = ($versionOutput -replace "markitdown\s+", "").Trim()
} catch {
    $ver = "dev"
}

$zipName = "markitdown-${ver}-nuitka-win-x64.zip"
$zipPath = Join-Path $OutputDir $zipName

if (Test-Path $zipPath) { Remove-Item -Force $zipPath }

Compress-Archive -Path $finalDir -DestinationPath $zipPath -Force
$zipSize = (Get-Item $zipPath).Length / 1MB
Write-Host "[Package] Created: $zipPath ($([math]::Round($zipSize, 1)) MB)" -ForegroundColor Green

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Build complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$exeSize = (Get-Item $exePath).Length / 1MB
$distSize = (Get-ChildItem $finalDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host ""
Write-Host "  Executable:  $([math]::Round($exeSize, 1)) MB" -ForegroundColor White
Write-Host "  Dist folder: $([math]::Round($distSize, 1)) MB" -ForegroundColor White
Write-Host "  Zip:         $([math]::Round($zipSize, 1)) MB" -ForegroundColor White
Write-Host "  Location:    $finalDir" -ForegroundColor White
Write-Host ""
