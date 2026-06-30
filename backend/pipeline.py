import os

from pdf_processor import process_pdf
from embeddings import generate_embeddings
from vector_store import add_to_store


def build_vector_database(pdf_path):
    source_name = os.path.splitext(os.path.basename(pdf_path))[0]

    chunks = process_pdf(pdf_path, source_name)
    if not chunks:
        raise ValueError("No text could be extracted from the PDF.")

    texts = [c["text"] for c in chunks]
    embeddings = generate_embeddings(texts)

    added = add_to_store(chunks, embeddings)
    return added