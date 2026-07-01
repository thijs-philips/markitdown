#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present Adam Fourney <adamfo@microsoft.com>
#
# SPDX-License-Identifier: MIT
"""
Nuitka entry point for the compiled MarkItDown executable.

Thin shim: forces UTF-8 console output and delegates all argument parsing /
conversion to the shared CLI core (``markitdown_cli_core``), so the Nuitka and
PyInstaller builds behave identically.
"""

import os
import sys

# Make the shared CLI core importable when running unfrozen (dev). When compiled,
# Nuitka includes markitdown_cli_core in the binary and this path is ignored.
_BUILD_COMMON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "build_common"
)
if os.path.isdir(_BUILD_COMMON):
    sys.path.insert(0, _BUILD_COMMON)

# Force UTF-8 on stdout/stderr so non-ASCII output (e.g. Japanese)
# is not replaced with '?' by the console codepage.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    from markitdown_cli_core import run

    base_dir = (
        os.path.dirname(sys.executable)
        if getattr(sys, "frozen", False)
        else os.path.dirname(os.path.abspath(__file__))
    )
    run(version_suffix="(nuitka)", base_dir=base_dir)


if __name__ == "__main__":
    main()

