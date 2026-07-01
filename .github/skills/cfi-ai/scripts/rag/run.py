"""RAG sample — chat completion grounded in the `eval-rag` vector store.

WHY THIS EXISTS
    Retrieval-Augmented Generation (RAG) lets an LLM answer questions
    using *your* documents instead of relying solely on what it learned
    during training. The pattern is:

        1. Off-line: embed each document chunk and store the vectors in
           a vector index (here, an Azure AI Search index).
        2. On-line: at query time, the proxy automatically:
             a. embeds the user question,
             b. retrieves the top-k matching chunks from the index,
             c. injects them as system context for the model,
             d. asks the model to answer using those chunks.

    From the caller's point of view, RAG is just a normal Chat Completions
    call with one extra parameter — the `file_search` tool pointing at a
    vector store id. LiteLLM handles steps 2a-2c on the proxy side using
    the registered Azure AI Search backend.

WHAT THIS SAMPLE PROVES
    The question below references a document we indexed earlier
    ("Project Iguana"). The model has never seen that document during
    training, so a correct answer (containing the codename "BLUE-OWL-42")
    is only possible if retrieval is actually wired up. The script
    asserts that string is present in the answer and fails otherwise.

SET UP YOUR OWN INDEX
    See `experiment/litellm/docs/rag-azure-ai-search.md` for the steps
    to register a new vector store via `POST /vector_store/new`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import make_openai_client, ok, fail, header, first_text  # noqa: E402

MODEL = "gpt-4o-mini"
VECTOR_STORE_ID = "eval-rag"


def main() -> int:
    client = make_openai_client(timeout=60)
    header(f"rag — {MODEL} + vector_store={VECTOR_STORE_ID}")
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Answer using the file_search results when relevant."},
                {"role": "user", "content": "What is the secret codename of Project Iguana, who leads it, and what is the budget?"},
            ],
            tools=[{"type": "file_search", "vector_store_ids": [VECTOR_STORE_ID]}],
        )
        answer = first_text(resp.choices[0].message.content)
        # Sanity-check that retrieval actually grounded the answer.
        grounded = "BLUE-OWL-42" in answer.upper().replace(" ", "")
        if grounded:
            ok(MODEL, answer)
            return 0
        else:
            fail(MODEL, f"answer not grounded in index: {answer}")
            return 1
    except Exception as e:  # noqa: BLE001
        fail(MODEL, str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
