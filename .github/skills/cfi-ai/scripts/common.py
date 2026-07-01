"""Shared helpers for all LiteLLM proxy samples.

Loads PROXY_BASE_URL and LITELLM_API_KEY from .env (or environment),
exposes a configured OpenAI client, an httpx client for pass-through, and
small print helpers so each sample stays minimal.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

import httpx
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from samples/Python/.env (one level up from any sample dir, or
# next to this file when imported by a script in the same dir).
HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

PROXY_BASE_URL: str = os.environ.get("PROXY_BASE_URL", "http://localhost:4000").rstrip("/")
API_KEY: str = os.environ.get("LITELLM_API_KEY", "")


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off", ""}


# Honor SSL_VERIFY=False to allow running behind a corporate TLS-interception
# proxy. When false we also silence urllib3's noisy InsecureRequestWarning.
SSL_VERIFY: bool = _env_bool("SSL_VERIFY", True)
if not SSL_VERIFY:
    import warnings
    try:
        from urllib3.exceptions import InsecureRequestWarning  # type: ignore
        warnings.simplefilter("ignore", InsecureRequestWarning)
    except Exception:  # pragma: no cover
        pass


if not API_KEY:
    print("ERROR: LITELLM_API_KEY is not set. Copy .env.example to .env and fill it in.", file=sys.stderr)
    sys.exit(2)


def make_openai_client(timeout: float = 300.0) -> OpenAI:
    """OpenAI SDK pointed at the LiteLLM proxy."""
    return OpenAI(
        base_url=f"{PROXY_BASE_URL}/v1",
        api_key=API_KEY,
        timeout=timeout,
        http_client=httpx.Client(verify=SSL_VERIFY, timeout=timeout),
    )


def make_httpx_client(timeout: float = 300.0) -> httpx.Client:
    """Raw httpx client for pass-through / non-OpenAI shapes."""
    return httpx.Client(
        base_url=PROXY_BASE_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=timeout,
        verify=SSL_VERIFY,
    )


# ---- pretty-printing -------------------------------------------------------

_GREEN = "\033[92m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_RESET = "\033[0m"


def _color(s: str, c: str) -> str:
    # ANSI codes are usually fine on modern Windows terminals; if not, the
    # raw codes are harmless noise in a log file.
    return f"{c}{s}{_RESET}"


def ok(model: str, snippet: str = "") -> None:
    print(_color(f"  PASS  ", _GREEN), model, "-", snippet[:60])


def fail(model: str, err: str) -> None:
    print(_color(f"  FAIL  ", _RED), model, "-", err[:120])


def skip(model: str, reason: str) -> None:
    print(_color(f"  SKIP  ", _YELLOW), model, "-", reason)


def header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def first_text(content) -> str:
    """Best-effort extract a short snippet from a completion response."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content.replace("\n", " ").strip()
    if isinstance(content, Iterable):
        for part in content:
            text = getattr(part, "text", None) or (part.get("text") if isinstance(part, dict) else None)
            if text:
                return text.replace("\n", " ").strip()
    return str(content)[:80]
