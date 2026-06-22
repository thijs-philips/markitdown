<#
.SYNOPSIS
    Download external tools (exiftool, ffmpeg) for bundling with MarkItDown.

.DESCRIPTION
    Downloads and extracts external binaries to the specified output directory.
    These tools are optional but enhance MarkItDown's capabilities:
    - exiftool: image/audio metadata extraction
    - ffmpeg: audio format conversion (required by pydub for audio transcription)

.PARAMETER Tool
    Which tool to download: "exiftool", "ffmpeg", or "all".

.PARAMETER OutputDir
    Directory to place the downloaded binaries.

.EXAMPLE
    .\download_externals.ps1 -Tool all -OutputDir .\external
    .\download_externals.ps1 -Tool exiftool -OutputDir .\external
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("exiftool", "ffmpeg", "all")]
    [string]$Tool,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir
)

$ErrorActionPreference = "Stop"
$TempDir = Join-Path $env:TEMP "markitdown_external_dl"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

if (-not (Test-Path $TempDir)) {
    New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
}

# ---------------------------------------------------------------------------
# ExifTool
# ---------------------------------------------------------------------------
function Download-ExifTool {
    param([string]$OutDir)

    Write-Host "  Downloading ExifTool for Windows..." -ForegroundColor Cyan

    # ExifTool Windows executable - check the latest version from exiftool.org
    # Using the "exiftool(-VER).zip" naming convention from the official site
    $exiftoolPage = "https://exiftool.org"

    try {
        # Fetch the download page to find the latest Windows zip
        $response = Invoke-WebRequest -Uri $exiftoolPage -UseBasicParsing -TimeoutSec 30

        # Find the Windows standalone executable zip link
        # Pattern: exiftool-XX.XX.zip (the standalone Windows version)
        $zipPattern = 'exiftool-[\d.]+\.zip'
        $match = [regex]::Match($response.Content, "href=`"($zipPattern)`"")

        if ($match.Success) {
            $zipFile = $match.Groups[1].Value
            $downloadUrl = "$exiftoolPage/$zipFile"
        } else {
            # Fallback: try the known URL pattern
            Write-Host "  Could not find download link on page, using fallback..." -ForegroundColor Yellow
            $downloadUrl = "https://exiftool.org/exiftool-13.12.zip"
            $zipFile = "exiftool-13.12.zip"
        }

        Write-Host "  Downloading from: $downloadUrl" -ForegroundColor Gray
        $zipPath = Join-Path $TempDir $zipFile

        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing -TimeoutSec 120

        # Extract
        $extractDir = Join-Path $TempDir "exiftool_extract"
        if (Test-Path $extractDir) { Remove-Item -Recurse -Force $extractDir }
        Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

        # The zip contains "exiftool(-k).exe" — rename to exiftool.exe
        $exeFiles = Get-ChildItem -Path $extractDir -Filter "exiftool*.exe" -Recurse
        if ($exeFiles.Count -gt 0) {
            $destPath = Join-Path $OutDir "exiftool.exe"
            Copy-Item -Path $exeFiles[0].FullName -Destination $destPath -Force
            Write-Host "  ExifTool installed to: $destPath" -ForegroundColor Green
        } else {
            Write-Host "  WARNING: Could not find exiftool exe in downloaded archive!" -ForegroundColor Red
            Write-Host "  Please download manually from https://exiftool.org" -ForegroundColor Yellow
            Write-Host "  Rename 'exiftool(-k).exe' to 'exiftool.exe' and place in: $OutDir" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  ERROR: Failed to download ExifTool: $_" -ForegroundColor Red
        Write-Host "  Manual download: https://exiftool.org" -ForegroundColor Yellow
        Write-Host "  Rename 'exiftool(-k).exe' to 'exiftool.exe' and place in: $OutDir" -ForegroundColor Yellow
    }
}

# ---------------------------------------------------------------------------
# ffmpeg
# ---------------------------------------------------------------------------
function Download-FFmpeg {
    param([string]$OutDir)

    Write-Host "  Downloading ffmpeg for Windows..." -ForegroundColor Cyan

    try {
        # Use gyan.dev builds (widely used, well-maintained Windows builds)
        # "essentials" build is smaller and contains ffmpeg + ffprobe
        $ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

        Write-Host "  Downloading from: $ffmpegUrl" -ForegroundColor Gray
        Write-Host "  (This may take a while — ffmpeg is ~80 MB)" -ForegroundColor Gray
        $zipPath = Join-Path $TempDir "ffmpeg-release-essentials.zip"

        Invoke-WebRequest -Uri $ffmpegUrl -OutFile $zipPath -UseBasicParsing -TimeoutSec 600

        # Extract
        $extractDir = Join-Path $TempDir "ffmpeg_extract"
        if (Test-Path $extractDir) { Remove-Item -Recurse -Force $extractDir }
        Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

        # Find ffmpeg.exe and ffprobe.exe in the extracted tree
        $ffmpegExe = Get-ChildItem -Path $extractDir -Filter "ffmpeg.exe" -Recurse | Select-Object -First 1
        $ffprobeExe = Get-ChildItem -Path $extractDir -Filter "ffprobe.exe" -Recurse | Select-Object -First 1

        if ($ffmpegExe) {
            $destPath = Join-Path $OutDir "ffmpeg.exe"
            Copy-Item -Path $ffmpegExe.FullName -Destination $destPath -Force
            Write-Host "  ffmpeg installed to: $destPath" -ForegroundColor Green
        } else {
            Write-Host "  WARNING: Could not find ffmpeg.exe in downloaded archive!" -ForegroundColor Red
        }

        if ($ffprobeExe) {
            $destPath = Join-Path $OutDir "ffprobe.exe"
            Copy-Item -Path $ffprobeExe.FullName -Destination $destPath -Force
            Write-Host "  ffprobe installed to: $destPath" -ForegroundColor Green
        } else {
            Write-Host "  WARNING: Could not find ffprobe.exe in downloaded archive!" -ForegroundColor Red
        }

        if (-not $ffmpegExe) {
            Write-Host "  Manual download: https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor Yellow
            Write-Host "  Place ffmpeg.exe and ffprobe.exe in: $OutDir" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  ERROR: Failed to download ffmpeg: $_" -ForegroundColor Red
        Write-Host "  Manual download: https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor Yellow
        Write-Host "  Place ffmpeg.exe and ffprobe.exe in: $OutDir" -ForegroundColor Yellow
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
switch ($Tool) {
    "exiftool" { Download-ExifTool -OutDir $OutputDir }
    "ffmpeg"   { Download-FFmpeg -OutDir $OutputDir }
    "all" {
        Download-ExifTool -OutDir $OutputDir
        Download-FFmpeg -OutDir $OutputDir
    }
}

# Cleanup temp
if (Test-Path $TempDir) {
    Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "  External tools directory contents:" -ForegroundColor Cyan
if (Test-Path $OutputDir) {
    Get-ChildItem -Path $OutputDir | ForEach-Object {
        $size = if ($_.Length -gt 1MB) { "$([math]::Round($_.Length / 1MB, 1)) MB" } else { "$([math]::Round($_.Length / 1KB, 1)) KB" }
        Write-Host "    $($_.Name) ($size)" -ForegroundColor White
    }
} else {
    Write-Host "    (empty)" -ForegroundColor Gray
}
