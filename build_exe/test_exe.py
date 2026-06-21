#!/usr/bin/env python3
"""
Test the standalone markitdown.exe against the test vectors from _test_vectors.py.
Run this from the build_exe directory after building.
"""

import subprocess
import sys
import os

EXE = os.path.join(os.path.dirname(__file__), "dist", "markitdown", "markitdown.exe")
TEST_DIR = os.path.join(os.path.dirname(__file__), "..", "packages", "markitdown", "tests", "test_files")
EXPECTED_DIR = os.path.join(TEST_DIR, "expected_outputs")

# Test vectors from _test_vectors.py
TESTS = [
    {
        "file": "test.docx",
        "must_include": [
            "314b0a30-5b04-470b-b9f7-eed2c2bec74a",
            "49e168b7-d2ae-407f-a055-2167576f39a1",
            "## d666f1f7-46cb-42bd-9a39-9a39cf2a509f",
            "# Abstract",
            "# Introduction",
            "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation",
            "data:image/png;base64...",
        ],
        "must_not_include": [
            "data:image/png;base64,iVBORw0KGgoAAAANSU",
        ],
    },
    {
        "file": "test_with_comment.docx",
        "must_include": [],  # Just check it doesn't crash
        "must_not_include": [],
    },
    {
        "file": "equations.docx",
        "must_include": [],
        "must_not_include": [],
    },
    {
        "file": "test.xlsx",
        "must_include": [
            "## 09060124-b5e7-4717-9d07-3c046eb",
            "6ff4173b-42a5-4784-9b19-f49caff4d93d",
            "affc7dad-52dc-4b98-9b5d-51e65d8a8ad0",
        ],
        "must_not_include": [],
    },
    {
        "file": "test.xls",
        "must_include": [
            "## 09060124-b5e7-4717-9d07-3c046eb",
            "6ff4173b-42a5-4784-9b19-f49caff4d93d",
            "affc7dad-52dc-4b98-9b5d-51e65d8a8ad0",
        ],
        "must_not_include": [],
    },
    {
        "file": "test.pptx",
        "must_include": [
            "2cdda5c8-e50e-4db4-b5f0-9722a649f455",
            "04191ea8-5c73-4215-a1d3-1cfb43aaaf12",
            "44bf7d06-5e7a-4a40-a2e1-a2e42ef28c8a",
            "1b92870d-e3b5-4e65-8153-919f4ff45592",
            "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation",
            "a3f6004b-6f4f-4ea8-bee3-3741f4dc385f",
            "2003",
            "![This phrase of the caption is Human-written.](Picture4.jpg)",
        ],
        "must_not_include": ["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQE"],
    },
    {
        "file": "test_outlook_msg.msg",
        "must_include": [
            "# Email Message",
            "**From:** test.sender@example.com",
            "**To:** test.recipient@example.com",
            "**Subject:** Test Email Message",
            "## Content",
            "This is the body of the test email message",
        ],
        "must_not_include": [],
    },
    {
        "file": "test.pdf",
        "must_include": [
            "While there is contemporaneous exploration of multi-agent approaches",
        ],
        "must_not_include": [],
    },
    {
        "file": "test_blog.html",
        "must_include": [
            "Large language models (LLMs) are powerful tools",
            "an example where high cost can easily prevent a generic complex",
        ],
        "must_not_include": [],
    },
    {
        "file": "test_wikipedia.html",
        "skip": True,  # WikipediaConverter requires url= hint (no CLI flag)
        "must_include": [],
        "must_not_include": [],
    },
    {
        "file": "test_serp.html",
        "skip": True,  # BingSerpConverter requires url= hint (no CLI flag)
        "must_include": [],
        "must_not_include": [],
    },
    {
        "file": "test_mskanji.csv",
        "extra_args": ["-c", "cp932"],
        "must_include": [
            "| 名前 | 年齢 | 住所 |",
            "| --- | --- | --- |",
            "| 佐藤太郎 | 30 | 東京 |",
            "| 三木英子 | 25 | 大阪 |",
        ],
        "must_not_include": [],
    },
    {
        "file": "test.json",
        "must_include": [
            "5b64c88c-b3c3-4510-bcb8-da0b200602d8",
            "9700dc99-6685-40b4-9a3a-5e406dcb37f3",
        ],
        "must_not_include": [],
    },
    {
        "file": "test_rss.xml",
        "must_include": [
            "# The Official Microsoft Blog",
            "## Ignite 2024: Why nearly 70% of the Fortune 500 now use Microsoft 365 Copilot",
        ],
        "must_not_include": ["<rss", "<feed"],
    },
    {
        "file": "test_notebook.ipynb",
        "must_include": [
            "# Test Notebook",
            "```python",
            'print("markitdown")',
            "## Code Cell Below",
        ],
        "must_not_include": [
            "nbformat",
            "nbformat_minor",
        ],
    },
    {
        "file": "test_files.zip",
        "must_include": [
            "314b0a30-5b04-470b-b9f7-eed2c2bec74a",
            "49e168b7-d2ae-407f-a055-2167576f39a1",
            "2cdda5c8-e50e-4db4-b5f0-9722a649f455",
            "## 09060124-b5e7-4717-9d07-3c046eb",
        ],
        "must_not_include": [],
    },
    {
        "file": "test.epub",
        "must_include": [
            "**Authors:** Test Author",
            "A test EPUB document for MarkItDown testing",
            "# Chapter 1: Test Content",
            "This is a **test** paragraph with some formatting",
            "# Chapter 2: More Content",
        ],
        "must_not_include": [],
    },
    {
        "file": "test.jpg",
        "must_include": [],  # Without exiftool, limited output expected
        "must_not_include": [],
    },
    {
        "file": "test.mp3",
        "must_include": [],  # Without exiftool/ffmpeg, limited output
        "must_not_include": [],
    },
    {
        "file": "test.wav",
        "must_include": [],
        "must_not_include": [],
    },
]


def run_test(test_info):
    filepath = os.path.join(TEST_DIR, test_info["file"])
    if not os.path.isfile(filepath):
        return "SKIP", f"File not found: {filepath}"
    if test_info.get("skip"):
        return "SKIP", test_info.get("skip_reason", "Requires URL hint (not supported in CLI)")

    extra_args = test_info.get("extra_args", [])
    cmd = [EXE] + extra_args + [filepath]

    try:
        result = subprocess.run(
            cmd, capture_output=True, timeout=120
        )
    except subprocess.TimeoutExpired:
        return "FAIL", "Timed out after 120s"
    except Exception as e:
        return "FAIL", f"Exception: {e}"

    if result.returncode != 0:
        stderr = result.stderr[:300].decode("utf-8", errors="replace") if result.stderr else "(no stderr)"
        return "FAIL", f"Exit code {result.returncode}: {stderr}"

    output = result.stdout.decode("utf-8", errors="replace")
    if not output.strip():
        return "WARN", "Empty output"

    # Check must_include
    missing = []
    for needle in test_info.get("must_include", []):
        if needle not in output:
            missing.append(needle[:60])

    # Check must_not_include
    forbidden_found = []
    for needle in test_info.get("must_not_include", []):
        if needle in output:
            forbidden_found.append(needle[:60])

    if missing or forbidden_found:
        parts = []
        if missing:
            parts.append(f"Missing {len(missing)}: {missing}")
        if forbidden_found:
            parts.append(f"Forbidden found {len(forbidden_found)}: {forbidden_found}")
        return "FAIL", "; ".join(parts)

    return "PASS", f"{len(output)} chars, {output.count(chr(10))} lines"


def main():
    if not os.path.isfile(EXE):
        print(f"ERROR: Executable not found at {EXE}")
        sys.exit(1)

    print(f"Testing: {EXE}")
    print(f"Test files: {TEST_DIR}")
    print("=" * 70)

    passed = 0
    failed = 0
    warned = 0
    skipped = 0

    for test in TESTS:
        status, detail = run_test(test)
        icon = {"PASS": "OK", "FAIL": "FAIL", "WARN": "WARN", "SKIP": "SKIP"}[status]
        print(f"  [{icon:4s}] {test['file']:<30s} {detail}")

        if status == "PASS":
            passed += 1
        elif status == "FAIL":
            failed += 1
        elif status == "WARN":
            warned += 1
        else:
            skipped += 1

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed, {warned} warnings, {skipped} skipped")
    print(f"Total:   {len(TESTS)} tests")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
