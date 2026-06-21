# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building the MarkItDown standalone Windows executable.

Usage:
    pyinstaller markitdown.spec

This produces a one-directory bundle at dist/markitdown/ containing:
    markitdown.exe          - the main executable
    external/               - bundled external tools (exiftool, ffmpeg)
    ... (supporting DLLs and data files)
"""

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import (
    collect_all,
    collect_data_files,
    collect_submodules,
    copy_metadata,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# SPECPATH is a PyInstaller built-in: the directory containing this .spec file
SPEC_DIR = SPECPATH
EXTERNAL_DIR = os.path.join(SPEC_DIR, "external")

# ---------------------------------------------------------------------------
# Hidden imports: packages that use try/except ImportError guards
# PyInstaller's static analysis should find most of these, but we list them
# explicitly for safety.
# ---------------------------------------------------------------------------
hidden_imports = [
    # Core (required)
    "magika",
    "magika.types",
    "onnxruntime",
    "charset_normalizer",
    "defusedxml",
    "markdownify",
    "bs4",
    "requests",
    # Optional converters — all included for [all] build
    "pptx",
    "mammoth",
    "lxml",
    "lxml.etree",
    "lxml._elementpath",
    "pandas",
    "numpy",
    "openpyxl",
    "xlrd",
    "pdfminer",
    "pdfminer.high_level",
    "pdfminer.layout",
    "pdfminer.pdfpage",
    "pdfplumber",
    "olefile",
    "pydub",
    "speech_recognition",
    "youtube_transcript_api",
    "azure.ai.documentintelligence",
    "azure.identity",
    # Transitive dependencies that may need hints
    "PIL",
    "PIL.Image",
    "certifi",
    "urllib3",
    "idna",
    "packaging",
    "charset_normalizer.md",
]

# Collect submodules for packages with complex internal structures
hidden_imports += collect_submodules("magika")
hidden_imports += collect_submodules("pdfminer")
hidden_imports += collect_submodules("pdfplumber")

# pandas 3.x needs collect_all to bundle properly with PyInstaller
pandas_datas, pandas_binaries, pandas_hiddenimports = collect_all("pandas")
hidden_imports += pandas_hiddenimports

# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------
datas = []

# magika: ONNX model and config files (critical — loaded at runtime)
datas += collect_data_files("magika")

# onnxruntime: native libs and providers
datas += collect_data_files("onnxruntime")

# pdfminer: CMap data for CJK PDF support
datas += collect_data_files("pdfminer")

# pdfplumber: may have data files
datas += collect_data_files("pdfplumber", include_py_files=False)

# certifi: CA bundle for HTTPS requests
datas += collect_data_files("certifi")

# charset_normalizer: data files
datas += collect_data_files("charset_normalizer")

# Copy metadata for markitdown itself (needed for __about__.__version__)
datas += copy_metadata("markitdown")

# pandas 3.x data files
datas += pandas_datas

# ---------------------------------------------------------------------------
# Bundled external binaries
# ---------------------------------------------------------------------------
external_binaries = []

# pandas native libraries
external_binaries += pandas_binaries

if os.path.isdir(EXTERNAL_DIR):
    for fname in os.listdir(EXTERNAL_DIR):
        fpath = os.path.join(EXTERNAL_DIR, fname)
        if os.path.isfile(fpath):
            # Bundle into 'external/' subdirectory within the dist
            external_binaries.append((fpath, "external"))

# ---------------------------------------------------------------------------
# Excluded modules (trim size)
# ---------------------------------------------------------------------------
excludes = [
    "tkinter",
    "matplotlib",
    "scipy",
    "pytest",
    "unittest",
    "test",
    # onnxruntime.quantization requires 'onnx' which is not installed
    "onnxruntime.quantization",
    # Pandas backends we don't need
    "pandas.tests",
    "pandas.io.sql",
    "pandas.io.gbq",
    "pandas.io.stata",
    "pandas.io.sas",
    "pandas.io.spss",
    "pandas.io.feather_format",
    "pandas.io.parquet",
    "pandas.plotting",
]

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    [os.path.join(SPEC_DIR, "markitdown_cli.py")],
    pathex=[],
    binaries=external_binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

# ---------------------------------------------------------------------------
# Remove duplicate data entries
# ---------------------------------------------------------------------------
seen = set()
unique_datas = []
for dest, src, typecode in a.datas:
    if dest not in seen:
        seen.add(dest)
        unique_datas.append((dest, src, typecode))
a.datas = unique_datas

# ---------------------------------------------------------------------------
# PYZ (Python bytecode archive)
# ---------------------------------------------------------------------------
pyz = PYZ(a.pure, a.zipped_data)

# ---------------------------------------------------------------------------
# EXE
# ---------------------------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # one-directory mode
    name="markitdown",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # CLI tool — needs a console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: add an icon if desired
)

# ---------------------------------------------------------------------------
# COLLECT (one-directory bundle)
# ---------------------------------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="markitdown",
)
