"""Realtime Transcription (Whisper) sample (interactive — NOT run in unattended tests).

Connects to gpt-realtime-whisper via the sidecar WebSocket proxy.
The sidecar validates the LiteLLM virtual key and forwards to Azure,
so the raw Azure API key never leaves the Docker network.

The transcription endpoint uses a different protocol from standard realtime:
- First event is `transcription_session.created` (not session.created)
- Configure via `transcription_session.update` (not session.update)
- Model is specified in session config, NOT in the URL
- Events: conversation.item.input_audio_transcription.delta / .completed

Run manually:
    python realtime/run_whisper.py
    python realtime/run_whisper.py --language sv
    python realtime/run_whisper.py --direct          # bypass sidecar
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import PROXY_BASE_URL, API_KEY, SSL_VERIFY, header, ok, fail  # noqa: E402

import ssl as _ssl  # noqa: E402
import websockets  # noqa: E402

# Permissive SSL context for wss:// behind a corporate TLS-interception proxy.
_SSL_CTX = None
if not SSL_VERIFY:
    _SSL_CTX = _ssl.create_default_context()
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = _ssl.CERT_NONE


def _ssl_for(url: str):
    """Only attach an SSL context to wss:// URLs (ws:// must get ssl=None)."""
    return _SSL_CTX if url.startswith("wss://") else None

MODEL = "gpt-realtime-whisper"
API_VERSION = "2025-04-01-preview"

# Sidecar proxy (default) — uses LiteLLM virtual key
SIDECAR_BASE = os.environ.get("SIDECAR_BASE_URL", "ws://localhost:8000")

# Direct Azure (--direct flag) — uses raw Azure key
AZURE_ENDPOINT = os.environ.get(
    "AZURE_REALTIME_ENDPOINT",
    "iexigtsazurioneyeai-can-resource.openai.azure.com",
)
AZURE_API_KEY = os.environ.get(
    "AZURE_REALTIME_API_KEY",
    os.environ.get("AZURE_API_KEY_CANADA", ""),
)


def _build_connection(direct: bool, language: str):
    """Return (url, headers) for either sidecar or direct Azure."""
    if direct:
        url = f"wss://{AZURE_ENDPOINT}/openai/realtime?api-version={API_VERSION}&intent=transcription"
        return url, {"api-key": AZURE_API_KEY}
    else:
        ws_base = SIDECAR_BASE.replace("http://", "ws://").replace("https://", "wss://")
        url = f"{ws_base}/realtime/transcribe?language={language}"
        return url, {"Authorization": f"Bearer {API_KEY}"}


async def run(language: str = "en", direct: bool = False) -> int:
    """Connect, configure transcription session, then disconnect."""
    url, headers = _build_connection(direct, language)
    mode = "direct" if direct else "sidecar"

    header(f"realtime-whisper (transcription, lang={language}, {mode})")
    print(f"  Endpoint: {url}")

    try:
        async with websockets.connect(
            url, additional_headers=headers, open_timeout=15, close_timeout=5,
            ssl=_ssl_for(url),
        ) as ws:
            # 1. Receive transcription_session.created
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            event = json.loads(raw)
            if event.get("type") != "transcription_session.created":
                fail(MODEL, f"expected transcription_session.created, got: {event.get('type')}")
                return 1
            session = event["session"]
            print(f"  Session ID: {session['id']}")
            print(f"  Input format: {session.get('input_audio_format')}")
            print(f"  Turn detection: {session.get('turn_detection', {}).get('type')}")

            # 2. Send transcription_session.update to configure model and language
            session_update = {
                "type": "transcription_session.update",
                "session": {
                    "input_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": MODEL,
                        "language": language,
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 500,
                    },
                },
            }
            await ws.send(json.dumps(session_update))
            raw2 = await asyncio.wait_for(ws.recv(), timeout=5)
            event2 = json.loads(raw2)

            if event2.get("type") == "error":
                fail(MODEL, f"session update error: {event2['error']['message']}")
                return 1

            print(f"  session update response: {event2.get('type')}")
            if event2.get("type") == "transcription_session.updated":
                sess = event2.get("session", {})
                txn = sess.get("input_audio_transcription", {})
                print(f"  Configured model: {txn.get('model')}")
                print(f"  Configured language: {txn.get('language')}")

            ok(MODEL, f"connected, model={MODEL}, lang={language}")
            return 0

    except Exception as e:  # noqa: BLE001
        fail(MODEL, str(e))
        return 1


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Test gpt-realtime-whisper transcription")
    parser.add_argument("--language", "-l", default="en", help="Language hint (default: en)")
    parser.add_argument("--direct", action="store_true", help="Bypass sidecar, connect directly to Azure")
    args = parser.parse_args()
    return asyncio.run(run(language=args.language, direct=args.direct))


if __name__ == "__main__":
    sys.exit(main())
