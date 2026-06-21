#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present Adam Fourney <adamfo@microsoft.com>
#
# SPDX-License-Identifier: MIT
"""
Standalone CLI entry point for the MarkItDown Windows executable.

This is a modified version of markitdown.__main__ that:
- Auto-configures paths to bundled external binaries (exiftool, ffmpeg)
- Removes plugin-related options (plugins cannot work in a frozen exe)
- Provides a --version flag that includes "(standalone)" suffix
"""

import argparse
import sys
import os
import codecs
from textwrap import dedent

# ---------------------------------------------------------------------------
# Frozen-exe bootstrap: set up paths to bundled external binaries BEFORE
# importing markitdown, because MarkItDown.__init__ reads EXIFTOOL_PATH
# at construction time.
# ---------------------------------------------------------------------------


def _get_base_dir() -> str:
    """Return the base directory of the frozen application or script dir."""
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


def _bootstrap_external_binaries() -> None:
    """
    Detect and configure bundled external binaries (exiftool, ffmpeg).
    Sets environment variables so that markitdown and pydub can find them.
    """
    base = _get_base_dir()
    externals_dir = os.path.join(base, "external")

    # --- exiftool ---
    if not os.environ.get("EXIFTOOL_PATH"):
        exiftool_exe = os.path.join(externals_dir, "exiftool.exe")
        if os.path.isfile(exiftool_exe):
            os.environ["EXIFTOOL_PATH"] = exiftool_exe

    # --- ffmpeg ---
    # pydub looks for ffmpeg/ffprobe on PATH, or via FFMPEG_BINARY / FFPROBE_BINARY
    if not os.environ.get("FFMPEG_BINARY"):
        ffmpeg_exe = os.path.join(externals_dir, "ffmpeg.exe")
        if os.path.isfile(ffmpeg_exe):
            os.environ["FFMPEG_BINARY"] = ffmpeg_exe
    if not os.environ.get("FFPROBE_BINARY"):
        ffprobe_exe = os.path.join(externals_dir, "ffprobe.exe")
        if os.path.isfile(ffprobe_exe):
            os.environ["FFPROBE_BINARY"] = ffprobe_exe

    # Also prepend externals_dir to PATH so subprocess calls find them
    if os.path.isdir(externals_dir):
        os.environ["PATH"] = externals_dir + os.pathsep + os.environ.get("PATH", "")


# Run bootstrap before any markitdown imports
_bootstrap_external_binaries()

# Now safe to import markitdown
from markitdown.__about__ import __version__  # noqa: E402
from markitdown._markitdown import MarkItDown, StreamInfo, DocumentConverterResult  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Convert various file formats to markdown.",
        prog="markitdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage=dedent(
            """
            SYNTAX:

                markitdown <OPTIONAL: FILENAME>
                If FILENAME is empty, markitdown reads from stdin.

            EXAMPLE:

                markitdown example.pdf

                OR

                cat example.pdf | markitdown

                OR

                markitdown < example.pdf

                OR to save to a file use

                markitdown example.pdf -o example.md

                OR

                markitdown example.pdf > example.md
            """
        ).strip(),
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__} (standalone)",
        help="show the version number and exit",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file name. If not provided, output is written to stdout.",
    )

    parser.add_argument(
        "-x",
        "--extension",
        help="Provide a hint about the file extension (e.g., when reading from stdin).",
    )

    parser.add_argument(
        "-m",
        "--mime-type",
        help="Provide a hint about the file's MIME type.",
    )

    parser.add_argument(
        "-c",
        "--charset",
        help="Provide a hint about the file's charset (e.g, UTF-8).",
    )

    parser.add_argument(
        "-d",
        "--use-docintel",
        action="store_true",
        help="Use Document Intelligence to extract text instead of offline conversion. "
        "Requires a valid Document Intelligence Endpoint.",
    )

    parser.add_argument(
        "-e",
        "--endpoint",
        type=str,
        help="Document Intelligence Endpoint. Required if using Document Intelligence.",
    )

    parser.add_argument(
        "--keep-data-uris",
        action="store_true",
        help="Keep data URIs (like base64-encoded images) in the output. "
        "By default, data URIs are truncated.",
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show information about bundled external tools and exit.",
    )

    parser.add_argument("filename", nargs="?")
    args, remaining = parser.parse_known_args()

    # --- Smart path detection ---
    # If there are leftover arguments, they're likely parts of an unquoted path
    # with spaces (e.g. `markitdown C:\My Documents\file.pdf`).
    if remaining:
        args.filename = _try_reassemble_path(args.filename, remaining, parser)

    # --info: show diagnostic information about the standalone build
    if args.info:
        _show_info()
        sys.exit(0)

    # If no filename and stdin is a terminal (not piped), show help
    if args.filename is None and sys.stdin.isatty():
        parser.print_help()
        sys.exit(0)

    # Validate the file exists before attempting conversion
    if args.filename is not None and not os.path.isfile(args.filename):
        _suggest_path_fix(args.filename)

    # Parse the extension hint
    extension_hint = args.extension
    if extension_hint is not None:
        extension_hint = extension_hint.strip().lower()
        if len(extension_hint) > 0:
            if not extension_hint.startswith("."):
                extension_hint = "." + extension_hint
        else:
            extension_hint = None

    # Parse the mime type
    mime_type_hint = args.mime_type
    if mime_type_hint is not None:
        mime_type_hint = mime_type_hint.strip()
        if len(mime_type_hint) > 0:
            if mime_type_hint.count("/") != 1:
                _exit_with_error(f"Invalid MIME type: {mime_type_hint}")
        else:
            mime_type_hint = None

    # Parse the charset
    charset_hint = args.charset
    if charset_hint is not None:
        charset_hint = charset_hint.strip()
        if len(charset_hint) > 0:
            try:
                charset_hint = codecs.lookup(charset_hint).name
            except LookupError:
                _exit_with_error(f"Invalid charset: {charset_hint}")
        else:
            charset_hint = None

    stream_info = None
    if (
        extension_hint is not None
        or mime_type_hint is not None
        or charset_hint is not None
    ):
        stream_info = StreamInfo(
            extension=extension_hint, mimetype=mime_type_hint, charset=charset_hint
        )

    if args.use_docintel:
        if args.endpoint is None:
            _exit_with_error(
                "Document Intelligence Endpoint is required when using Document Intelligence."
            )
        elif args.filename is None:
            _exit_with_error("Filename is required when using Document Intelligence.")

        markitdown = MarkItDown(
            enable_plugins=False, docintel_endpoint=args.endpoint
        )
    else:
        markitdown = MarkItDown(enable_plugins=False)

    if args.filename is None:
        result = markitdown.convert_stream(
            sys.stdin.buffer,
            stream_info=stream_info,
            keep_data_uris=args.keep_data_uris,
        )
    else:
        result = markitdown.convert(
            args.filename, stream_info=stream_info, keep_data_uris=args.keep_data_uris
        )

    _handle_output(args, result)


def _try_reassemble_path(filename, remaining, parser):
    """
    When argparse finds leftover arguments, they are most likely fragments
    of a file path that contains spaces and wasn't quoted.

    Example:
        markitdown C:\\My Documents\\report.pdf
        → filename = "C:\\My", remaining = ["Documents\\report.pdf"]

    Try joining the pieces back together. If the reconstructed path exists,
    use it. Otherwise, give a helpful error.
    """
    # Filter out anything that looks like an unknown flag
    unknown_flags = [r for r in remaining if r.startswith("-")]
    path_parts = [r for r in remaining if not r.startswith("-")]

    if unknown_flags:
        # Genuine unknown options — report them
        _exit_with_error(
            f"Unknown option(s): {' '.join(unknown_flags)}\n"
            f"Run 'markitdown -h' for usage information."
        )

    if not path_parts:
        return filename

    # Reconstruct: join filename + remaining path parts with spaces
    parts = ([filename] if filename else []) + path_parts
    joined = " ".join(parts)

    if os.path.isfile(joined):
        print(
            f'Note: Path contains spaces. Consider quoting it: markitdown "{joined}"',
            file=sys.stderr,
        )
        return joined

    # Maybe the user just passed multiple wrong things — give a clear error
    _exit_with_error(
        f'File not found: "{joined}"\n'
        f"\n"
        f"If the path contains spaces, wrap it in quotes:\n"
        f'    markitdown "{joined}"'
    )


def _suggest_path_fix(filepath):
    """
    The given file path doesn't exist. Try to give a helpful suggestion:
    - Check for common typos (wrong slashes, missing extension)
    - Look for similar files in the same directory
    """
    import glob

    messages = [f'File not found: "{filepath}"']

    # Check if the parent directory exists
    parent = os.path.dirname(filepath) or "."
    basename = os.path.basename(filepath)

    if not os.path.isdir(parent):
        messages.append(f'  Directory does not exist: "{parent}"')
    elif basename:
        # Look for similar files (case-insensitive, partial match)
        pattern = os.path.join(parent, f"*{os.path.splitext(basename)[0]}*")
        matches = glob.glob(pattern)
        if matches:
            messages.append("  Did you mean one of these?")
            for m in matches[:5]:
                messages.append(f'    "{m}"')

    # Check for forward-slash vs backslash issues
    if "/" in filepath:
        alt = filepath.replace("/", "\\")
        if os.path.isfile(alt):
            messages.append(f'  Try using backslashes: "{alt}"')

    _exit_with_error("\n".join(messages))


def _handle_output(args, result: DocumentConverterResult):
    """Handle output to stdout or file."""
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.markdown)
    else:
        # Force UTF-8 on stdout to avoid mangling non-ASCII chars on Windows
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write(result.markdown.encode("utf-8"))
            sys.stdout.buffer.write(b"\n")
            sys.stdout.buffer.flush()
        else:
            print(
                result.markdown.encode(sys.stdout.encoding, errors="replace").decode(
                    sys.stdout.encoding
                )
            )


def _show_info():
    """Print diagnostic info about the standalone build."""
    print(f"markitdown {__version__} (standalone Windows executable)")
    print(f"Python: {sys.version}")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    print(f"Base dir: {_get_base_dir()}")
    print()

    # External tools
    exiftool_path = os.environ.get("EXIFTOOL_PATH", "")
    ffmpeg_path = os.environ.get("FFMPEG_BINARY", "")

    print("External tools:")
    if exiftool_path and os.path.isfile(exiftool_path):
        print(f"  exiftool: {exiftool_path} [FOUND]")
    else:
        print(f"  exiftool: not bundled (image/audio metadata extraction disabled)")

    if ffmpeg_path and os.path.isfile(ffmpeg_path):
        print(f"  ffmpeg:   {ffmpeg_path} [FOUND]")
    else:
        print(f"  ffmpeg:   not bundled (audio transcription may be limited)")

    print()

    # Check optional converter dependencies
    print("Optional converter dependencies:")
    _check_dep("python-pptx", "pptx", "PowerPoint (.pptx)")
    _check_dep("mammoth", "mammoth", "Word (.docx)")
    _check_dep("lxml", "lxml", "XML/HTML parsing")
    _check_dep("pandas", "pandas", "Excel (.xlsx/.xls)")
    _check_dep("openpyxl", "openpyxl", "Excel (.xlsx)")
    _check_dep("xlrd", "xlrd", "Excel (.xls)")
    _check_dep("pdfminer.six", "pdfminer", "PDF")
    _check_dep("pdfplumber", "pdfplumber", "PDF tables")
    _check_dep("olefile", "olefile", "Outlook (.msg)")
    _check_dep("pydub", "pydub", "Audio conversion")
    _check_dep("SpeechRecognition", "speech_recognition", "Speech-to-text")
    _check_dep("youtube-transcript-api", "youtube_transcript_api", "YouTube transcripts")
    _check_dep("azure-ai-documentintelligence", "azure.ai.documentintelligence", "Azure Doc Intelligence")


def _check_dep(package_name: str, import_name: str, description: str):
    """Check if a dependency is available and print status."""
    try:
        __import__(import_name)
        print(f"  {description:<30} ({package_name}) [OK]")
    except ImportError:
        print(f"  {description:<30} ({package_name}) [MISSING]")


def _exit_with_error(message: str):
    print(message)
    sys.exit(1)


if __name__ == "__main__":
    main()
