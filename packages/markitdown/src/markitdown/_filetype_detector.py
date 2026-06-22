"""
Lightweight file type detector — drop-in replacement for the magika-based
detection used in _markitdown.py.

Uses the ``filetype`` library (magic-bytes, ~12 KB, zero deps) for binary
formats and simple heuristics for text-based formats (HTML, CSV, JSON, XML,
Markdown, RSS/Atom).  This avoids pulling in onnxruntime + numpy (~54 MB)
that magika requires.

The public API mirrors only the subset of magika that _markitdown.py uses:

    detector = LightFileTypeDetector()
    result   = detector.identify_stream(file_stream)

    result.status                          # "ok"
    result.prediction.output.label         # e.g. "pdf"
    result.prediction.output.mime_type     # e.g. "application/pdf"
    result.prediction.output.extensions    # e.g. ["pdf"]
    result.prediction.output.is_text       # bool
"""

from __future__ import annotations

import re
from typing import BinaryIO, List

import filetype as _filetype


# ---------------------------------------------------------------------------
# Result dataclasses (mimic magika's nested structure)
# ---------------------------------------------------------------------------

class _Output:
    __slots__ = ("label", "mime_type", "extensions", "is_text")

    def __init__(
        self,
        label: str,
        mime_type: str,
        extensions: List[str],
        is_text: bool,
    ):
        self.label = label
        self.mime_type = mime_type
        self.extensions = extensions
        self.is_text = is_text


class _Prediction:
    __slots__ = ("output",)

    def __init__(self, output: _Output):
        self.output = output


class _Result:
    __slots__ = ("status", "prediction")

    def __init__(self, status: str, prediction: _Prediction):
        self.status = status
        self.prediction = prediction


# ---------------------------------------------------------------------------
# Text-format sniffing heuristics
# ---------------------------------------------------------------------------

# Compiled once at import time.
_RE_HTML = re.compile(
    rb"<(!doctype\s+html|html|head|body|div|p\b|span|table|script|style)\b",
    re.IGNORECASE,
)
_RE_XML_DECL = re.compile(rb"<\?xml\b", re.IGNORECASE)
_RE_RSS_ATOM = re.compile(
    rb"<(rss\b|feed\b|channel\b)", re.IGNORECASE
)


def _sniff_text(head: bytes) -> _Output | None:
    """Return an _Output for text-based formats, or None if undetermined."""
    stripped = head.lstrip()

    # JSON / JSONL – starts with { or [
    if stripped[:1] in (b"{", b"["):
        return _Output("json", "application/json", ["json", "jsonl", "ipynb"], is_text=True)

    # XML family (must check before HTML since XHTML is also XML)
    if _RE_XML_DECL.search(head[:256]) or _RE_RSS_ATOM.search(head[:512]):
        return _Output("xml", "text/xml", ["xml"], is_text=True)

    # HTML
    if _RE_HTML.search(head[:4096]):
        return _Output("html", "text/html", ["html", "htm"], is_text=True)

    # CSV – at least 2 lines with the same number of commas (≥1)
    lines = head[:4096].split(b"\n")[:10]
    non_empty = [ln for ln in lines if ln.strip()]
    if len(non_empty) >= 2:
        counts = [ln.count(b",") for ln in non_empty]
        if counts[0] >= 1 and len(set(counts)) == 1:
            return _Output("csv", "text/csv", ["csv"], is_text=True)

    # Markdown – look for common Markdown patterns
    if stripped[:2] in (b"# ", b"##") or stripped[:3] in (b"---", b"***", b"```"):
        return _Output("markdown", "text/markdown", ["md", "markdown"], is_text=True)

    return None


# ---------------------------------------------------------------------------
# Public detector class
# ---------------------------------------------------------------------------

class LightFileTypeDetector:
    """Drop-in replacement for ``magika.Magika()``."""

    def identify_stream(self, file_stream: BinaryIO) -> _Result:
        cur_pos = file_stream.tell()
        try:
            head = file_stream.read(8192)
        finally:
            file_stream.seek(cur_pos)

        if not head:
            return _Result(
                "ok",
                _Prediction(_Output("unknown", "", [], is_text=False)),
            )

        # 1) Try binary magic-bytes detection via filetype lib
        kind = _filetype.guess(head)
        if kind is not None:
            label = kind.extension  # e.g. "pdf", "docx", "epub"
            return _Result(
                "ok",
                _Prediction(
                    _Output(
                        label=label,
                        mime_type=kind.mime,
                        extensions=[label],
                        is_text=False,
                    )
                ),
            )

        # 2) Text-based heuristic sniffing
        text_output = _sniff_text(head)
        if text_output is not None:
            return _Result("ok", _Prediction(text_output))

        # 3) Check if the content looks like valid text at all
        try:
            head[:2048].decode("utf-8")
            is_text = True
        except (UnicodeDecodeError, ValueError):
            is_text = False

        if is_text:
            return _Result(
                "ok",
                _Prediction(
                    _Output("txt", "text/plain", ["txt"], is_text=True)
                ),
            )

        # 4) Unknown binary
        return _Result(
            "ok",
            _Prediction(_Output("unknown", "", [], is_text=False)),
        )
