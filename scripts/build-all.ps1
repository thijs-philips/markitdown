<#
.SYNOPSIS
    End-to-end Windows build: compile MarkItDown -> integrate into the context-menu
    app -> produce the installer.

.DESCRIPTION
    Runs the three pipeline stages in order:

      Stage 1  Compile the MarkItDown engine to a standalone Windows folder.
                 nuitka      -> build_nuitka\build.ps1
                 pyinstaller -> build_pyinstaller\build.ps1
      Stage 2  Stage that engine into windows-context-menu\markitdown
                 -> scripts\integrate-engine.ps1
      Stage 3  Publish the C# app + build the Inno Setup installer
                 -> windows-context-menu\Installer\build-installer.ps1
      Stage 4  Publish the installer as a versioned package in the repo
                 -> scripts\package-release.ps1

    Each stage also has its own clearly-named script and can be run on its own.

.PARAMETER Engine
    Engine build chain: nuitka (default) or pyinstaller.

.PARAMETER SkipEngine
    Skip stage 1 and reuse the existing engine output (handy when only the C#
    app or installer changed).

.PARAMETER SelfContained
    Bundle the .NET runtime into the installer (no .NET runtime prerequisite on
    the target machine, but a larger installer). Passed through to stage 3.

.PARAMETER Clean
    Clean engine build artifacts before stage 1.

.PARAMETER SkipPackage
    Skip stage 4 (do not copy the installer into releases\<version>\).

.PARAMETER CommitRelease
    In stage 4, also git add + commit the new releases\<version>\ folder.

.EXAMPLE
    .\build-all.ps1
    .\build-all.ps1 -Engine pyinstaller
    .\build-all.ps1 -SkipEngine -SelfContained
    .\build-all.ps1 -Engine nuitka -Clean
    .\build-all.ps1 -CommitRelease
#>
[CmdletBinding()]
param(
    [ValidateSet("nuitka", "pyinstaller")]
    [string]$Engine = "nuitka",
    [switch]$SkipEngine,
    [switch]$SelfContained,
    [switch]$Clean,
    [switch]$SkipPackage,
    [switch]$CommitRelease
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir

function Write-Stage($n, $text) {
    Write-Host ""
    Write-Host "############################################" -ForegroundColor Magenta
    Write-Host "#  STAGE $n  $text" -ForegroundColor Magenta
    Write-Host "############################################" -ForegroundColor Magenta
    Write-Host ""
}

$sw = [System.Diagnostics.Stopwatch]::StartNew()

# ---------------------------------------------------------------------------
# Stage 1: compile the MarkItDown engine
# ---------------------------------------------------------------------------
if (-not $SkipEngine) {
    Write-Stage 1 "Compile MarkItDown engine ($Engine)"
    switch ($Engine) {
        "nuitka"      { $engineScript = Join-Path $RepoRoot "build_nuitka\build.ps1" }
        "pyinstaller" { $engineScript = Join-Path $RepoRoot "build_pyinstaller\build.ps1" }
    }
    $engineArgs = @{}
    if ($Clean) { $engineArgs["Clean"] = $true }
    & $engineScript @engineArgs
    if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) { throw "Stage 1 (engine build) failed." }
} else {
    Write-Stage 1 "SKIPPED (reusing existing $Engine engine output)"
}

# ---------------------------------------------------------------------------
# Stage 2: integrate the engine into the context-menu app
# ---------------------------------------------------------------------------
Write-Stage 2 "Integrate engine into context-menu app"
& (Join-Path $ScriptDir "integrate-engine.ps1") -Engine $Engine
if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) { throw "Stage 2 (integrate) failed." }

# ---------------------------------------------------------------------------
# Stage 3: publish app + build installer
# ---------------------------------------------------------------------------
Write-Stage 3 "Build installer"
$installerScript = Join-Path $RepoRoot "windows-context-menu\Installer\build-installer.ps1"
$installerArgs = @{}
if ($SelfContained) { $installerArgs["SelfContained"] = $true }
& $installerScript @installerArgs
if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) { throw "Stage 3 (installer) failed." }

# ---------------------------------------------------------------------------
# Stage 4: publish the installer as a versioned package in the repo
# ---------------------------------------------------------------------------
if (-not $SkipPackage) {
    Write-Stage 4 "Package versioned release"
    $packageScript = Join-Path $ScriptDir "package-release.ps1"
    $packageArgs = @{ Engine = $Engine }
    if ($CommitRelease) { $packageArgs["Commit"] = $true }
    & $packageScript @packageArgs
    if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) { throw "Stage 4 (package) failed." }
} else {
    Write-Stage 4 "SKIPPED (not packaging a versioned release)"
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
$sw.Stop()
$setup = Get-ChildItem (Join-Path $RepoRoot "windows-context-menu\Installer\dist") `
            -Filter "MarkdownConverter-Setup-*.exe" -ErrorAction SilentlyContinue |
         Sort-Object LastWriteTime -Descending | Select-Object -First 1

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Pipeline complete in $([math]::Round($sw.Elapsed.TotalMinutes,1)) min" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
if ($setup) {
    Write-Host ("  Installer: {0} ({1:N1} MB)" -f $setup.FullName, ($setup.Length / 1MB)) -ForegroundColor White
}
