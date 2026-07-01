"""Embeddings sample — `client.embeddings.create(...)`.

WHY THIS EXISTS
    Embeddings turn text into a fixed-length vector of floats so you can
    measure semantic similarity (cosine distance) between pieces of text.
    They are the foundation of every RAG / search / clustering / dedup
    workflow — store the vectors in a vector DB (Azure AI Search, pgvector,
    Pinecone, ...), then at query time embed the user question and find
    the nearest stored vectors.

WHAT THIS SAMPLE SHOWS
    - The OpenAI SDK call is identical regardless of which embedding model
      is targeted; only the dimensionality of the returned vector changes:
        text-embedding-3-large  -> 3072 floats
        text-embedding-ada-002  -> 1536 floats
    - One call can embed a batch by passing a list to `input=[...]`.
    - `resp.data[i].embedding` is a plain Python list of floats.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import make_openai_client, ok, fail, header  # noqa: E402

MODELS = ["text-embedding-3-large", "text-embedding-ada-002"]


def main() -> int:
    client = make_openai_client(timeout=60)
    header(f"embeddings — {len(MODELS)} models")
    failures = 0
    for m in MODELS:
        try:
            resp = client.embeddings.create(model=m, input="hello world")
            dim = len(resp.data[0].embedding)
            ok(m, f"dim={dim}")
        except Exception as e:  # noqa: BLE001
            fail(m, str(e))
            failures += 1
    print(f"\n{len(MODELS) - failures}/{len(MODELS)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
