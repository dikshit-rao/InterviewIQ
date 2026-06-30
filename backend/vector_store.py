import os
import pickle

import faiss
import numpy as np

from config import INDEX_PATH, CHUNKS_PATH


def _load_existing():
    """Return (index, chunks) if a global store exists, else (None, [])."""
    if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(CHUNKS_PATH, "rb") as f:
            chunks = pickle.load(f)
        return index, chunks
    return None, []


def add_to_store(chunk_dicts, embeddings):
    """Append new chunks + embeddings to the single global FAISS index.

    We normalize the vectors and use IndexFlatIP so the similarity is COSINE,
    not raw L2. MiniLM is trained for cosine — this measurably improves
    which chunks get retrieved.
    """
    embeddings = np.array(embeddings).astype("float32")
    faiss.normalize_L2(embeddings)

    index, chunks = _load_existing()
    if index is None:
        index = faiss.IndexFlatIP(embeddings.shape[1])

    index.add(embeddings)
    chunks.extend(chunk_dicts)        # keep chunk dicts aligned with vectors

    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    return len(chunk_dicts)


def load_store():
    index, chunks = _load_existing()
    if index is None:
        raise ValueError("No documents indexed yet. Upload a PDF first.")
    return index, chunks