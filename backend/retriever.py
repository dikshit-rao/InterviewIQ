import faiss

from embeddings import generate_embeddings
from vector_store import load_store


def retrieve_chunks(question, documents=None, k=5):
    """Retrieve top-k chunk dicts, optionally restricted to selected documents.

    documents: list of source names the user ticked in the Chat UI.
               Empty / None = search across everything.

    We over-fetch then filter by source, so selecting a single subject still
    returns enough relevant chunks instead of coming back nearly empty.
    """
    index, chunks = load_store()

    q = generate_embeddings([question])
    faiss.normalize_L2(q)

    search_k = k * 6 if documents else k
    search_k = min(search_k, len(chunks))

    scores, indices = index.search(q, search_k)

    results = []
    for idx in indices[0]:
        if idx == -1:
            continue
        chunk = chunks[idx]
        if documents and chunk["source"] not in documents:
            continue
        results.append(chunk)
        if len(results) >= k:
            break

    return results