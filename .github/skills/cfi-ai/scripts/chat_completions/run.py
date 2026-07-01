"""Chat-completions sample — `client.chat.completions.create(...)`.

WHY THIS EXISTS
    The Chat Completions API (`POST /v1/chat/completions`) is the original
    OpenAI surface and the lowest common denominator that almost every
    LLM provider speaks. LiteLLM exposes a single `/v1/chat/completions`
    on the proxy and routes each `model` name to the right backend
    (Azure OpenAI, Azure AI Inference, Anthropic-on-Foundry, ...).

    From the caller's perspective this is just the OpenAI SDK pointed at
    the proxy:
        client = OpenAI(base_url="http://localhost:4000/v1", api_key=...)
        client.chat.completions.create(model="<any-name-from-config>", ...)

WHEN TO USE CHAT VS RESPONSES
    Chat Completions  -> simple request/response, multi-turn via the full
                         `messages=[...]` history, tool calls, vision.
                         Supported by virtually every model.
    Responses API     -> newer, stateful-ish surface. Some Azure models
                         (gpt-5-pro, gpt-5.1-codex(-max), and the
                         Responses-only variants of gpt-5-mini / gpt-5.1)
                         are deployed only on /openai/responses. See the
                         neighbouring `responses/` sample.

REASONING MODELS
    o-series and grok-4-20-reasoning consume hundreds of *hidden* reasoning
    tokens before the first visible character. We bump
    `max_completion_tokens=1024` so the visible "OK" actually fits.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import make_openai_client, ok, fail, header, first_text  # noqa: E402

MODELS = [
    # Azure OpenAI chat
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4.1",
    # o-series (reasoning)
    "o1",
    "o3",
    "o3-mini",
    # gpt-5 family (these accept chat-completions; the Responses-only
    # variants live in the `responses/` sample)
    "gpt-5",
    "gpt-5-nano",
    "gpt-5.1",
    "gpt-5.2",
    "gpt-5.4",
    "gpt-5.5",
    # Anthropic on Foundry — LiteLLM translates OpenAI <-> Anthropic shapes
    "claude-haiku-4-5",
    "claude-opus-4-5",
    "claude-opus-4-6",
    "claude-opus-4-8",
    # Azure AI Inference (third-party models hosted by Foundry)
    "grok-4-20-reasoning",
    "grok-4-20-non-reasoning",
    "Kimi-K2.5",
    "Kimi-K2.6",
    "Phi-4-multimodal-instruct",
    # DeepSeek
    "DeepSeek-V4-Flash",
    "DeepSeek-V4-Pro",
]

PROMPT = "Reply with exactly the two characters: OK"


def main() -> int:
    client = make_openai_client(timeout=120)
    header(f"chat_completions — {len(MODELS)} models")
    failures = 0
    for m in MODELS:
        try:
            resp = client.chat.completions.create(
                model=m,
                messages=[{"role": "user", "content": PROMPT}],
                # Reasoning models (o*, grok-4-20-reasoning) consume hundreds
                # of hidden reasoning tokens before any visible output.
                max_completion_tokens=1024,
            )
            ok(m, first_text(resp.choices[0].message.content))
        except Exception as e:  # noqa: BLE001 — sample script
            fail(m, str(e))
            failures += 1
    print(f"\n{len(MODELS) - failures}/{len(MODELS)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
