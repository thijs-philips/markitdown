"""Speech-to-text — ``client.audio.transcriptions.create(...)`` via the proxy.

WHY THIS EXISTS
    LiteLLM exposes the OpenAI ``/v1/audio/transcriptions`` surface and
    routes the ``model`` name to the matching Azure OpenAI transcription
    deployment. From the caller's side it is just the OpenAI SDK pointed at
    the proxy:
        client = OpenAI(base_url="http://localhost:4000/v1", api_key=...)
        client.audio.transcriptions.create(model="gpt-4o-transcribe", file=...)

    Three deployments are exercised:
      * ``gpt-4o-transcribe``         — full-fidelity, ``json`` response
      * ``gpt-4o-mini-transcribe``    — cheaper/faster sibling, ``json``
      * ``gpt-4o-transcribe-diarize`` — per-speaker segments via
        ``response_format=diarized_json``

A short test clip is synthesised on the fly through the proxy's
``gpt-4o-mini-tts`` deployment so the sample is self-contained; if a
``sample_speech.mp3`` is already present it is reused.

NOTE
    Azure Cognitive Services Speech (the ConversationTranscriber diarizer in
    the native ``samples_native`` suite) speaks its own websocket protocol and
    does NOT route through LiteLLM — it is intentionally omitted here. Speaker
    diarization through the proxy is available via the ``-diarize`` deployment.

Run:
    python transcriptions/run.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import make_openai_client, ok, fail, header  # noqa: E402

TTS_MODEL = "gpt-4o-mini-tts"

DEPLOYMENTS = [
    ("gpt-4o-transcribe",         "json"),
    ("gpt-4o-mini-transcribe",    "json"),
    ("gpt-4o-transcribe-diarize", "diarized_json"),
]

HERE = Path(__file__).resolve().parent
CLIP = HERE / "sample_speech.mp3"
SAMPLE_TEXT = (
    "The quick brown fox jumps over the lazy dog. "
    "Azure AI Foundry hosts many speech models in Sweden Central."
)
EXPECTED_PHRASES = ["fox", "Azure"]


def ensure_clip(client) -> bytes:
    if CLIP.exists() and CLIP.stat().st_size > 1024:
        return CLIP.read_bytes()
    print(f"  generating sample clip via {TTS_MODEL} -> {CLIP.name}")
    resp = client.audio.speech.create(
        model=TTS_MODEL,
        voice="alloy",
        input=SAMPLE_TEXT,
    )
    audio = resp.read()
    CLIP.write_bytes(audio)
    print(f"  wrote {CLIP.name} ({len(audio)} bytes)")
    return audio


def transcribe(client, deployment: str, response_format: str, audio: bytes) -> int:
    try:
        result = client.audio.transcriptions.create(
            model=deployment,
            file=(CLIP.name, audio, "audio/mpeg"),
            response_format=response_format,
        )
        text = getattr(result, "text", None) or str(result)
        missing = [p for p in EXPECTED_PHRASES if p.lower() not in text.lower()]
        if missing:
            fail(deployment, f"missing phrases {missing} in: {text[:120]}")
            return 1

        snippet = text.replace("\n", " ")[:40]
        extra = ""
        if response_format == "diarized_json":
            segments = getattr(result, "segments", None) or []
            speakers = sorted({getattr(s, "speaker", None) for s in segments} - {None})
            extra = f" [segments={len(segments)} speakers={','.join(speakers) or '?'}]"
        ok(deployment, snippet + extra)
        return 0
    except Exception as e:  # noqa: BLE001 — sample script
        fail(deployment, str(e))
        return 1


def main() -> int:
    client = make_openai_client(timeout=120)
    header("transcriptions — gpt-4o-transcribe family")
    try:
        audio = ensure_clip(client)
    except Exception as e:  # noqa: BLE001
        fail("setup", f"could not produce test clip: {e}")
        return 1

    failures = 0
    for deployment, response_format in DEPLOYMENTS:
        failures += transcribe(client, deployment, response_format, audio)
    print(f"\n{len(DEPLOYMENTS) - failures}/{len(DEPLOYMENTS)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
