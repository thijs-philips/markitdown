"""Azure Cognitive Services Speech — TTS via sidecar + proxy.

WHEN TO USE THIS
    • 400+ neural voices across 140+ locales (e.g. en-US-JennyNeural,
      sv-SE-SofieNeural, ja-JP-NanamiNeural).
    • Precise pronunciation control via IPA phonetics.
    • Full SSML support: prosody, breaks, say-as, emphasis, and any
      future SSML element — expressed as JsonML (no XML on client side).
    • Best for multilingual or narration-quality speech.

    Compare with run_openai.py (gpt-4o-mini-tts) which is simpler but
    has fewer voices and no SSML support.

HOW IT WORKS
    Client  ──JSON──▶  LiteLLM proxy (/speech/tts)
                          │  auth + spend tracking
                          ▼
                       tts-sidecar (:8000/tts)
                          │  builds SSML from JSON fields
                          ▼
                       Azure Speech REST endpoint
                          │  returns audio bytes
                          ▼
                       proxy relays audio back to client

Run:
    python tts/run_speech.py

Voice list:
    https://learn.microsoft.com/azure/ai-services/speech-service/language-support
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import make_httpx_client, ok, fail, header  # noqa: E402

PATH = "/speech/tts"
VOICE = "en-US-JennyNeural"
HERE = Path(__file__).resolve().parent

# --- Test 1: plain text ---
TEXT = "Hello from the AI router samples. This audio was synthesised by Azure Cognitive Services Speech."
OUT = HERE / "out.mp3"

# --- Test 2: IPA phonetics ---
# The "ipa" field tells the sidecar to wrap the text in an SSML <phoneme>
# tag. Azure Speech then uses the IPA transcription for pronunciation
# instead of guessing from spelling — useful for proper nouns, foreign
# words, or very precise narration.
PHONETIC_TEXT = "Hello, Azure!"
PHONETIC_IPA = "hɛloʊ ˈæʒər"   # IPA for roughly "hello azure"
OUT_PHONETIC = HERE / "out_phonetic.mp3"

# --- Test 3: full SSML via JsonML ---
# The "ssml" field accepts a JsonML tree — an array-based encoding of
# arbitrary XML.  The sidecar recursively serialises it to SSML so the
# client never touches XML.  This example mixes several SSML elements:
#   • <prosody>  — slow rate
#   • <break>    — 500 ms pause
#   • <say-as>   — read a date properly
#   • <phoneme>  — IPA pronunciation override
ADVANCED_SSML = [
    "prosody", {"rate": "slow"},
    "Welcome. ",
    ["break", {"time": "500ms"}],
    "Today is ",
    ["say-as", {"interpret-as": "date", "format": "dmy"}, "11/05/2026"],
    ". ",
    ["break", {"time": "300ms"}],
    "Let me say hello: ",
    ["phoneme", {"alphabet": "ipa", "ph": "hɛloʊ"}, "hello"],
    "!",
]
OUT_ADVANCED = HERE / "out_advanced.mp3"


def _synth(client, label: str, payload: dict, out_path: Path) -> bool:
    """Send one TTS request and save the result."""
    try:
        r = client.post(PATH, json=payload)
        if r.status_code >= 400:
            fail(label, f"HTTP {r.status_code}: {r.text[:200]}")
            return False
        audio = r.content
        if not audio or len(audio) < 1024:
            fail(label, f"audio too small: {len(audio)} bytes")
            return False
        out_path.write_bytes(audio)
        ok(label, f"wrote {out_path.name} ({len(audio)} bytes)")
        return True
    except Exception as e:  # noqa: BLE001
        fail(label, str(e))
        return False


def main() -> int:
    header(f"tts — Azure Speech ({VOICE}, via proxy)")
    all_ok = True

    with make_httpx_client(timeout=60) as client:
        # 1. Plain text
        if not _synth(client, VOICE, {"text": TEXT, "voice": VOICE}, OUT):
            all_ok = False

        # 2. IPA phonetics — same voice, but pronunciation overridden
        payload_ipa = {"text": PHONETIC_TEXT, "voice": VOICE, "ipa": PHONETIC_IPA}
        if not _synth(client, f"{VOICE} (IPA)", payload_ipa, OUT_PHONETIC):
            all_ok = False

        # 3. Full SSML via JsonML — arbitrary SSML structure as JSON
        payload_ssml = {"ssml": ADVANCED_SSML, "voice": VOICE}
        if not _synth(client, f"{VOICE} (JsonML)", payload_ssml, OUT_ADVANCED):
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
