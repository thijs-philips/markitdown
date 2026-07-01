"""Responses API sample — `client.responses.create(...)`.

WHY THIS EXISTS
    Responses is OpenAI's newer surface (`POST /v1/responses`). Unlike
    Chat Completions it returns a structured `output` list of "items"
    (messages, tool calls, refusals, etc.) instead of a single
    `choices[].message`, and it natively understands multi-step
    tool-using sessions.

    Why we need it on Azure: several gpt-5.x deployments are
    **Responses-only** — their `/openai/deployments/<name>/chat/completions`
    URL returns 404. Routing them through `azure/<deployment>` and calling
    `client.responses.create(...)` lands on `/openai/responses` which is
    the URL they actually serve.

KEY API DIFFERENCES vs CHAT COMPLETIONS

    Chat Completions                       Responses
    ---------------------------------      ------------------------------
    messages=[{role, content}, ...]        input="..."  OR  input=[items]
    response.choices[0].message.content    response.output_text
                                           response.output[i].content[j].text
    max_completion_tokens=N                max_output_tokens=N
    tools=[{type:"function", ...}]         tools=[{type:"...", ...}]  (broader)
    streaming via deltas on choices[0]     streaming via typed events

    The OpenAI Python SDK exposes `output_text` as a convenience that
    concatenates all text parts; the loop in `_extract_text` below also
    walks `output[].content[]` for older SDKs / partial responses.

WHEN TO USE WHICH
    - Compatibility / wide model support / simple Q&A   -> Chat Completions
    - Built-in tool calling, structured outputs,
      reasoning models with explicit reasoning items,
      Azure deployments that ONLY ship Responses        -> Responses

    On this proxy `gpt-5-mini`, `gpt-5.1`, `gpt-5-pro`, `gpt-5.1-codex`
    and `gpt-5.1-codex-max` are all routed for Responses; the rest of the
    gpt-5 family answers on Chat Completions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import make_openai_client, ok, fail, header  # noqa: E402

MODELS = [
    "gpt-5-mini",
    "gpt-5-pro",
    "gpt-5.1",
    "gpt-5.1-codex",
    "gpt-5.1-codex-max",
]

PROMPT = "Reply with exactly the two characters: OK"


def _extract_text(resp) -> str:
    # The Responses API returns an `output` list of items, each with content
    # parts that have a `text` field.
    text = getattr(resp, "output_text", None)
    if text:
        return text.strip()
    for item in getattr(resp, "output", []) or []:
        for part in getattr(item, "content", []) or []:
            t = getattr(part, "text", None)
            if t:
                return t.strip()
    return ""


def main() -> int:
    client = make_openai_client(timeout=180)
    header(f"responses — {len(MODELS)} models")
    failures = 0
    for m in MODELS:
        try:
            resp = client.responses.create(model=m, input=PROMPT)
            ok(m, _extract_text(resp))
        except Exception as e:  # noqa: BLE001
            fail(m, str(e))
            failures += 1
    print(f"\n{len(MODELS) - failures}/{len(MODELS)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
