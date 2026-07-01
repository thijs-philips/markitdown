<#
.SYNOPSIS
    Stage 2 of the Windows build pipeline: integrate the compiled MarkItDown
    engine into the MarkdownConverter context-menu app.

.DESCRIPTION
    Copies the standalone MarkItDown engine produced by stage 1 (PyInstaller or
    Nuitka) into windows-context-menu/markitdown/, which the C#
    project bundles at publish time and invokes at runtime.

    This step is engine-agnostic: both build chains emit a self-contained
    "markitdown/" folder containing markitdown.exe, so this script simply mirrors
    that folder into the app's bundled engine location.

.PARAMETER Engine
    Which engine build to stage:
      nuitka      -> build_nuitka/output/markitdown        (default)
      pyinstaller -> build_pyinstaller/dist/markitdown

.PARAMETER Build
    Also run `dotnet build` on the solution afterwards to verify the engine
    integrates and the app compiles. Off by default (stage 3 publishes anyway).

.EXAMPLE
    .\integrate-engine.ps1
    .\integrate-engine.ps1 -Engine pyinstaller
    .\integrate-engine.ps1 -Engine nuitka -Build
#>
[CmdletBinding()]
param(
    [ValidateSet("nuitka", "pyinstaller")]
    [string]$Engine = "nuitka",
    [switch]$Build
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir
$AppDir    = Join-Path $RepoRoot "windows-context-menu"
$DestDir   = Join-Path $AppDir "markitdown"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stage 2: Integrate engine ($Engine)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------------------
# Resolve the engine output folder
# ---------------------------------------------------------------------------
switch ($Engine) {
    "nuitka"      { $SrcDir = Join-Path $RepoRoot "build_nuitka\output\markitdown" }
    "pyinstaller" { $SrcDir = Join-Path $RepoRoot "build_pyinstaller\dist\markitdown" }
}

$srcExe = Join-Path $SrcDir "markitdown.exe"
if (-not (Test-Path $srcExe)) {
    throw "Engine output not found at '$srcExe'.`n" +
          "Run stage 1 first:`n" +
          "  nuitka      -> build_nuitka\build.ps1`n" +
          "  pyinstaller -> build_pyinstaller\build.ps1"
}

# ---------------------------------------------------------------------------
# Mirror the engine into markitdown/ (clean copy, keep README)
# ---------------------------------------------------------------------------
Write-Host "[Integrate] Source: $SrcDir" -ForegroundColor Yellow
Write-Host "[Integrate] Dest:   $DestDir" -ForegroundColor Yellow

$keepReadme = Join-Path $DestDir "README.md"
$readmeBackup = $null
if (Test-Path $keepReadme) {
    $readmeBackup = Get-Content -Raw -LiteralPath $keepReadme
}

# robocopy /MIR mirrors (and prunes stale files from previous engine builds).
# Exit codes < 8 are success for robocopy.
robocopy $SrcDir $DestDir /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed (exit $LASTEXITCODE)." }

# /MIR removes the README; restore it so the staging folder stays documented.
if ($null -ne $readmeBackup) {
    Set-Content -LiteralPath $keepReadme -Value $readmeBackup -NoNewline
}

$staged = Get-ChildItem $DestDir -Recurse -File | Measure-Object -Property Length -Sum
$mb = [math]::Round(($staged.Sum / 1MB), 1)
Write-Host "[Integrate] Staged $($staged.Count) files ($mb MB)." -ForegroundColor Green

# Quick smoke test of the staged engine
$destExe = Join-Path $DestDir "markitdown.exe"
$ver = & $destExe --version 2>&1
Write-Host "[Integrate] Engine: $ver" -ForegroundColor Green

# ---------------------------------------------------------------------------
# Optional: verify the app compiles with the engine in place
# ---------------------------------------------------------------------------
if ($Build) {
    Write-Host ""
    Write-Host "[Build] dotnet build (Release) to verify integration..." -ForegroundColor Yellow
    $sln = Join-Path $AppDir "MarkdownConverter.sln"
    $dotnet = Join-Path $env:ProgramFiles "dotnet\dotnet.exe"
    if (-not (Test-Path $dotnet)) { $dotnet = "dotnet" }
    & $dotnet build $sln -c Release --nologo
    if ($LASTEXITCODE -ne 0) { throw "dotnet build failed (exit $LASTEXITCODE)." }
    Write-Host "[Build] Done." -ForegroundColor Green
}

Write-Host ""
Write-Host "[Integrate] Stage 2 complete." -ForegroundColor Green
