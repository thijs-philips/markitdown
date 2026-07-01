"""Realtime Translation sample (interactive — NOT run in unattended smoke tests).

Connects to gpt-realtime-translate via the sidecar WebSocket proxy.
The sidecar validates the LiteLLM virtual key and forwards to Azure,
so the raw Azure API key never leaves the Docker network.

Translation uses a *dedicated* endpoint path that differs from standard
realtime.  The session streams continuously from incoming audio
(no response.create needed).

Events: session.output_audio.delta, session.output_transcript.delta,
        session.input_transcript.delta

Run manually:
    python realtime/run_translate.py
    python realtime/run_translate.py --language fr
    python realtime/run_translate.py --direct          # bypass sidecar
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

MODEL = "gpt-realtime-translate"

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
        url = f"wss://{AZURE_ENDPOINT}/openai/v1/realtime/translations?model={MODEL}"
        return url, {"api-key": AZURE_API_KEY}
    else:
        ws_base = SIDECAR_BASE.replace("http://", "ws://").replace("https://", "wss://")
        url = f"{ws_base}/realtime/translate?language={language}"
        return url, {"Authorization": f"Bearer {API_KEY}"}


async def run(target_language: str = "es", direct: bool = False) -> int:
    """Connect, configure session, optionally send audio, then disconnect."""
    url, headers = _build_connection(direct, target_language)
    mode = "direct" if direct else "sidecar"

    header(f"realtime-translate → {target_language} ({mode})")
    print(f"  Endpoint: {url}")

    try:
        async with websockets.connect(
            url, additional_headers=headers, open_timeout=15, close_timeout=5,
            ssl=_ssl_for(url),
        ) as ws:
            # 1. Receive session.created
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            event = json.loads(raw)
            if event.get("type") != "session.created":
                fail(MODEL, f"expected session.created, got: {event.get('type')}")
                return 1
            session = event["session"]
            print(f"  Session ID: {session['id']}")
            print(f"  Default input lang: {session['audio']['input'].get('language')}")
            print(f"  Default output lang: {session['audio']['output'].get('language')}")
            print(f"  Default voice: {session['audio']['output'].get('voice')}")

            # 2. Send session.update to configure target language
            session_update = {
                "type": "session.update",
                "session": {
                    "audio": {
                        "output": {
                            "language": target_language,
                        }
                    }
                },
            }
            await ws.send(json.dumps(session_update))
            raw2 = await asyncio.wait_for(ws.recv(), timeout=5)
            event2 = json.loads(raw2)
            if event2.get("type") == "error":
                fail(MODEL, f"session.update error: {event2['error']['message']}")
                return 1
            print(f"  session.update response: {event2.get('type')}")

            ok(MODEL, f"connected, target={target_language}")
            return 0

    except Exception as e:  # noqa: BLE001
        fail(MODEL, str(e))
        return 1


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Test gpt-realtime-translate")
    parser.add_argument("--language", "-l", default="es", help="Target language (default: es)")
    parser.add_argument("--direct", action="store_true", help="Bypass sidecar, connect directly to Azure")
    args = parser.parse_args()
    return asyncio.run(run(target_language=args.language, direct=args.direct))


if __name__ == "__main__":
    sys.exit(main())
