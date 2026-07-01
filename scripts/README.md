# Windows build pipeline

These scripts turn the Python **MarkItDown** library into a Windows
Explorer context-menu app with an installer, in three stages:

```
Stage 1  Compile MarkItDown          ──►  a standalone markitdown.exe folder
Stage 2  Integrate into the app      ──►  staged under Third-Party/markitdown
Stage 3  Build the installer         ──►  MarkdownConverter-Setup-x.y.z.exe
```

## Layout (hybrid: stage logic lives with its code; glue lives here)

| Stage | Script | Lives in | What it does |
|-------|--------|----------|--------------|
| 1 (Nuitka)      | `build_nuitka/build.ps1`        | engine dir | Compiles MarkItDown with Nuitka → `build_nuitka/output/markitdown/` |
| 1 (PyInstaller) | `build_pyinstaller/build.ps1`   | engine dir | Freezes MarkItDown with PyInstaller → `build_pyinstaller/dist/markitdown/` |
| 2 | [`scripts/integrate-engine.ps1`](integrate-engine.ps1) | **here** | Mirrors the chosen engine into `windows-context-menu/Third-Party/markitdown/` |
| 3 | `windows-context-menu/Installer/build-installer.ps1` | app dir | `dotnet publish` (bundles the engine) → Inno Setup installer |
| all | [`scripts/build-all.ps1`](build-all.ps1) | **here** | Optional orchestrator that runs 1 → 2 → 3 |

## Quick start

Run the whole pipeline (defaults to the Nuitka engine):

```powershell
scripts\build-all.ps1
```

Use the PyInstaller engine instead:

```powershell
scripts\build-all.ps1 -Engine pyinstaller
```

Rebuild only the app + installer, reusing the last engine build:

```powershell
scripts\build-all.ps1 -SkipEngine
```

## Running stages individually

```powershell
# Stage 1 — pick ONE engine
build_nuitka\build.ps1                 # Nuitka  (faster runtime, smaller dist)
build_pyinstaller\build.ps1            # PyInstaller

# Stage 2 — stage that engine into the context-menu app
scripts\integrate-engine.ps1 -Engine nuitka        # or -Engine pyinstaller
scripts\integrate-engine.ps1 -Engine nuitka -Build # also dotnet build to verify

# Stage 3 — publish app + build installer
windows-context-menu\Installer\build-installer.ps1
windows-context-menu\Installer\build-installer.ps1 -SelfContained
```

## Engine choice

Both engines emit a self-contained `markitdown/` folder containing
`markitdown.exe`, so stage 2/3 work with either. Differences:

| | Nuitka (default) | PyInstaller |
|---|---|---|
| Dist folder layout | flat (`*.dll`, `*.pyd`, data dirs) | `_internal/` subfolder |
| Dist size | ~104 MB | ~180 MB |
| Warm startup | ~335 ms | ~1150 ms |
| Build prerequisite | MSVC (or Zig) | none |

## Prerequisites

- **Python 3.11+** (engine build)
- **MSVC** (Visual Studio 2022 Build Tools) for the Nuitka engine — or `-Compiler zig`
- **.NET 10 SDK** (x64) for the C# app
- **Inno Setup 6** for the installer: `winget install --id JRSoftware.InnoSetup -e`
