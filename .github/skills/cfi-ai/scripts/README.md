# Python samples for the CFI Lab LiteLLM proxy

Minimal CLI samples — one per OpenAI-style interface — that talk to the
LiteLLM proxy at `https://litellm.cfilab.philips.com` and exercise the
Azure AI Foundry deployments wired up in the proxy config.

For the *why* — how to pick a model, when to use Chat vs Responses, how
the pass-through endpoints work, and how the proxy compares to going
direct to Azure — see the parent [`SKILL.md`](../SKILL.md).

## Layout

```
skills/cfi/cfi-ai/scripts/
├── .venv/                       # shared virtual environment
├── requirements.txt             # openai, httpx, python-dotenv, websockets, Pillow
├── .env                         # PROXY_BASE_URL, LITELLM_API_KEY (gitignored)
├── .env.example                 # template
├── common.py                    # shared client setup + pretty-printers
├── run_all.py                   # spawns each sample as a subprocess (per-script timeout)
├── start.bat                    # one-shot: build .venv + install deps + run_all.py
│
├── embeddings/run.py            # text-embedding-3-large, text-embedding-ada-002
├── chat_completions/run.py      # 23 models: gpt-4*, o*, gpt-5*, claude-*, grok, kimi, phi, deepseek
├── responses/run.py             # gpt-5-mini, gpt-5-pro, gpt-5.1-codex(-max)
├── rag/run.py                   # gpt-4o-mini grounded in the eval-rag vector store
├── ocr/run.py                   # mistral-document-ai-2505 (pass-through, generates test image)
│
├── transcriptions/run.py        # gpt-4o-transcribe family (generates test clip)
│
├── tts/                         # two TTS engines
│   ├── run.py                   # runner — calls both scripts below
│   ├── run_speech.py            # Azure Cognitive Services Speech (400+ voices, IPA, SSML)
│   └── run_openai.py            # gpt-4o-mini-tts (OpenAI SDK)
│
├── image_generation/run.py      # gpt-image-2, MAI-Image-2, FLUX.2-pro
│
└── realtime/                    # interactive — NOT in run_all.py
    ├── run.py                   # runner — calls all three scripts below
    ├── run_standard.py          # gpt-realtime (standard OpenAI realtime via proxy)
    ├── run_translate.py         # gpt-realtime-translate (via sidecar)
    └── run_whisper.py           # gpt-realtime-whisper transcription (via sidecar)
```

## Quick start

```pwsh
# from skills/cfi/cfi-ai/scripts/
.\start.bat
```

That creates `.venv`, installs deps, copies `.env.example` to `.env` if
missing, then runs every non-interactive sample with a per-script timeout
and writes a summary to `test-results.log`.

Then edit `.env` and paste your LiteLLM virtual key (`sk-…`). The proxy
URL defaults to the deployed CFI Lab proxy; only change `PROXY_BASE_URL`
if you're running a proxy on your own machine.

## Running one sample by itself

```pwsh
.\.venv\Scripts\activate.bat
python chat_completions\run.py
python responses\run.py
python rag\run.py
python image_generation\run.py MAI-Image-2    # specific model
python tts\run_openai.py --voice coral         # specific TTS engine + voice
python realtime\run_translate.py --language fr  # interactive
```

## What `run_all.py` covers

| Sample | Timeout | What it tests |
|--------|---------|---------------|
| `embeddings` | 60s | 2 embedding models |
| `chat_completions` | 600s | 23 chat models (GPT, o-series, Claude, Grok, Kimi, Phi, DeepSeek) |
| `responses` | 600s | 5 Responses-only models |
| `rag` | 120s | RAG grounding via Azure AI Search |
| `ocr` | 180s | Mistral OCR pass-through |
| `tts` | 60s | Both TTS engines (Azure Speech + gpt-4o-mini-tts) |
| `transcriptions` | 120s | gpt-4o-transcribe family (speech-to-text + diarization) |
| `image_generation` | 600s | All 3 image models (gpt-image-2, MAI-Image-2, FLUX.2-pro) |

The `realtime/` samples are interactive (WebSocket + audio) and excluded
from `run_all.py`.

## Why the `openai` SDK and not `openai-agents-python`?

`openai-agents-python` is an agent-orchestration framework — useful when
you want tools, handoffs, and traces, but overkill for "ping each model"
smoke tests. The plain `openai` SDK speaks every OpenAI-compatible surface
(Chat Completions, Responses, Embeddings, Images, Audio, Realtime) against
any base URL, so a single dependency covers most samples. `httpx` is used
for the pass-through endpoints (OCR, image, TTS).
