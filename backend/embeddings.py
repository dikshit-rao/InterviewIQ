import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL

# Load the model ONCE at import time. Loading is computationally expensive,
# so doing it here (instead of inside the function) avoids re-initialising
# on every request and keeps API responses fast.
embedding_model = SentenceTransformer(EMBEDDING_MODEL)


def generate_embeddings(texts):
    """texts: list[str] -> float32 numpy array (FAISS requires float32)."""
    embeddings = embedding_model.encode(texts, convert_to_numpy=True)
    return embeddings.astype("float32")