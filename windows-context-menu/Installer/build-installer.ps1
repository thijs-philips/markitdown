<#
.SYNOPSIS
    Publishes Markdown Converter and builds the Inno Setup installer.

.DESCRIPTION
    1. Publishes the app for win-x64 with ReadyToRun (framework-dependent by
       default). ReadyToRun crossgen REQUIRES the 64-bit .NET SDK, so this
       script uses the x64 dotnet host at "C:\Program Files\dotnet\dotnet.exe"
       when present (the x86 SDK fails with NETSDK1096 / clrjit_win_x64_x86).
    2. Runs ISCC.exe over Installer\MarkdownConverter.iss to produce
       Installer\dist\MarkdownConverter-Setup-<version>.exe.

.PARAMETER Configuration
    Build configuration (default: Release).

.PARAMETER SelfContained
    Bundle the .NET runtime (no prerequisite on the target machine, ~70 MB larger).
    Omit for a smaller framework-dependent build that needs the .NET 10 Desktop Runtime.

.EXAMPLE
    .\build-installer.ps1
    .\build-installer.ps1 -SelfContained
#>
[CmdletBinding()]
param(
    [string]$Configuration = "Release",
    [switch]$SelfContained
)

$ErrorActionPreference = "Stop"

$installerDir = $PSScriptRoot
$repoRoot     = Split-Path -Parent $installerDir
$project      = Join-Path $repoRoot "MarkdownConverter.csproj"
$publishDir   = Join-Path $installerDir "publish"
$issFile      = Join-Path $installerDir "MarkdownConverter.iss"

# --- Resolve the 64-bit dotnet host (needed for ReadyToRun crossgen) ----------
$dotnet = Join-Path $env:ProgramFiles "dotnet\dotnet.exe"
if (-not (Test-Path $dotnet)) {
    Write-Warning "64-bit dotnet not found at '$dotnet'; falling back to 'dotnet' on PATH. ReadyToRun may fail if that is the x86 SDK."
    $dotnet = "dotnet"
}

# --- Resolve ISCC.exe ---------------------------------------------------------
$isccCandidates = @(
    (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
    (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"),
    (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe")
)
$iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) {
    throw "ISCC.exe (Inno Setup 6 compiler) not found. Install it: winget install --id JRSoftware.InnoSetup -e"
}

# --- 1. Publish ---------------------------------------------------------------
if (Test-Path $publishDir) { Remove-Item $publishDir -Recurse -Force }

$selfContainedArg = if ($SelfContained) { "true" } else { "false" }

Write-Host "Publishing ($Configuration, win-x64, self-contained=$selfContainedArg)..." -ForegroundColor Cyan
# ReadyToRun is disabled: crossgen2 crashes on the installed .NET SDK
# (NETSDK1096 / jitStartup). The app is fully functional without R2R (it JITs at
# runtime, only the first launch is marginally slower).
& $dotnet publish $project `
    -c $Configuration `
    -r win-x64 `
    --self-contained $selfContainedArg `
    -p:PublishReadyToRun=false `
    -o $publishDir `
    --nologo
if ($LASTEXITCODE -ne 0) { throw "dotnet publish failed (exit $LASTEXITCODE)." }

# --- 2. Compile the installer -------------------------------------------------
Write-Host "Compiling installer with $iscc ..." -ForegroundColor Cyan
& $iscc $issFile
if ($LASTEXITCODE -ne 0) { throw "ISCC failed (exit $LASTEXITCODE)." }

$setup = Get-ChildItem (Join-Path $installerDir "dist") -Filter "MarkdownConverter-Setup-*.exe" |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($setup) {
    Write-Host ("Installer built: {0} ({1:N1} MB)" -f $setup.FullName, ($setup.Length / 1MB)) -ForegroundColor Green
} else {
    throw "Installer compiled but no output .exe was found."
}
