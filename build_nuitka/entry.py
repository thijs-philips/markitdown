#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present Adam Fourney <adamfo@microsoft.com>
#
# SPDX-License-Identifier: MIT
"""
Minimal entry point for the Nuitka-compiled MarkItDown executable.
Reuses the existing markitdown CLI (markitdown.__main__).
"""
import sys
import io

# Force UTF-8 on stdout/stderr so non-ASCII output (e.g. Japanese)
# is not replaced with '?' by the console codepage.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from markitdown.__main__ import main

if __name__ == "__main__":
    main()
