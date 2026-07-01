---
name: cfi-ai
description: 'How to call the AI models available at CFI Lab from Python. Catalog includes chat (GPT-4o, GPT-4.1, gpt-5 family), reasoning (o1, o3, o3-mini, grok-4-20-reasoning), Anthropic (Claude Opus 4-x, Claude Haiku 4-5), open / third-party (Kimi, Phi, DeepSeek V4), Responses-only deployments (gpt-5-mini, gpt-5-pro, gpt-5.1, gpt-5.1-codex, gpt-5.1-codex-max), embeddings (text-embedding-3-large, ada-002), RAG via vector stores, image generation (gpt-image-2, MAI-Image-2, FLUX.2-pro), Mistral Document AI OCR, TTS (gpt-4o-mini-tts + 400+ Azure neural voices with SSML), speech-to-text (gpt-4o-transcribe family with diarization), and realtime audio (standard / translate / whisper). Use whenever the user wants to pick a CFI Lab model, build or extend a Python script against it, debug an auth or 404 routing error, configure RAG, send SSML, or open a realtime WebSocket. Browse the live model catalog and usage stats at https://litellm.cfilab.philips.com/ui; OpenAPI / Swagger at /docs.'
---

# CFI Lab AI — Python

This skill teaches you how to call the AI models available at CFI Lab from Python. It bundles a complete, working sample for every capability in [`scripts/`](./scripts/) so you can run them as-is, copy a snippet, or extend the suite. Every snippet inlined below comes from a script that has been verified end-to-end against the live models.

The CFI Lab catalog is delivered through a single Python entry point: an `OpenAI` SDK client pointed at `https://litellm.cfilab.philips.com/v1` with your virtual key. You don't pick an Azure region or an api-version — just pick a *model name* and call the matching SDK method.

To browse the live catalog (model names, per-key spend, rate limits):

- **Web UI** — <https://litellm.cfilab.philips.com/ui>
- **OpenAPI / Swagger** — <https://litellm.cfilab.philips.com/docs>

## When to use this skill

Use this skill whenever the task involves calling a CFI Lab AI model from Python, **or** debugging why such a call fails. Concretely:

- Adding a new Python script that calls a CFI Lab model.
- Picking the right model and capability (chat vs Responses, gpt-image vs MAI/FLUX, OpenAI TTS vs Azure Speech) for a given task.
- Diagnosing a `401`, `404`, `429`, or routing error against `litellm.cfilab.philips.com`.
- Wiring up RAG against a registered vector store (`eval-rag`, …).
- Sending JSON-based SSML for high-quality multilingual TTS.
- Building or extending the bundled sample suite under [`scripts/`](./scripts/).

## What's in the catalog

| Capability | Models / deployments | Sample |
|---|---|---|
| **Chat** — general | `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, `gpt-5`, `gpt-5-nano`, `gpt-5.2`, `gpt-5.4`, `gpt-5.5` | [`scripts/chat_completions/run.py`](./scripts/chat_completions/run.py) |
| **Chat** — reasoning (hidden thinking tokens) | `o1`, `o3`, `o3-mini`, `grok-4-20-reasoning` | same file |
| **Chat** — Anthropic | `claude-haiku-4-5`, `claude-opus-4-5`, `claude-opus-4-6`, `claude-opus-4-8` | same file |
| **Chat** — open-source / third-party | `Kimi-K2.5`, `Kimi-K2.6`, `Phi-4-multimodal-instruct`, `grok-4-20-non-reasoning`, `DeepSeek-V4-Flash`, `DeepSeek-V4-Pro` | same file |
| **Responses** (Responses-only deployments — 404 on chat) | `gpt-5-mini`, `gpt-5-pro`, `gpt-5.1`, `gpt-5.1-codex`, `gpt-5.1-codex-max` | [`scripts/responses/run.py`](./scripts/responses/run.py) |
| **Embeddings** | `text-embedding-3-large` (3072 dim), `text-embedding-ada-002` (1536 dim) | [`scripts/embeddings/run.py`](./scripts/embeddings/run.py) |
| **RAG** (grounding against a registered vector store) | any chat model + `tools=[file_search]` | [`scripts/rag/run.py`](./scripts/rag/run.py) |
| **Image generation** | `gpt-image-2` (OpenAI SDK), `MAI-Image-2`, `FLUX.2-pro` | [`scripts/image_generation/run.py`](./scripts/image_generation/run.py) |
| **OCR** (document → markdown) | `mistral-document-ai-2505` | [`scripts/ocr/run.py`](./scripts/ocr/run.py) |
| **Text-to-speech** | `gpt-4o-mini-tts` (11 voices), Azure neural voices via SSML (400+ voices, 140+ locales) | [`scripts/tts/run_openai.py`](./scripts/tts/run_openai.py), [`scripts/tts/run_speech.py`](./scripts/tts/run_speech.py) |
| **Speech-to-text** | `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `gpt-4o-transcribe-diarize` | [`scripts/transcriptions/run.py`](./scripts/transcriptions/run.py) |
| **Realtime audio** (WebSocket) | `gpt-realtime`, `gpt-realtime-translate`, `gpt-realtime-whisper` | [`scripts/realtime/run_standard.py`](./scripts/realtime/run_standard.py), [`run_translate.py`](./scripts/realtime/run_translate.py), [`run_whisper.py`](./scripts/realtime/run_whisper.py) |

For an authoritative, always-current list (including newly added deployments and any rate-limit / cost info that applies to your key), check the LiteLLM UI at <https://litellm.cfilab.philips.com/ui>.

## Ask the user when more than one model fits

The catalog has overlapping models for most capabilities. Before writing code for a task that has more than one reasonable answer, **pause and ask the user** with a concise options list and known trade-offs. Pick a sensible default and mark it as recommended, but let the user override.

When to ask (non-exhaustive):

| Task | Options to surface | Known trade-offs |
|---|---|---|
| Chat with reasoning | `gpt-5`, `o3`, `claude-opus-4-8`, `grok-4-20-reasoning`, `DeepSeek-V4-Pro` | Cost vs latency vs context window; reasoning models burn hidden thinking tokens — set `max_completion_tokens=1024+`. |
| Chat — low latency / cheap | `gpt-4o-mini`, `gpt-5-nano`, `claude-haiku-4-5`, `Kimi-K2.5`, `DeepSeek-V4-Flash` | All fast and cheap; some (Kimi / DeepSeek / Claude) can cold-start (60–120 s) when the upstream pool is idle. |
| Chat vs Responses | `client.chat.completions.create` vs `client.responses.create` | A handful of gpt-5.x deployments are **Responses-only** — they 404 on chat completions. Everything else does both. |
| Image generation | `gpt-image-2`, `MAI-Image-2`, `FLUX.2-pro` | `gpt-image-2` best for instruction following (slow: 60–200 s); MAI / FLUX have distinct aesthetic / licensing footprints; MAI requires width / height ≥ 768. |
| Speech-to-text | `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `gpt-4o-transcribe-diarize` | Mini = cheapest. Diarize returns `segments[]` with `speaker` labels via `response_format="diarized_json"`. |
| Text-to-speech | `gpt-4o-mini-tts` (11 expressive voices) vs Azure neural voices (400+, full SSML) | `gpt-4o-mini-tts` is more natural for open prompts; Azure Speech wins for multilingual / precise prosody / phoneme control. |
| Realtime | `gpt-realtime` (general conversation), `gpt-realtime-translate` (speech → speech in target language), `gpt-realtime-whisper` (speech → text) | Different protocols per deployment — see the realtime samples. |

How to present the choice (template):

> I can do this with any of:
> - **Option A** (recommended) — *one-line summary*. Pros: …. Cons: ….
> - **Option B** — *one-line summary*. Pros: …. Cons: ….
> - **Option C** — *one-line summary*. Pros: …. Cons: ….
>
> Defaulting to **A** unless you'd like a different one.

If the user's request already pins a model, skip the prompt and just build it. Only ask when the choice is genuinely open and the trade-offs would change the resulting code.

## Setup

The bundled samples need exactly three env vars — full template in [`scripts/.env.example`](./scripts/.env.example):

| Var | Required | Default | Notes |
|---|---|---|---|
| `PROXY_BASE_URL` | yes | `http://localhost:4000` | The CFI Lab endpoint is `https://litellm.cfilab.philips.com`. |
| `LITELLM_API_KEY` | yes | — | Your virtual key (starts with `sk-`). Request one from <CFI@philips.com> if you don't have one yet. Treat it like any other secret — never commit it. |
| `SSL_VERIFY` | no | `True` | Set to `False` on networks with TLS interception (Philips corporate proxy) so HTTPS/WSS calls don't fail certificate checks. |

Copy `.env.example` to `.env` and fill in your key before running anything; `.env` is gitignored.

## How to call any model

All non-realtime calls go through a single OpenAI client:

```python
from openai import OpenAI
import httpx
client = OpenAI(
    base_url="https://litellm.cfilab.philips.com/v1",
    api_key=LITELLM_API_KEY,                 # your virtual key, starts with "sk-"
    http_client=httpx.Client(verify=SSL_VERIFY),
)
```

The capability determines the SDK method:

| Capability | Call |
|---|---|
| Chat completions | `client.chat.completions.create(model="<name>", messages=[...])` |
| Responses | `client.responses.create(model="<name>", input="...")` |
| Embeddings | `client.embeddings.create(model="text-embedding-3-large", input=[...])` |
| Images (gpt-image-2) | `client.images.generate(model="gpt-image-2", prompt="...", size="1024x1024")` |
| Transcriptions | `client.audio.transcriptions.create(model="gpt-4o-transcribe", file=(name, bytes, mime), response_format="json")` |
| TTS (OpenAI-shape) | `client.audio.speech.create(model="gpt-4o-mini-tts", voice="alloy", input="...")` |
| RAG | `client.chat.completions.create(model="gpt-4o-mini", messages=[...], tools=[{"type":"file_search","vector_store_ids":["eval-rag"]}])` |

Three capabilities don't fit the OpenAI SDK shape — **OCR**, **MAI / FLUX image generation**, and **Azure neural voice SSML TTS**. They use plain `httpx.post` with `Authorization: Bearer <virtual-key>` and a CFI-specific path (`/foundry/mistral-ocr`, `/image/mai`, `/image/flux`, `/speech/tts`). Examples below.

## Use the bundled common helper, don't reinvent

[`scripts/common.py`](./scripts/common.py) builds the right clients with the right auth and corporate-TLS plumbing. Import from it instead of constructing `OpenAI` or `httpx.Client` manually:

```python
from common import (
    make_openai_client,        # OpenAI SDK pointed at the CFI Lab endpoint
    make_httpx_client,         # raw httpx for the non-OpenAI-shape endpoints (Bearer auth pre-injected)
    PROXY_BASE_URL, API_KEY,   # for WebSocket URLs and rare overrides
    SSL_VERIFY,                # plumb into your own httpx / websockets
    ok, fail, skip, header, first_text,
)
```

When adding a new sample under `scripts/<domain>/run.py`, follow the same import dance the existing samples use — including the `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` line — so `common` resolves the same way.

## Worked examples

### Chat completions

```python
client = make_openai_client(timeout=120)
resp = client.chat.completions.create(
    model="claude-opus-4-6",                       # or gpt-4o / o3 / grok-4-20-reasoning / DeepSeek-V4-Pro / ...
    messages=[{"role": "user", "content": prompt}],
    max_completion_tokens=1024,                    # leaves headroom for reasoning models
)
text = resp.choices[0].message.content
```

Use `max_completion_tokens` (not `max_tokens`) for forward-compatibility with reasoning models — `o3`, `o1`, and `grok-4-20-reasoning` consume hundreds of *hidden* reasoning tokens before the first visible character and the visible output gets truncated otherwise.

The same call works for every chat model in the catalog. Full sample with all 23 models: [`scripts/chat_completions/run.py`](./scripts/chat_completions/run.py).

### Responses (for the Responses-only deployments)

`gpt-5-mini`, `gpt-5-pro`, `gpt-5.1`, `gpt-5.1-codex`, and `gpt-5.1-codex-max` are **Responses-only** — they 404 on `chat.completions`. Use `client.responses.create(...)`:

```python
resp = client.responses.create(model="gpt-5.1-codex", input=prompt)
text = resp.output_text                            # SDK convenience
# or walk resp.output[i].content[j].text for older SDKs / structured outputs
```

The Responses API returns a structured `output` list of items (messages, tool calls, refusals, reasoning) instead of a single `choices[].message`. The SDK exposes `output_text` as a convenience that concatenates all text parts. See [`scripts/responses/run.py`](./scripts/responses/run.py) for the full extraction loop.

### Embeddings

```python
resp = client.embeddings.create(model="text-embedding-3-large", input=["hello", "world"])
vectors = [d.embedding for d in resp.data]         # list of float lists
```

Dimension is determined by the model (`text-embedding-3-large` → 3072, `text-embedding-ada-002` → 1536). Batch via `input=[...]`. Sample: [`scripts/embeddings/run.py`](./scripts/embeddings/run.py).

### RAG — file_search over a registered vector store

A normal chat completion plus one extra parameter — the `file_search` tool pointing at a vector store ID:

```python
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Answer using the file_search results when relevant."},
        {"role": "user", "content": question},
    ],
    tools=[{"type": "file_search", "vector_store_ids": ["eval-rag"]}],
)
```

The embed → retrieve → ground loop runs server-side; the call returns a regular chat completion. You don't pick the embedding model or search index — those are wired into the vector store registration. Existing vector store IDs are listed in the LiteLLM UI; to register a new one, contact <CFI@philips.com>.

Sample with grounded-answer assertion: [`scripts/rag/run.py`](./scripts/rag/run.py).

### OCR — Mistral Document AI

This capability doesn't have an OpenAI-shaped surface, so it uses raw `httpx` against the CFI path `/foundry/mistral-ocr`:

```python
with make_httpx_client(timeout=180) as client:    # Bearer header pre-injected
    r = client.post("/foundry/mistral-ocr", json={
        "model": "mistral-document-ai-2505",
        "document": {"type": "image_url", "image_url": data_url},   # base64 data URL or https URL
    })
    pages = r.json()["pages"]                                       # [{"markdown": "...", ...}, ...]
```

The response is `{"pages": [{"markdown": "..."}, ...]}` — each page rendered as markdown (tables become markdown tables, etc.). Full sample with a self-generated invoice image: [`scripts/ocr/run.py`](./scripts/ocr/run.py).

### Image generation

Three models, two call shapes:

```python
# gpt-image-2 — OpenAI SDK
client = make_openai_client(timeout=300)
resp = client.images.generate(model="gpt-image-2", prompt=prompt, size="1024x1024", n=1)
png_bytes = base64.b64decode(resp.data[0].b64_json)

# MAI-Image-2 / FLUX.2-pro — raw httpx against /image/mai or /image/flux
with make_httpx_client(timeout=300) as client:
    r = client.post("/image/mai", json={
        "model": "MAI-Image-2",
        "prompt": prompt, "width": 1024, "height": 1024, "n": 1,
    })
    png_bytes = base64.b64decode(r.json()["data"][0]["b64_json"])
```

`gpt-image-2` is slow (60–200 s, sometimes >5 min) and can return `429 EngineOverloaded` on warm-up — retry with backoff. MAI-Image-2 requires width and height ≥ 768. Full sample: [`scripts/image_generation/run.py`](./scripts/image_generation/run.py).

### Text-to-speech — two engines

`gpt-4o-mini-tts` is the simplest path — 11 expressive voices, OpenAI SDK:

```python
resp = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",                                  # alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse
    input="Hello from CFI Lab.",
)
mp3_bytes = resp.read()
```

Azure neural voices via `/speech/tts` give you 400+ voices across 140+ locales plus full SSML control (prosody, breaks, phonemes, say-as) — the JSON body is converted to SSML server-side so the client never has to touch XML:

```python
with make_httpx_client(timeout=60) as client:
    # Plain text
    r = client.post("/speech/tts", json={"text": "Hello.", "voice": "en-US-JennyNeural"})
    # IPA pronunciation override
    r = client.post("/speech/tts", json={
        "text": "Hello, Azure!", "voice": "en-US-JennyNeural", "ipa": "hɛloʊ ˈæʒər",
    })
    # Full SSML via JsonML (array-based XML encoding — see the sample)
    r = client.post("/speech/tts", json={
        "ssml": ["prosody", {"rate": "slow"}, "Welcome. ",
                 ["break", {"time": "500ms"}],
                 "Today is ", ["say-as", {"interpret-as": "date", "format": "dmy"}, "11/05/2026"]],
        "voice": "en-US-JennyNeural",
    })
    mp3_bytes = r.content
```

Voice list: <https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts>. Samples: [`scripts/tts/run_openai.py`](./scripts/tts/run_openai.py), [`scripts/tts/run_speech.py`](./scripts/tts/run_speech.py).

### Speech-to-text

The `gpt-4o-transcribe` family is the OpenAI SDK call you'd expect:

```python
result = client.audio.transcriptions.create(
    model="gpt-4o-transcribe",                          # or gpt-4o-mini-transcribe / gpt-4o-transcribe-diarize
    file=("clip.mp3", audio_bytes, "audio/mpeg"),
    response_format="json",                              # use "diarized_json" with the -diarize deployment
)
text = result.text                                       # plus result.segments[].speaker on diarize
```

Sample (including auto-generation of a test clip via `gpt-4o-mini-tts`): [`scripts/transcriptions/run.py`](./scripts/transcriptions/run.py).

### Realtime audio (WebSocket)

`gpt-realtime` (general conversation), `gpt-realtime-translate` (speech → translated speech), and `gpt-realtime-whisper` (speech → transcript) all use the `websockets` library with `Authorization: Bearer <virtual-key>` on the upgrade:

```python
ws_base = PROXY_BASE_URL.replace("http", "ws", 1)
url = f"{ws_base}/v1/realtime?model=gpt-realtime"
async with websockets.connect(
    url,
    additional_headers={"Authorization": f"Bearer {API_KEY}"},
    ssl=_ssl_for(url),                                  # see SSL section below
) as ws:
    first_event = json.loads(await ws.recv())           # session.created
    # ... send/receive frames ...
```

Translate and whisper use slightly different protocols (`session.update` to set target language, or `transcription_session.*` for whisper) and connect via a dedicated WebSocket endpoint at `SIDECAR_BASE_URL` (default `ws://localhost:8000`). Samples: [`scripts/realtime/run_standard.py`](./scripts/realtime/run_standard.py), [`run_translate.py`](./scripts/realtime/run_translate.py), [`run_whisper.py`](./scripts/realtime/run_whisper.py).

## Corporate TLS (`SSL_VERIFY=False`)

If `.env` sets `SSL_VERIFY=False` (corporate TLS-interception proxy), every outbound client must respect it. `common.py` exports the parsed boolean — plumb it through:

- **OpenAI SDK**: must be constructed with `http_client=httpx.Client(verify=SSL_VERIFY, timeout=...)` — `make_openai_client` already does this.
- **httpx clients**: `httpx.Client(verify=SSL_VERIFY, ...)` — `make_httpx_client` already does this.
- **`websockets.connect`**: pass `ssl=_SSL_CTX` where:
  ```python
  import ssl as _ssl
  _SSL_CTX = None
  if not SSL_VERIFY:
      _SSL_CTX = _ssl.create_default_context()
      _SSL_CTX.check_hostname = False
      _SSL_CTX.verify_mode = _ssl.CERT_NONE
  # And only attach it to wss:// URLs (ws:// must get ssl=None):
  def _ssl_for(url): return _SSL_CTX if url.startswith("wss://") else None
  ```

Forgetting any one of these on a corporate network produces an opaque `SSL: CERTIFICATE_VERIFY_FAILED` from a layer that's hard to see — always plumb all three when adding a new sample.

## Running the bundled suite

```pwsh
cd skills/cfi/cfi-ai/scripts
.\start.bat
```

`start.bat` creates `.venv`, installs `requirements.txt`, copies `.env.example` to `.env` if missing, and runs every non-interactive sample with a per-script timeout, writing a summary to `test-results.log`.

To run one sample by itself:

```pwsh
.\.venv\Scripts\activate.bat
python chat_completions\run.py
python responses\run.py
python image_generation\run.py MAI-Image-2          # specific model
python tts\run_openai.py --voice coral              # specific voice
python realtime\run_translate.py --language fr      # interactive
```

[`scripts/run_all.py`](./scripts/run_all.py) runs every non-interactive sample as a separate subprocess so a hang in one doesn't poison the others. The realtime samples are interactive (they hold a WebSocket open) and are excluded — run them individually from `scripts/realtime/`.

## When you add a new sample

1. Create `scripts/<domain>/run.py`.
2. Insert the parent on `sys.path` and `from common import ...` — never re-import `dotenv` or rebuild the client config locally.
3. Pick the correct helper: `make_openai_client()` for any OpenAI-SDK capability, `make_httpx_client()` for the non-OpenAI-shape endpoints (`/foundry/mistral-ocr`, `/image/mai`, `/image/flux`, `/speech/tts`), or a raw `httpx.Client(verify=SSL_VERIFY, ...)` if you genuinely need to call something off-platform.
4. Use `ok(model, snippet)` / `fail(model, err)` / `skip(model, reason)` / `header(title)` for output so it lines up with the rest of the suite.
5. Make `main()` return `0` on success and a non-zero count on failure, and add the script to [`scripts/run_all.py`](./scripts/run_all.py) (with a sensible per-script timeout) if it's non-interactive.

## Common failures and what they usually mean

| Symptom | Likely cause |
|---|---|
| `ERROR: LITELLM_API_KEY is not set` | `.env` next to `common.py` doesn't define it. Copy `.env.example` to `.env` and paste your virtual key (starts with `sk-`). Don't have a key yet? Request one from <CFI@philips.com>. |
| `401 Unauthorized` | Virtual key is wrong, revoked, or has no permission for that model. Check the LiteLLM UI for your key's allowed models, or request a fresh key / scope change from <CFI@philips.com>. |
| `404 Not Found` on `chat.completions` for a gpt-5.x model | That deployment is Responses-only — call `client.responses.create(...)` instead. |
| `404` on an unknown model name | Check the model spelling against the LiteLLM UI catalog at <https://litellm.cfilab.philips.com/ui>. |
| `Read timed out` on Grok / Kimi / Phi / DeepSeek / `gpt-image-2` | Upstream cold start. Bump the per-call timeout (`make_openai_client(timeout=300)` or `make_httpx_client(timeout=300)`). |
| `429 EngineOverloaded` on image generation | Upstream throttling. Retry with exponential backoff. |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Corporate TLS interception. Set `SSL_VERIFY=False` in `.env` and make sure the `verify=` / `http_client=` / `ssl=` plumbing is in place for *this* client. |
| Image call returns `200` but no bytes | Some configurations return `url` instead of `b64_json`. Handle both — see the bundled image sample. |
| MAI-Image-2 returns 400 on small dimensions | Width and height must each be ≥ 768 pixels. |
| RAG answer doesn't reference the index | The `file_search` tool reached the model but retrieval returned nothing useful. Check the vector store ID is correct in the LiteLLM UI. |

## What this skill does **not** cover

- Operating the CFI Lab platform itself (model routing config, vector store registration, sidecar deployment) — contact <CFI@philips.com>.
- Streaming responses — every snippet here is single-shot. The same `OpenAI` client supports `stream=True` for Chat and a typed event stream for Responses; consult the OpenAI Python SDK docs for the per-surface streaming shape.
