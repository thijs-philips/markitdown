<#
.SYNOPSIS
    Install the MarkdownConverter context-menu app locally (without building the
    Inno Setup installer) and register the Windows Explorer "Convert to Markdown"
    menu.

.DESCRIPTION
    Mirrors a published build into the install directory, then runs the app's
    own `install` verb to register the classic + Windows 11 context menus.

    Registration writes to HKLM/HKCR, so this script self-elevates via UAC if it
    is not already running as Administrator.

    Run stage 1+2 first so the engine is bundled in the publish output:
      build_pyinstaller\build.ps1   (or build_nuitka\build.ps1)
      scripts\integrate-engine.ps1 -Engine pyinstaller
      dotnet publish windows-context-menu\MarkdownConverter.csproj -c Release -r win-x64 --self-contained false -o windows-context-menu\Installer\publish

.PARAMETER PublishDir
    Folder containing the published MarkdownConverter.exe (default: the app's
    Installer\publish).

.PARAMETER InstallDir
    Destination install folder (default: C:\Program Files\MarkdownConverter).

.PARAMETER Uninstall
    Unregister the context menu and remove the install directory instead of
    installing.

.EXAMPLE
    .\install-local.ps1
    .\install-local.ps1 -Uninstall
#>
[CmdletBinding()]
param(
    [string]$PublishDir,
    [string]$InstallDir = (Join-Path $env:ProgramFiles "MarkdownConverter"),
    [switch]$Uninstall,
    [switch]$NoPause
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir
if (-not $PublishDir) {
    $PublishDir = Join-Path $RepoRoot "windows-context-menu\Installer\publish"
}

# ---------------------------------------------------------------------------
# Schedule-DeleteOnReboot: queue a locked file/folder for deletion at next boot
# via MoveFileEx(MOVEFILE_DELAY_UNTIL_REBOOT). The Session Manager (smss.exe)
# processes these from HKLM\...\PendingFileRenameOperations very early in boot,
# before any shell host can re-lock the COM DLL. Returns the number of paths
# scheduled. Requires administrator (writes to a protected location's queue).
# ---------------------------------------------------------------------------
function Schedule-DeleteOnReboot {
    param([Parameter(Mandatory)][string]$Path)

    if (-not ("MarkdownConverter.RebootDelete" -as [type])) {
        Add-Type -Namespace MarkdownConverter -Name RebootDelete -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet=System.Runtime.InteropServices.CharSet.Unicode, SetLastError=true)]
public static extern bool MoveFileEx(string lpExistingFileName, string lpNewFileName, int dwFlags);
'@
    }
    $MOVEFILE_DELAY_UNTIL_REBOOT = 0x4

    # PowerShell marshals $null for a [string] P/Invoke arg as an EMPTY string,
    # not a NULL pointer. MoveFileEx needs a real NULL destination to mean
    # "delete on reboot"; use [NullString]::Value to send one.
    $nullDest = [NullString]::Value

    # Schedule deepest paths first (files before their parent directories) so the
    # directories are empty by the time their own delete is processed.
    $targets = @()
    if (Test-Path $Path) {
        $targets += Get-ChildItem -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue |
                    Sort-Object FullName -Descending
    }
    $count = 0
    foreach ($t in $targets) {
        if ([MarkdownConverter.RebootDelete]::MoveFileEx($t.FullName, $nullDest, $MOVEFILE_DELAY_UNTIL_REBOOT)) {
            $count++
        }
    }
    if ([MarkdownConverter.RebootDelete]::MoveFileEx($Path, $nullDest, $MOVEFILE_DELAY_UNTIL_REBOOT)) {
        $count++
    }
    return $count
}

# ---------------------------------------------------------------------------
# Self-elevate (registration touches HKLM\Software\Classes + HKCR)
# ---------------------------------------------------------------------------
$isAdmin = ([System.Security.Principal.WindowsPrincipal] `
    [System.Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[Elevate] Requesting administrator privileges..." -ForegroundColor Yellow
    $argList = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", "`"$PSCommandPath`"",
        "-PublishDir", "`"$PublishDir`"",
        "-InstallDir", "`"$InstallDir`""
    )
    if ($Uninstall) { $argList += "-Uninstall" }
    if ($NoPause)   { $argList += "-NoPause" }
    Start-Process -FilePath "pwsh.exe" -Verb RunAs -ArgumentList $argList
    return
}

$exeName = "MarkdownConverter.exe"
$installedExe = Join-Path $InstallDir $exeName

if ($Uninstall) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Uninstall MarkdownConverter" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    if (Test-Path $installedExe) {
        Write-Host "[Uninstall] Unregistering context menu..." -ForegroundColor Yellow
        & $installedExe uninstall --silent
        Start-Sleep -Milliseconds 500
    } else {
        Write-Host "[Uninstall] $installedExe not found; skipping unregister." -ForegroundColor Yellow
    }
    if (Test-Path $InstallDir) {
        # Explorer loads MarkdownConverter.ContextMenu.comhost.dll into its own
        # process for the Windows 11 menu. Unregistering the CLSID does NOT
        # unload an already-loaded DLL, so the file stays locked and the folder
        # removal fails. Restart Explorer to release the handle, then remove
        # with a short retry loop in case the lock lingers briefly.
        Write-Host "[Uninstall] Restarting Explorer to release the COM handler..." -ForegroundColor Yellow
        Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2   # Explorer auto-restarts

        Write-Host "[Uninstall] Removing $InstallDir ..." -ForegroundColor Yellow
        for ($i = 0; $i -lt 5 -and (Test-Path $InstallDir); $i++) {
            try {
                Remove-Item $InstallDir -Recurse -Force -ErrorAction Stop
            } catch {
                Start-Sleep -Seconds 1
            }
        }
        if (Test-Path $InstallDir) {
            # Last resort: a shell host still holds the comhost DLL and won't let
            # go without a reboot. Schedule the leftover files+folder for deletion
            # at next boot via MoveFileEx(MOVEFILE_DELAY_UNTIL_REBOOT), which the
            # Session Manager processes before anything locks the DLL again.
            Write-Host "[Uninstall] Files still locked; scheduling removal at next reboot..." -ForegroundColor Yellow
            $scheduled = Schedule-DeleteOnReboot -Path $InstallDir
            if ($scheduled -gt 0) {
                Write-Host "[Uninstall] $scheduled item(s) will be deleted after you restart Windows." -ForegroundColor Green
            } else {
                Write-Warning "Could not schedule reboot cleanup for $InstallDir. Remove it manually after a restart."
            }
        }
    }
    Write-Host "[Uninstall] Done." -ForegroundColor Green
    if (-not $NoPause) { Write-Host "Press any key to close..."; [void][System.Console]::ReadKey($true) }
    return
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Install MarkdownConverter (local)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# Validate publish output
# ---------------------------------------------------------------------------
$srcExe = Join-Path $PublishDir $exeName
if (-not (Test-Path $srcExe)) {
    throw "Published app not found at '$srcExe'. Publish first (see this script's help)."
}

# ---------------------------------------------------------------------------
# Mirror publish output into the install directory
# ---------------------------------------------------------------------------
Write-Host "[Install] Source: $PublishDir" -ForegroundColor Yellow
Write-Host "[Install] Dest:   $InstallDir" -ForegroundColor Yellow
# /R:2 /W:1 = fail fast (default is ~1M retries @ 30s) so a locked file (e.g. a
# comhost.dll still held by a shell host from a prior install) can't hang the
# copy for hours. Exit code 8+ is a genuine failure; 1-7 are success/info.
robocopy $PublishDir $InstallDir /MIR /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) {
    Write-Warning "robocopy reported errors (exit $LASTEXITCODE) - likely a locked file (e.g. comhost.dll in use). Continuing; re-run after a reboot for a fully clean copy."
} else {
    Write-Host "[Install] Files copied." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Register the context menu (classic + Windows 11) via the app's install verb
# ---------------------------------------------------------------------------
Write-Host "[Install] Registering context menu..." -ForegroundColor Yellow
& $installedExe install --silent
Start-Sleep -Milliseconds 500

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------
$clsid = "{e7b3c5a2-9d14-4f67-b8e1-6c2a4d7f9e03}"
$reg = "Registry::HKEY_LOCAL_MACHINE\Software\Classes\CLSID\$clsid\InprocServer32"
if (Test-Path $reg) {
    $dll = (Get-ItemProperty $reg).'(default)'
    Write-Host "[Verify] Convert CLSID -> $dll" -ForegroundColor Green
}
$cmd = (Get-ItemProperty "Registry::HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\ConvertToMarkdown\command" -ErrorAction SilentlyContinue).'(default)'
Write-Host "[Verify] .pdf classic command -> $cmd" -ForegroundColor Green

Write-Host ""
Write-Host "[Install] Done. Right-click a PDF/DOCX/etc. to test 'Convert to Markdown'." -ForegroundColor Green
if (-not $NoPause) { Write-Host "Press any key to close..."; [void][System.Console]::ReadKey($true) }
