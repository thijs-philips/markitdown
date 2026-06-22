# MarkItDown — Nuitka Native Build

An alternative packaging chain that compiles MarkItDown to a native Windows executable using [Nuitka](https://nuitka.net/) (Python → C → machine code). Produces a faster, smaller binary compared to PyInstaller.

## Comparison with PyInstaller build

| Metric | PyInstaller (`build_pyinstaller/`) | Nuitka (`build_nuitka/`) |
|---|---|---|
| EXE size | 14.2 MB | 46.5 MB |
| Dist folder | ~180 MB | **103.7 MB** |
| Startup (warm) | ~1150 ms | **~335 ms** |
| HTML conversion (warm) | ~1215 ms | **~360 ms** |
| Runtime speed | 1x | **~3x faster** |

The Nuitka build is larger as a single EXE (more code compiled in) but the total distribution is smaller and significantly faster at runtime.

## Prerequisites

- **Python 3.11+** (tested with 3.13)
- **MSVC** (Visual Studio 2022 Build Tools) — or Zig as fallback
- **Windows 10/11 x64**

MSVC is auto-detected. If not available, use `-Compiler zig` (slower build).

## Quick Start

```powershell
cd build_nuitka
.\build.ps1
```

The output lands in `build_nuitka/output/markitdown/`:

```
output/
  markitdown/
    markitdown.exe      # The compiled binary
    python313.dll       # CPython runtime
    *.pyd               # Compiled extension modules
    certifi/            # CA certificates
    pdfminer/           # PDF cmap data
    ...
  markitdown-x.y.z-nuitka-win-x64.zip   # Distribution archive
```

## Build Options

```powershell
# Clean build (removes previous artifacts)
.\build.ps1 -Clean

# Use Zig compiler instead of MSVC (cross-platform, slower build)
.\build.ps1 -Compiler zig

# Skip venv creation (use current Python environment)
.\build.ps1 -SkipVenv
```

## Lightweight Dependencies

This build uses a lean dependency set that replaces heavy packages:

| Original | Replacement | Size savings |
|---|---|---|
| `magika` + `onnxruntime` + `numpy` | `filetype` + text heuristics | ~54 MB |
| `pandas` (for XLSX) | `openpyxl` + `xlrd` direct | ~13 MB |

The replacements are built into the markitdown source code:
- [`_filetype_detector.py`](../packages/markitdown/src/markitdown/_filetype_detector.py) — drop-in magika replacement
- [`_xlsx_converter.py`](../packages/markitdown/src/markitdown/converters/_xlsx_converter.py) — pandas-free XLSX/XLS conversion

All 109 test vectors pass with these replacements.

## Usage

Once built, use exactly like the PyInstaller version:

```powershell
.\output\markitdown\markitdown.exe report.pdf
.\output\markitdown\markitdown.exe page.html -o page.md
type data.csv | .\output\markitdown\markitdown.exe -x .csv
```

## Architecture

```
build_nuitka/
├── build.ps1           # Main build script
├── entry.py            # Minimal entry point (imports markitdown.__main__)
├── requirements.txt    # Lean dependency list
└── README.md           # This file
```

The build compiles ~700 C source files using MSVC `cl.exe`, producing a native x64 binary with the CPython runtime embedded.
