# MarkItDown — Windows Standalone Executable

A portable Windows command-line tool that converts documents, spreadsheets, presentations, PDFs, HTML, and many other file formats to Markdown. No Python installation required — just download and run.

## Download & Install

1. Download the latest `markitdown-x.y.z-win-x64.zip` from [Releases](../../releases)
2. Extract the zip to a folder (e.g. `C:\Tools\markitdown\`)
3. (Optional) Add the folder to your system `PATH`

The complete application lives inside the extracted `markitdown\` directory. Keep all files together — the exe depends on libraries in the `_internal\` subdirectory.

## Usage

### Basic conversion

```powershell
markitdown report.pdf                    # prints Markdown to the console
markitdown report.pdf -o report.md       # saves to a file
```

### Supported file formats

| Format | Extensions |
|---|---|
| PDF | `.pdf` |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Excel | `.xlsx`, `.xls` |
| HTML | `.html`, `.htm` |
| CSV | `.csv` |
| JSON | `.json` |
| XML / RSS / Atom | `.xml` |
| EPUB | `.epub` |
| Outlook email | `.msg` |
| Jupyter Notebook | `.ipynb` |
| Images (EXIF metadata) | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff` |
| Audio (metadata / transcription) | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |
| ZIP archives | `.zip` (recursively converts contents) |
| Plain text | `.txt`, `.md`, `.log`, `.yaml`, `.toml`, etc. |

### Reading from stdin

Pipe content from another program (use `-x` to hint the format):

```powershell
type page.html | markitdown -x .html
curl -s https://example.com | markitdown -x .html -o example.md
```

### Charset hint

Specify a charset when the file is not UTF-8:

```powershell
markitdown data.csv -c cp932            # Japanese Shift-JIS CSV
markitdown data.csv -c latin-1          # ISO 8859-1
```

### MIME type hint

Force a specific MIME type when auto-detection doesn't work:

```powershell
markitdown ambiguous_file -m "application/pdf"
```

### Azure Document Intelligence

For scanned PDFs or complex layouts, use Azure's Document Intelligence service:

```powershell
markitdown scan.pdf -d -e "https://YOUR_RESOURCE.cognitiveservices.azure.com/"
```

Requires Azure credentials configured via environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`) or Azure CLI login.

### Keep base64 data URIs

By default, inline images (data URIs) are truncated. To keep them:

```powershell
markitdown page.html --keep-data-uris
```

### Build diagnostics

Check which libraries and external tools are available:

```powershell
markitdown --info
```

Example output:

```
markitdown 0.1.5 (standalone Windows executable)
Python: 3.13.7
Frozen: True
Base dir: C:\Tools\markitdown\_internal

External tools:
  exiftool: C:\Tools\markitdown\_internal\external\exiftool.exe [FOUND]
  ffmpeg:   C:\Tools\markitdown\_internal\external\ffmpeg.exe [FOUND]

Optional converter dependencies:
  PowerPoint (.pptx)             (python-pptx) [OK]
  Word (.docx)                   (mammoth) [OK]
  Excel (.xlsx/.xls)             (pandas) [OK]
  PDF                            (pdfminer.six) [OK]
  ...
```

### All command-line options

```
markitdown [-h] [-v] [-o OUTPUT] [-x EXTENSION] [-m MIME_TYPE]
           [-c CHARSET] [-d] [-e ENDPOINT] [--keep-data-uris] [--info]
           [filename]

positional arguments:
  filename              File to convert (omit to read from stdin)

options:
  -h, --help            Show help and exit
  -v, --version         Show version and exit
  -o, --output OUTPUT   Write output to a file instead of stdout
  -x, --extension EXT   File extension hint (e.g. .html, .pdf)
  -m, --mime-type TYPE  MIME type hint (e.g. application/pdf)
  -c, --charset CHARSET Charset hint (e.g. UTF-8, cp932)
  -d, --use-docintel    Use Azure Document Intelligence
  -e, --endpoint URL    Azure Document Intelligence endpoint
  --keep-data-uris      Keep base64 data URIs in the output
  --info                Show build diagnostics and exit
```

## External Tools (ExifTool & ffmpeg)

The build can optionally bundle **ExifTool** and **ffmpeg** alongside the exe for image metadata extraction and audio conversion:

- **ExifTool** — extracts EXIF metadata from images (`.jpg`, `.png`, etc.) and audio files
- **ffmpeg** — required by SpeechRecognition/pydub for audio format conversion

Without these tools, image and audio conversion still works but with limited output.

You can also provide these tools yourself by setting environment variables:

```powershell
$env:EXIFTOOL_PATH = "C:\path\to\exiftool.exe"
$env:FFMPEG_BINARY = "C:\path\to\ffmpeg.exe"
$env:FFPROBE_BINARY = "C:\path\to\ffprobe.exe"
```

## Differences from the pip-installed version

This standalone exe is functionally equivalent to `pip install 'markitdown[all]'` with two exceptions:

| Feature | `pip install markitdown` | Standalone exe |
|---|---|---|
| `--use-plugins` / `--list-plugins` | Available | Removed (plugins require a Python environment) |
| `--info` | Not available | Added (shows bundled tools and dependency status) |

All conversion capabilities and other CLI flags are identical.

---

## Building from Source

### Prerequisites

- **Windows 10/11** (x64)
- **Python 3.10+** (3.12 or 3.13 recommended)
- **PowerShell 5.1+** (bundled with Windows)

### Quick build

```powershell
cd build_pyinstaller
.\build.ps1
```

This will:
1. Create a virtual environment in `build_pyinstaller/.venv/`
2. Install `markitdown[all]` and PyInstaller
3. Download ExifTool and ffmpeg
4. Run PyInstaller to produce the directory bundle
5. Verify the build
6. Package into `dist/markitdown-x.y.z-win-x64.zip`

The output is at `build_pyinstaller/dist/markitdown/markitdown.exe`.

### Build options

```powershell
.\build.ps1                  # Full build with external tools
.\build.ps1 -Clean           # Clean previous artifacts first
.\build.ps1 -SkipExternals   # Skip ExifTool/ffmpeg download
.\build.ps1 -SkipVenv        # Use current Python environment
.\build.ps1 -OneFile         # Single-file exe (slower startup)
```

### Manual build (step by step)

If you prefer to run each step yourself:

```powershell
cd build_pyinstaller

# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install ../packages/markitdown[all] pyinstaller

# 3. (Optional) Download external tools
.\download_externals.ps1 -Tool exiftool -OutputDir external
.\download_externals.ps1 -Tool ffmpeg -OutputDir external

# 4. Build
pyinstaller markitdown.spec --noconfirm --clean

# 5. Verify
.\dist\markitdown\markitdown.exe --version
.\dist\markitdown\markitdown.exe --info
```

### Manual external tool setup

If the automated download fails, place the binaries manually:

**ExifTool:**
1. Download from https://exiftool.org — get the "Windows Executable" zip
2. Rename `exiftool(-k).exe` → `exiftool.exe`
3. Place in `build_pyinstaller/external/exiftool.exe`

**ffmpeg:**
1. Download from https://www.gyan.dev/ffmpeg/builds/ — get the "essentials" build
2. Extract `ffmpeg.exe` and `ffprobe.exe` from the `bin/` directory
3. Place both in `build_pyinstaller/external/`

### Running the test suite

After building, verify the exe against the project's test files:

```powershell
cd build_pyinstaller
python test_exe.py
```

This tests all supported formats against the expected outputs from the test suite.

### CI/CD

The GitHub Actions workflow at `.github/workflows/build-exe.yml` automates the build:

- **Manual trigger**: Actions → "Build Windows Executable" → Run workflow
- **Tag trigger**: Push a tag like `v1.2.3` to automatically build and attach to a draft release

Artifacts are uploaded and retained for 30 days.

## Directory Structure

```
build_pyinstaller/
├── build.ps1                 # Main build script
├── download_externals.ps1    # Downloads ExifTool & ffmpeg
├── markitdown_cli.py         # Standalone CLI entry point
├── markitdown.spec           # PyInstaller spec file
├── test_exe.py               # Test script for the built exe
├── README.md                 # This file
├── external/                 # External binaries (created during build)
│   ├── exiftool.exe
│   ├── ffmpeg.exe
│   └── ffprobe.exe
├── dist/                     # Build output
│   ├── markitdown/
│   │   ├── markitdown.exe
│   │   ├── _internal/
│   │   │   ├── external/     # Bundled ExifTool & ffmpeg
│   │   │   └── ...           # Python runtime & libraries
│   │   └── ...
│   └── markitdown-x.y.z-win-x64.zip
└── build/                    # Intermediate build files
```

## Expected Size

| Build variant | Approximate size |
|---|---|
| Directory bundle (uncompressed) | ~200 MB |
| Directory bundle (zipped) | ~60–80 MB |
| Without ExifTool/ffmpeg (zipped) | ~50–70 MB |

The largest components are onnxruntime (~50–80 MB, used by magika for file-type detection) and numpy/pandas (~60 MB, for Excel support).

## Troubleshooting

### "Failed to import encodings module" or "Failed to execute script"
The `_internal/` directory next to `markitdown.exe` must be intact. Don't move or rename `markitdown.exe` without its `_internal/` folder.

### ExifTool / ffmpeg not detected
1. Run `markitdown --info` to see if external tools are found
2. Verify the binaries exist in the `_internal/external/` subdirectory
3. Or set `EXIFTOOL_PATH` and `FFMPEG_BINARY` environment variables to point to your own copies

### Antivirus false positives
PyInstaller executables are occasionally flagged by antivirus software. This is a [known issue](https://github.com/pyinstaller/pyinstaller/issues/6754). Code-signing the executable resolves this for distribution.

### Build fails with import errors
- Use Python 3.10+ (3.12 or 3.13 recommended)
- Run `pip install markitdown[all] pyinstaller --upgrade`
- Ensure `magika~=0.6.1` installs correctly (requires `onnxruntime`)

