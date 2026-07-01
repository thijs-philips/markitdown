"""Text-to-speech samples — two engines, one folder.

This folder contains two TTS approaches. Run them individually or both
at once via this script:

    python tts/run.py              # both engines
    python tts/run_openai.py       # gpt-4o-mini-tts only
    python tts/run_speech.py       # Azure Cognitive Services Speech only

┌──────────────────────┬──────────────────────────────────────────────┐
│ gpt-4o-mini-tts      │ Azure Cognitive Services Speech             │
│ (run_openai.py)      │ (run_speech.py)                             │
├──────────────────────┼──────────────────────────────────────────────┤
│ OpenAI-compatible    │ SSML-based (XML), via sidecar               │
│ API: /v1/audio/speech│ API: /speech/tts (proxy pass-through)       │
│ Voices: alloy, coral,│ Voices: 400+ neural voices across 140+     │
│   echo, shimmer, …   │   locales (en-US-JennyNeural, sv-SE-…)     │
│ Simple: text + voice │ Rich: IPA phonetics, prosody, breaks,       │
│                      │   say-as, emphasis — any SSML element       │
│ Fast, low latency    │ Best for multilingual / precise narration   │
│ No SSML support      │ Full SSML via JsonML (no XML on client)     │
└──────────────────────┴──────────────────────────────────────────────┘

When to use which:
  • gpt-4o-mini-tts — quick prototyping, English-centric, OpenAI SDK.
  • Azure Speech — production multilingual, precise pronunciation
    control (IPA), SSML prosody/breaks, or 400+ voice choices.
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable


def main() -> int:
    rc = 0
    for script in ["run_speech.py", "run_openai.py"]:
        path = HERE / script
        if not path.exists():
            print(f"  SKIP  {script} (not found)")
            continue
        result = subprocess.run([PY, str(path)], cwd=str(HERE))
        rc |= result.returncode
    return rc


if __name__ == "__main__":
    sys.exit(main())
