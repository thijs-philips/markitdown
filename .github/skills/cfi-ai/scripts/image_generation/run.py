"""Image generation samples — gpt-image-2, MAI-Image-2, FLUX.2-pro.

THREE MODELS, TWO API SHAPES
    gpt-image-2  — standard OpenAI `images.generate()` via SDK.
    MAI-Image-2  — Microsoft AI model, POST /image/mai (proxy pass-through).
    FLUX.2-pro   — Black Forest Labs, POST /image/flux (proxy pass-through).

    All three go through the LiteLLM proxy and require only a virtual key.
    The pass-through detail is invisible to callers — everyone just POSTs
    JSON and gets base64-encoded image bytes back.

GOTCHAS
    - gpt-image-2 latency is typically 60-200s, occasionally >5 minutes.
    - MAI-Image-2 requires width/height ≥ 768 pixels.
    - Azure can return EngineOverloaded (429) — retry with backoff.

Run:
    python image_generation/run.py              # all three
    python image_generation/run.py gpt-image-2  # just one
    python image_generation/run.py MAI-Image-2 FLUX.2-pro
"""

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import make_openai_client, make_httpx_client, ok, fail, header  # noqa: E402

HERE = Path(__file__).resolve().parent
PROMPT = "A small orange cat sleeping on a wooden windowsill, soft morning light"


# ── gpt-image-2 (OpenAI SDK) ──────────────────────────────────────────
def run_gpt_image_2() -> int:
    client = make_openai_client(timeout=300)
    model = "gpt-image-2"
    header(f"image_generation — {model}")
    try:
        resp = client.images.generate(
            model=model,
            prompt=PROMPT,
            size="1024x1024",
            n=1,
        )
        d = resp.data[0]
        if getattr(d, "b64_json", None):
            out = HERE / "out.png"
            out.write_bytes(base64.b64decode(d.b64_json))
            ok(model, f"saved {out.name} ({out.stat().st_size} bytes)")
        elif getattr(d, "url", None):
            ok(model, f"url={d.url[:60]}...")
        else:
            fail(model, "no b64_json or url in response")
            return 1
        return 0
    except Exception as e:  # noqa: BLE001
        fail(model, str(e))
        return 1


# ── MAI-Image-2 / FLUX.2-pro (pass-through) ───────────────────────────
PASSTHROUGH_MODELS = {
    "MAI-Image-2": {
        "path": "/image/mai",
        "body": {"prompt": PROMPT, "width": 1024, "height": 1024, "n": 1, "model": "MAI-Image-2"},
        "out": "out_mai.png",
    },
    "FLUX.2-pro": {
        "path": "/image/flux",
        "body": {"prompt": PROMPT, "width": 1024, "height": 1024, "n": 1, "model": "FLUX.2-pro"},
        "out": "out_flux.png",
    },
}


def run_passthrough(model: str) -> int:
    cfg = PASSTHROUGH_MODELS[model]
    header(f"image_generation — {model}")
    with make_httpx_client(timeout=180) as client:
        try:
            r = client.post(cfg["path"], json=cfg["body"])
            if r.status_code >= 400:
                fail(model, f"HTTP {r.status_code}: {r.text[:300]}")
                return 1
            data = r.json()
            items = data.get("data", [])
            if not items:
                fail(model, "empty data array")
                return 1
            b64 = items[0].get("b64_json", "")
            if not b64:
                url = items[0].get("url", "")
                if url:
                    ok(model, f"url={url[:60]}...")
                    return 0
                fail(model, "no b64_json or url in response")
                return 1
            img = base64.b64decode(b64)
            out = HERE / cfg["out"]
            out.write_bytes(img)
            ok(model, f"wrote {out.name} ({len(img)} bytes)")
            return 0
        except Exception as e:  # noqa: BLE001
            fail(model, str(e))
        return 1


# ── main ───────────────────────────────────────────────────────────────
ALL_MODELS = ["gpt-image-2", "MAI-Image-2", "FLUX.2-pro"]


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Test image generation models")
    parser.add_argument("models", nargs="*", default=ALL_MODELS,
                        help=f"Models to test (default: all). Choices: {', '.join(ALL_MODELS)}")
    args = parser.parse_args()

    rc = 0
    for m in args.models:
        if m == "gpt-image-2":
            rc |= run_gpt_image_2()
        else:
            rc |= run_passthrough(m)
    return rc


if __name__ == "__main__":
    sys.exit(main())
