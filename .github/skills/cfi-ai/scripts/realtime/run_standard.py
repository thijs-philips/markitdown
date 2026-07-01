"""Realtime sample (interactive — NOT run in unattended smoke tests).

Connects to the LiteLLM proxy's WebSocket endpoint for Azure's gpt-realtime
deployments. A full session would send audio frames and stream responses;
this sample only connects, waits for the first server event, and
disconnects.

Run manually:
    python realtime/run_standard.py gpt-realtime
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import PROXY_BASE_URL, API_KEY, SSL_VERIFY, header, ok, fail  # noqa: E402

import ssl as _ssl  # noqa: E402
import websockets  # noqa: E402

# Permissive SSL context for wss:// behind a corporate TLS-interception proxy.
# None means "use the default secure context" (normal verification).
_SSL_CTX = None
if not SSL_VERIFY:
    _SSL_CTX = _ssl.create_default_context()
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = _ssl.CERT_NONE


def _ssl_for(url: str):
    """Only attach an SSL context to wss:// URLs (ws:// must get ssl=None)."""
    return _SSL_CTX if url.startswith("wss://") else None


async def run(model: str) -> int:
    ws_base = PROXY_BASE_URL.replace("http://", "ws://").replace("https://", "wss://")
    url = f"{ws_base}/v1/realtime?model={model}"
    header(f"realtime — {model}")
    try:
        async with websockets.connect(
            url,
            additional_headers={"Authorization": f"Bearer {API_KEY}"},
            open_timeout=15,
            close_timeout=5,
            ssl=_ssl_for(url),
        ) as ws:
            # Wait for the first server event.
            raw = await asyncio.wait_for(ws.recv(), timeout=15)
            event = json.loads(raw)
            ok(model, f"first event: {event.get('type', '<no type>')}")
            return 0
    except Exception as e:  # noqa: BLE001
        fail(model, str(e))
        return 1


def main() -> int:
    model = sys.argv[1] if len(sys.argv) > 1 else "gpt-realtime"
    return asyncio.run(run(model))


if __name__ == "__main__":
    sys.exit(main())
