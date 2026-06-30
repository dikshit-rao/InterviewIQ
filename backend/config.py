import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Anchor every path to THIS file's folder so the app works no matter
# which directory you launch uvicorn from. Relative paths like "uploads/"
# break the moment you run the server from somewhere else.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STORAGE_DIR = os.path.join(BASE_DIR, "storage")
UPLOAD_DIR = os.path.join(STORAGE_DIR, "uploads")
VECTOR_DIR = os.path.join(STORAGE_DIR, "vector_db")
DB_PATH = os.path.join(STORAGE_DIR, "interviewiq.db")

# One global FAISS index + one chunks file (not per-document folders)
INDEX_PATH = os.path.join(VECTOR_DIR, "global.index")
CHUNKS_PATH = os.path.join(VECTOR_DIR, "global_chunks.pkl")

# Make sure storage folders exist at startup
for path in (UPLOAD_DIR, VECTOR_DIR):
    os.makedirs(path, exist_ok=True)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-2.5-flash-lite"