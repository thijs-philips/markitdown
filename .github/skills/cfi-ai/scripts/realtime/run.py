"""Realtime samples runner — runs all three realtime scripts.

Three models, three scripts:
    run_standard.py   — gpt-realtime (standard OpenAI realtime via proxy)
    run_translate.py  — gpt-realtime-translate (via sidecar WebSocket proxy)
    run_whisper.py    — gpt-realtime-whisper transcription (via sidecar)

All are interactive and NOT included in the unattended run_all.py suite.

Run:
    python realtime/run.py            # all three
    python realtime/run_standard.py   # just standard realtime
    python realtime/run_translate.py  # just translate
    python realtime/run_whisper.py    # just whisper
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable

SCRIPTS = ["run_standard.py", "run_translate.py", "run_whisper.py"]


def main() -> int:
    rc = 0
    for script in SCRIPTS:
        path = HERE / script
        if not path.exists():
            print(f"  SKIP  {script} (not found)")
            continue
        result = subprocess.run([PY, str(path)], cwd=str(HERE))
        rc |= result.returncode
    return rc


if __name__ == "__main__":
    sys.exit(main())
