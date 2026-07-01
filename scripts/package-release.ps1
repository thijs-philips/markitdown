<#
.SYNOPSIS
    Stage 4 of the Windows build pipeline: publish the freshly-built installer as
    a versioned package inside the repository.

.DESCRIPTION
    Takes the installer produced by stage 3
    (windows-context-menu\Installer\dist\MarkdownConverter-Setup-<version>.exe)
    and copies it into a tracked, versioned location in the repo:

        releases\<version>\MarkdownConverter-Setup-<version>.exe
        releases\<version>\SHA256SUMS.txt
        releases\<version>\RELEASE.md

    A SHA-256 checksum and a small manifest (version, date, engine, size) are
    written alongside the installer so each release is self-describing.

    The version is read from windows-context-menu\Installer\MarkdownConverter.iss
    (#define MyAppVersion) unless overridden with -Version.

    By default nothing is committed; pass -Commit to `git add` + `git commit`
    the new release folder.

.PARAMETER Version
    Override the release version. Defaults to MyAppVersion from the .iss file.

.PARAMETER Engine
    Recorded in RELEASE.md for provenance (nuitka or pyinstaller). Default: nuitka.

.PARAMETER InstallerPath
    Explicit path to the installer .exe. Defaults to the newest
    MarkdownConverter-Setup-*.exe under windows-context-menu\Installer\dist.

.PARAMETER Commit
    Stage and commit the new releases\<version>\ folder.

.EXAMPLE
    .\package-release.ps1
    .\package-release.ps1 -Version 1.2.0 -Commit
    .\package-release.ps1 -Engine pyinstaller
#>
[CmdletBinding()]
param(
    [string]$Version,
    [ValidateSet("nuitka", "pyinstaller")]
    [string]$Engine = "nuitka",
    [string]$InstallerPath,
    [switch]$Commit
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir
$IssFile   = Join-Path $RepoRoot "windows-context-menu\Installer\MarkdownConverter.iss"
$DistDir   = Join-Path $RepoRoot "windows-context-menu\Installer\dist"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stage 4: Package versioned release" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------------------
# Resolve version (from .iss unless overridden)
# ---------------------------------------------------------------------------
if (-not $Version) {
    if (-not (Test-Path $IssFile)) {
        throw "Cannot resolve version: '$IssFile' not found. Pass -Version explicitly."
    }
    $match = Select-String -Path $IssFile -Pattern '#define\s+MyAppVersion\s+"([^"]+)"' |
             Select-Object -First 1
    if (-not $match) {
        throw "Could not find '#define MyAppVersion' in '$IssFile'. Pass -Version explicitly."
    }
    $Version = $match.Matches[0].Groups[1].Value
}
Write-Host "Version: $Version" -ForegroundColor White

# ---------------------------------------------------------------------------
# Resolve the installer .exe
# ---------------------------------------------------------------------------
if (-not $InstallerPath) {
    if (-not (Test-Path $DistDir)) {
        throw "Installer output folder not found: '$DistDir'. Run stage 3 (build-installer.ps1) first."
    }
    $installer = Get-ChildItem $DistDir -Filter "MarkdownConverter-Setup-*.exe" -ErrorAction SilentlyContinue |
                 Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $installer) {
        throw "No MarkdownConverter-Setup-*.exe found in '$DistDir'. Run stage 3 first."
    }
    $InstallerPath = $installer.FullName
}
if (-not (Test-Path $InstallerPath)) {
    throw "Installer not found: '$InstallerPath'."
}
$installerItem = Get-Item $InstallerPath
Write-Host "Installer: $($installerItem.FullName) ($([math]::Round($installerItem.Length/1MB,1)) MB)" -ForegroundColor White

# ---------------------------------------------------------------------------
# Copy into releases\<version>\
# ---------------------------------------------------------------------------
$releaseDir = Join-Path $RepoRoot "releases\$Version"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

$destName = "MarkdownConverter-Setup-$Version.exe"
$destPath = Join-Path $releaseDir $destName
Copy-Item $InstallerPath $destPath -Force
Write-Host "Copied -> $destPath" -ForegroundColor Green

# ---------------------------------------------------------------------------
# Checksum + manifest
# ---------------------------------------------------------------------------
$hash = (Get-FileHash $destPath -Algorithm SHA256).Hash.ToLower()
$sumsPath = Join-Path $releaseDir "SHA256SUMS.txt"
"$hash  $destName" | Set-Content -Path $sumsPath -Encoding ascii -NoNewline
Add-Content -Path $sumsPath -Value "`n" -NoNewline
Write-Host "SHA256: $hash" -ForegroundColor White

$sizeMB = [math]::Round($installerItem.Length / 1MB, 1)
$dateUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss 'UTC'")
$releaseMd = @"
# Markdown Converter $Version

| Field | Value |
| ----- | ----- |
| Version | $Version |
| Installer | ``$destName`` |
| Size | $sizeMB MB |
| SHA-256 | ``$hash`` |
| Engine | $Engine |
| Built (UTC) | $dateUtc |

Install by running the ``.exe`` (requires elevation to register the Explorer
context-menu entries). Verify the download with:

``````powershell
(Get-FileHash "$destName" -Algorithm SHA256).Hash -eq "$hash"
``````
"@
$releaseMdPath = Join-Path $releaseDir "RELEASE.md"
Set-Content -Path $releaseMdPath -Value $releaseMd -Encoding utf8
Write-Host "Manifest -> $releaseMdPath" -ForegroundColor Green

# ---------------------------------------------------------------------------
# Optional commit
# ---------------------------------------------------------------------------
if ($Commit) {
    Write-Host ""
    Write-Host "Committing release folder..." -ForegroundColor Cyan
    Push-Location $RepoRoot
    try {
        git add -- "releases/$Version"
        git commit -m "release: Markdown Converter $Version ($Engine installer)"
    } finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Release $Version packaged" -ForegroundColor Green
Write-Host "  $destPath" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green
if (-not $Commit) {
    Write-Host "Not committed. Re-run with -Commit or commit releases/$Version manually." -ForegroundColor Yellow
}
