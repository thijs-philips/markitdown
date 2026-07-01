"""OCR sample — Mistral Document AI on Foundry, via proxy pass-through.

WHY THIS EXISTS
    Foundry's `mistral-document-ai-2505` is an OCR / document-understanding
    model. Unlike chat models, it does NOT live on the OpenAI-compatible
    surface. Its endpoint is:

        https://<resource>.services.ai.azure.com/providers/mistral/azure/ocr

    and it expects Mistral's native payload, not the OpenAI vision shape:

        {"model": "<deployment>",
         "document": {"type": "image_url", "image_url": "<data-url-or-https-url>"}}

    For non-OpenAI surfaces like this we configure a **pass-through** in
    `experiment/litellm/config.yaml`:

        general_settings:
          pass_through_endpoints:
            - path: "/foundry/mistral-ocr"
              target: "<the URL above>"
              headers:
                api-key: "os.environ/AZURE_API_KEY"
                content-type: "application/json"

    The caller still authenticates with their LiteLLM virtual key
    (Authorization: Bearer ...) and the proxy injects the upstream
    Azure key, so the secret is never exposed to clients.

WHAT THIS SAMPLE SHOWS
    1. Build a small PNG containing realistic invoice-like text using
       Pillow (so the test is self-contained — no committed binaries).
    2. Send it to `/foundry/mistral-ocr` as a base64 data URL.
    3. Print the recognised text and verify a known phrase comes back.

EXPECTED OUTPUT
    The `pages` field contains one entry per page; `pages[0].markdown`
    is the recognised text formatted as Markdown (tables become Markdown
    tables, etc.). For our generated image we expect to see the strings
    "INVOICE #2026-0001", "Acme Robotics", and the line item amounts.
"""

import base64
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import make_httpx_client, ok, fail, header  # noqa: E402

MODEL = "mistral-document-ai-2505"
PATH = "/foundry/mistral-ocr"
HERE = Path(__file__).resolve().parent
SAMPLE_PNG = HERE / "sample_invoice.png"
EXPECTED_PHRASES = ["INVOICE", "Acme Robotics", "BLUE-OWL-42"]


def build_sample_image() -> bytes:
    """Render a small invoice-style PNG with Pillow.

    Doing this at runtime keeps the repo free of binary fixtures and lets
    you tweak the text to see how the OCR responds.
    """
    from PIL import Image, ImageDraw, ImageFont  # local import keeps
                                                  # samples without OCR
                                                  # working without Pillow

    img = Image.new("RGB", (900, 520), "white")
    draw = ImageDraw.Draw(img)

    # Try a couple of common system fonts; fall back to PIL's default.
    def _font(size: int):
        for name in ("arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    big = _font(34)
    med = _font(22)
    small = _font(18)

    draw.text((30, 25), "INVOICE #2026-0001", fill="black", font=big)
    draw.text((30, 80), "Acme Robotics, Inc.", fill="black", font=med)
    draw.text((30, 110), "1 Iguana Way, Sweden", fill="black", font=small)
    draw.text((30, 135), "Project codename: BLUE-OWL-42", fill="black", font=small)

    draw.line([(30, 175), (870, 175)], fill="black", width=2)
    draw.text((30, 185), "Description", fill="black", font=med)
    draw.text((520, 185), "Qty", fill="black", font=med)
    draw.text((620, 185), "Unit", fill="black", font=med)
    draw.text((760, 185), "Total", fill="black", font=med)
    draw.line([(30, 220), (870, 220)], fill="black", width=1)

    rows = [
        ("Quad-A actuator",        "4",  "$120.00", "$480.00"),
        ("Lidar housing",          "1",  "$340.00", "$340.00"),
        ("Cable harness, 2m",      "12", "$ 18.50", "$222.00"),
        ("Calibration, on-site",   "1",  "$200.00", "$200.00"),
    ]
    y = 230
    for desc, qty, unit, total in rows:
        draw.text((30, y),  desc,  fill="black", font=small)
        draw.text((520, y), qty,   fill="black", font=small)
        draw.text((620, y), unit,  fill="black", font=small)
        draw.text((760, y), total, fill="black", font=small)
        y += 32

    draw.line([(30, y + 5), (870, y + 5)], fill="black", width=1)
    draw.text((620, y + 18), "TOTAL DUE", fill="black", font=med)
    draw.text((760, y + 18), "$1,242.00", fill="black", font=med)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def main() -> int:
    header(f"ocr — {MODEL} (pass-through)")

    try:
        png_bytes = build_sample_image()
    except ImportError as e:
        fail(MODEL, f"Pillow not installed: {e}")
        return 1

    SAMPLE_PNG.write_bytes(png_bytes)
    print(f"  wrote {SAMPLE_PNG.name} ({len(png_bytes)} bytes)")

    data_url = "data:image/png;base64," + base64.b64encode(png_bytes).decode()
    payload = {
        "model": MODEL,
        "document": {"type": "image_url", "image_url": data_url},
    }

    with make_httpx_client(timeout=120) as client:
        try:
            r = client.post(PATH, json=payload)
            if r.status_code >= 400:
                fail(MODEL, f"HTTP {r.status_code}: {r.text[:200]}")
                return 1
            body = r.json()
            pages = body.get("pages", [])
            md = pages[0].get("markdown", "") if pages else ""
            print("  --- recognised text (first 400 chars) ---")
            print("  " + md[:400].replace("\n", "\n  "))
            print("  --- end ---")

            missing = [p for p in EXPECTED_PHRASES if p not in md]
            if missing:
                fail(MODEL, f"missing expected phrases: {missing}")
                return 1
            ok(MODEL, f"pages={len(pages)} chars={len(md)} all expected phrases found")
            return 0
        except Exception as e:  # noqa: BLE001
            fail(MODEL, str(e))
            return 1


if __name__ == "__main__":
    sys.exit(main())
