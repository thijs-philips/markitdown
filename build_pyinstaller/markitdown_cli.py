#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present Adam Fourney <adamfo@microsoft.com>
#
# SPDX-License-Identifier: MIT
"""
PyInstaller entry point for the standalone MarkItDown executable.

Thin shim: configures the bundled external binaries (exiftool, ffmpeg) and then
delegates all argument parsing / conversion to the shared CLI core
(``markitdown_cli_core``), so the PyInstaller and Nuitka builds behave
identically.
"""

import os
import sys

# Make the shared CLI core importable when running unfrozen (dev). When frozen,
# PyInstaller bundles markitdown_cli_core directly and this path simply doesn't
# exist, which is harmless.
_BUILD_COMMON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "build_common"
)
if os.path.isdir(_BUILD_COMMON):
    sys.path.insert(0, _BUILD_COMMON)


def _get_base_dir() -> str:
    """Return the base directory of the frozen application (or this script's dir)."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


def _bootstrap_external_binaries() -> None:
    """
    Detect bundled external binaries (exiftool, ffmpeg) and expose them via the
    environment variables MarkItDown / pydub read at construction time. Must run
    before markitdown is imported.
    """
    base = _get_base_dir()
    externals_dir = os.path.join(base, "external")

    if not os.environ.get("EXIFTOOL_PATH"):
        exiftool_exe = os.path.join(externals_dir, "exiftool.exe")
        if os.path.isfile(exiftool_exe):
            os.environ["EXIFTOOL_PATH"] = exiftool_exe

    if not os.environ.get("FFMPEG_BINARY"):
        ffmpeg_exe = os.path.join(externals_dir, "ffmpeg.exe")
        if os.path.isfile(ffmpeg_exe):
            os.environ["FFMPEG_BINARY"] = ffmpeg_exe
    if not os.environ.get("FFPROBE_BINARY"):
        ffprobe_exe = os.path.join(externals_dir, "ffprobe.exe")
        if os.path.isfile(ffprobe_exe):
            os.environ["FFPROBE_BINARY"] = ffprobe_exe

    if os.path.isdir(externals_dir):
        os.environ["PATH"] = externals_dir + os.pathsep + os.environ.get("PATH", "")


def main() -> None:
    # Force UTF-8 on stdout/stderr so non-ASCII output isn't mangled by the
    # Windows console codepage.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    _bootstrap_external_binaries()

    from markitdown_cli_core import run

    run(version_suffix="(standalone)", base_dir=_get_base_dir())


if __name__ == "__main__":
    main()
