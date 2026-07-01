"""OpenAI-compatible TTS — gpt-4o-mini-tts via LiteLLM proxy.

WHEN TO USE THIS
    • Standard OpenAI `audio.speech.create()` API — works with any
      OpenAI SDK client.
    • Simple: just text + voice name, no SSML needed.
    • Voices: alloy, ash, ballad, coral, echo, fable, nova, onyx,
      sage, shimmer, verse.
    • Fast, low latency.
    • Best for quick prototyping and English-centric use cases.

    Compare with run_speech.py (Azure Cognitive Services Speech) which
    has 400+ voices, IPA phonetics, and full SSML control.

Run:
    python tts/run_openai.py
    python tts/run_openai.py --voice coral
    python tts/run_openai.py --voice shimmer --text "Custom text"
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import make_openai_client, ok, fail, header  # noqa: E402

MODEL = "gpt-4o-mini-tts"
HERE = Path(__file__).resolve().parent
OUT = HERE / "out_openai.mp3"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Test gpt-4o-mini-tts via proxy")
    parser.add_argument("--voice", default="alloy", help="Voice name (default: alloy)")
    parser.add_argument("--text", default="Hello from the AI router. This is gpt-4o-mini-tts speaking through the LiteLLM proxy.", help="Text to speak")
    args = parser.parse_args()

    client = make_openai_client(timeout=30)
    header(f"tts (OpenAI) — {MODEL}, voice={args.voice}")
    try:
        resp = client.audio.speech.create(
            model=MODEL,
            input=args.text,
            voice=args.voice,
        )
        audio = resp.read()
        if not audio or len(audio) < 1024:
            fail(MODEL, f"audio too small: {len(audio)} bytes")
            return 1
        OUT.write_bytes(audio)
        ok(MODEL, f"wrote {OUT.name} ({len(audio)} bytes)")
        return 0
    except Exception as e:  # noqa: BLE001
        fail(MODEL, str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
