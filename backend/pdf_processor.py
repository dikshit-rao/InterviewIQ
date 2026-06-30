import re

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def clean_text(text):
    """Fix the broken-word extraction (e.g. 'or\nder_id' -> 'order_id')."""
    # join words split across a single newline
    text = re.sub(r"(\w)\n(\w)", r"\1\2", text)
    # collapse remaining newlines / repeated whitespace into single spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def process_pdf(pdf_path, source_name):
    """Return a list of chunk dicts: {"text", "source", "page"}.

    We chunk page-by-page so every chunk remembers its page number, which
    is what makes 'Source: file.pdf, page 17' citations possible.
    """
    reader = PdfReader(pdf_path)
    chunks = []

    for page_num, page in enumerate(reader.pages, start=1):
        extracted = page.extract_text()
        if not extracted or not extracted.strip():
            continue
        extracted = clean_text(extracted)
        for piece in splitter.split_text(extracted):
            chunks.append({
                "text": piece,
                "source": source_name,
                "page": page_num,
            })

    return chunks