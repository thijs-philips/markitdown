#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Unified command-line front-end for the frozen MarkItDown executables
(PyInstaller and Nuitka builds both import this module).

Design goals
------------
1. **Explicit streaming.** Reading from stdin requires an explicit ``--stdin``
   flag (or ``-`` as the filename). Running ``markitdown`` with no input no
   longer blocks silently waiting on stdin.
2. **Descriptive messages.** Missing input, unknown flags, or bad paths produce
   a short, human-readable message plus a pointer to ``-h`` — never a Python
   traceback.
3. **No raw tracebacks.** Every unexpected error is caught and rendered as a
   one-line ``error: ...`` message. Set ``MARKITDOWN_TRACEBACK=1`` (or pass
   ``--traceback``) to opt back into the full Python traceback for debugging.

The two frozen entry points stay thin: they perform their build-specific
bootstrap (e.g. PyInstaller wires up bundled exiftool/ffmpeg) and then call
:func:`run`.
"""

from __future__ import annotations

import argparse
import codecs
import glob
import os
import sys
from textwrap import dedent
from typing import List, Optional


class CliError(Exception):
    """A user-facing error. Rendered as ``error: <message>`` with the given exit code."""

    def __init__(self, message: str, code: int = 1):
        super().__init__(message)
        self.code = code


class _FriendlyArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that prints a friendly message instead of a bare usage dump."""

    def error(self, message: str):  # noqa: D401 - argparse signature
        self.print_usage(sys.stderr)
        sys.stderr.write(f"\n{self.prog}: error: {message}\n")
        sys.stderr.write(f"Run '{self.prog} -h' for full usage.\n")
        sys.exit(2)


def _debug_enabled(argv: List[str]) -> bool:
    return "--traceback" in argv or os.environ.get("MARKITDOWN_TRACEBACK") == "1"


def run(*, version_suffix: str = "", base_dir: Optional[str] = None) -> None:
    """
    Entry point used by both frozen builds.

    Parameters
    ----------
    version_suffix:
        Appended to the ``--version`` string, e.g. ``"(standalone)"`` or
        ``"(nuitka)"``.
    base_dir:
        Directory of the frozen application, used by ``--info``. Falls back to
        this module's directory when omitted.
    """
    argv = sys.argv[1:]
    try:
        _run(argv, version_suffix=version_suffix, base_dir=base_dir)
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)
    except BrokenPipeError:
        # Downstream consumer (e.g. `| head`) closed the pipe. Exit quietly.
        try:
            sys.stdout.close()
        except Exception:
            pass
        sys.exit(0)
    except CliError as err:
        print(f"error: {err}", file=sys.stderr)
        sys.exit(err.code)
    except SystemExit:
        raise
    except Exception as err:  # noqa: BLE001 - this is the top-level guard
        if _debug_enabled(argv):
            raise
        print(f"error: {type(err).__name__}: {err}", file=sys.stderr)
        print(
            "\nRun 'markitdown -h' for usage. "
            "Set MARKITDOWN_TRACEBACK=1 (or pass --traceback) for details.",
            file=sys.stderr,
        )
        sys.exit(1)


def _build_parser(version_suffix: str) -> _FriendlyArgumentParser:
    parser = _FriendlyArgumentParser(
        description="Convert various file formats to Markdown.",
        prog="markitdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage=dedent(
            """
            markitdown <FILENAME> [options]
            markitdown --stdin [options] < input
            cat input.pdf | markitdown --stdin

            Convert a document to Markdown. Provide a FILENAME, or pass --stdin
            (or '-' as the filename) to read from standard input.

            EXAMPLES:
                markitdown report.pdf
                markitdown report.pdf -o report.md
                markitdown --stdin -x html < page.html
                type page.html | markitdown --stdin -x html
            """
        ).strip(),
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {_lazy_version()} {version_suffix}".rstrip(),
        help="show the version number and exit",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file name. If omitted, Markdown is written to stdout.",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read the input document from standard input instead of a file.",
    )
    parser.add_argument(
        "-x",
        "--extension",
        help="Hint about the file extension (e.g. when reading from stdin): -x html",
    )
    parser.add_argument(
        "-m",
        "--mime-type",
        help="Hint about the file's MIME type (e.g. application/pdf).",
    )
    parser.add_argument(
        "-c",
        "--charset",
        help="Hint about the file's charset (e.g. UTF-8).",
    )
    parser.add_argument(
        "-d",
        "--use-docintel",
        action="store_true",
        help="Use Azure Document Intelligence instead of offline conversion. "
        "Requires --endpoint.",
    )
    parser.add_argument(
        "-e",
        "--endpoint",
        type=str,
        help="Azure Document Intelligence endpoint. Required with --use-docintel.",
    )
    parser.add_argument(
        "--keep-data-uris",
        action="store_true",
        help="Keep data URIs (e.g. base64 images) in the output instead of truncating them.",
    )
    parser.add_argument(
        "--traceback",
        action="store_true",
        help="Show the full Python traceback if an unexpected error occurs.",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show information about this build and its optional dependencies, then exit.",
    )
    parser.add_argument(
        "filename",
        nargs="?",
        help="Path to the document to convert. Use '-' to read from stdin.",
    )
    return parser


def _lazy_version() -> str:
    try:
        from markitdown.__about__ import __version__

        return __version__
    except Exception:
        return "?"


def _run(argv: List[str], *, version_suffix: str, base_dir: Optional[str]) -> None:
    parser = _build_parser(version_suffix)
    args, remaining = parser.parse_known_args(argv)

    # --info: diagnostics, then exit.
    if args.info:
        _show_info(version_suffix=version_suffix, base_dir=base_dir)
        sys.exit(0)

    # Reassemble an unquoted path that contains spaces (e.g. C:\My Documents\f.pdf).
    if remaining:
        args.filename = _try_reassemble_path(args.filename, remaining)

    # ---- Resolve the input source --------------------------------------
    use_stdin = args.stdin or args.filename == "-"
    if args.filename == "-":
        args.filename = None

    if use_stdin and args.filename is not None:
        raise CliError(
            "Cannot use --stdin together with a filename. "
            "Pass a file, or use --stdin alone.",
            code=2,
        )

    if not use_stdin and args.filename is None:
        # No input was specified.
        if _stdin_is_piped():
            raise CliError(
                "No input specified, but data is being piped in. "
                "Add --stdin (or pass '-') to convert piped input.",
                code=2,
            )
        # Interactive shell with no arguments: show help and exit cleanly.
        parser.print_help()
        sys.exit(0)

    # Validate a real file path up front (turns OSError into a friendly message).
    if args.filename is not None and not os.path.isfile(args.filename):
        _suggest_path_fix(args.filename)

    stream_info = _build_stream_info(args)

    # ---- Convert -------------------------------------------------------
    from markitdown._markitdown import MarkItDown  # lazy: heavy import

    if args.use_docintel:
        if args.endpoint is None:
            raise CliError(
                "--endpoint is required when using --use-docintel.", code=2
            )
        if args.filename is None:
            raise CliError(
                "A filename is required when using --use-docintel.", code=2
            )
        converter = MarkItDown(enable_plugins=False, docintel_endpoint=args.endpoint)
    else:
        converter = MarkItDown(enable_plugins=False)

    if args.filename is None:
        # stdin may be a non-seekable pipe (e.g. `type file | markitdown --stdin`).
        # magika needs to seek the stream, so buffer it into a seekable BytesIO.
        import io

        data = sys.stdin.buffer.read()
        if not data:
            raise CliError("No data received on stdin.", code=2)
        result = converter.convert_stream(
            io.BytesIO(data),
            stream_info=stream_info,
            keep_data_uris=args.keep_data_uris,
        )
    else:
        result = converter.convert(
            args.filename,
            stream_info=stream_info,
            keep_data_uris=args.keep_data_uris,
        )

    _handle_output(args, result)


def _build_stream_info(args):
    from markitdown._markitdown import StreamInfo

    extension_hint = args.extension
    if extension_hint is not None:
        extension_hint = extension_hint.strip().lower()
        if extension_hint:
            if not extension_hint.startswith("."):
                extension_hint = "." + extension_hint
        else:
            extension_hint = None

    mime_type_hint = args.mime_type
    if mime_type_hint is not None:
        mime_type_hint = mime_type_hint.strip()
        if mime_type_hint:
            if mime_type_hint.count("/") != 1:
                raise CliError(f"Invalid MIME type: {mime_type_hint}", code=2)
        else:
            mime_type_hint = None

    charset_hint = args.charset
    if charset_hint is not None:
        charset_hint = charset_hint.strip()
        if charset_hint:
            try:
                charset_hint = codecs.lookup(charset_hint).name
            except LookupError:
                raise CliError(f"Invalid charset: {charset_hint}", code=2)
        else:
            charset_hint = None

    if extension_hint is None and mime_type_hint is None and charset_hint is None:
        return None
    return StreamInfo(
        extension=extension_hint, mimetype=mime_type_hint, charset=charset_hint
    )


def _stdin_is_piped() -> bool:
    """True when stdin has piped/redirected data (not an interactive terminal)."""
    try:
        return not sys.stdin.isatty()
    except Exception:
        return False


def _try_reassemble_path(filename: Optional[str], remaining: List[str]) -> Optional[str]:
    """
    Leftover args usually mean an unquoted path with spaces, e.g.
    ``markitdown C:\\My Documents\\report.pdf`` -> filename="C:\\My",
    remaining=["Documents\\report.pdf"]. Try to rejoin them.
    """
    unknown_flags = [r for r in remaining if r.startswith("-")]
    path_parts = [r for r in remaining if not r.startswith("-")]

    if unknown_flags:
        raise CliError(
            "Unknown option(s): {opts}\nRun 'markitdown -h' for usage.".format(
                opts=" ".join(unknown_flags)
            ),
            code=2,
        )

    if not path_parts:
        return filename

    parts = ([filename] if filename else []) + path_parts
    joined = " ".join(parts)

    if os.path.isfile(joined):
        print(
            f'Note: path contains spaces. Quote it next time: markitdown "{joined}"',
            file=sys.stderr,
        )
        return joined

    raise CliError(
        'File not found: "{joined}"\n'
        "If the path contains spaces, wrap it in quotes:\n"
        '    markitdown "{joined}"'.format(joined=joined),
        code=2,
    )


def _suggest_path_fix(filepath: str) -> None:
    """Raise a CliError with helpful suggestions for a path that doesn't exist."""
    messages = [f'File not found: "{filepath}"']

    parent = os.path.dirname(filepath) or "."
    basename = os.path.basename(filepath)

    if not os.path.isdir(parent):
        messages.append(f'  Directory does not exist: "{parent}"')
    elif basename:
        pattern = os.path.join(parent, f"*{os.path.splitext(basename)[0]}*")
        matches = glob.glob(pattern)
        if matches:
            messages.append("  Did you mean one of these?")
            for m in matches[:5]:
                messages.append(f'    "{m}"')

    if "/" in filepath:
        alt = filepath.replace("/", "\\")
        if os.path.isfile(alt):
            messages.append(f'  Try using backslashes: "{alt}"')

    raise CliError("\n".join(messages), code=2)


def _handle_output(args, result) -> None:
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.markdown)
    else:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write(result.markdown.encode("utf-8"))
            sys.stdout.buffer.write(b"\n")
            sys.stdout.buffer.flush()
        else:
            enc = sys.stdout.encoding or "utf-8"
            print(result.markdown.encode(enc, errors="replace").decode(enc))


def _show_info(*, version_suffix: str, base_dir: Optional[str]) -> None:
    version = _lazy_version()
    label = f"markitdown {version} {version_suffix}".strip()
    print(label)
    print(f"Python: {sys.version}")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    if base_dir:
        print(f"Base dir: {base_dir}")
    print()

    exiftool_path = os.environ.get("EXIFTOOL_PATH", "")
    ffmpeg_path = os.environ.get("FFMPEG_BINARY", "")
    print("External tools:")
    print(
        f"  exiftool: {exiftool_path} [FOUND]"
        if exiftool_path and os.path.isfile(exiftool_path)
        else "  exiftool: not configured (image/audio metadata extraction limited)"
    )
    print(
        f"  ffmpeg:   {ffmpeg_path} [FOUND]"
        if ffmpeg_path and os.path.isfile(ffmpeg_path)
        else "  ffmpeg:   not configured (audio transcription limited)"
    )
    print()

    print("Optional converter dependencies:")
    deps = [
        ("python-pptx", "pptx", "PowerPoint (.pptx)"),
        ("mammoth", "mammoth", "Word (.docx)"),
        ("lxml", "lxml", "XML/HTML parsing"),
        ("pandas", "pandas", "Excel (.xlsx/.xls)"),
        ("openpyxl", "openpyxl", "Excel (.xlsx)"),
        ("xlrd", "xlrd", "Excel (.xls)"),
        ("pdfminer.six", "pdfminer", "PDF"),
        ("pdfplumber", "pdfplumber", "PDF tables"),
        ("olefile", "olefile", "Outlook (.msg)"),
        ("pydub", "pydub", "Audio conversion"),
        ("SpeechRecognition", "speech_recognition", "Speech-to-text"),
        ("youtube-transcript-api", "youtube_transcript_api", "YouTube transcripts"),
        (
            "azure-ai-documentintelligence",
            "azure.ai.documentintelligence",
            "Azure Doc Intelligence",
        ),
    ]
    for package_name, import_name, description in deps:
        try:
            __import__(import_name)
            status = "[OK]"
        except ImportError:
            status = "[MISSING]"
        print(f"  {description:<30} ({package_name}) {status}")
