"""Lightweight local vector database management."""

import os
import chromadb
from chromadb.utils import embedding_functions
from corecoder.config import Config


def get_collection():
    """Get or create the ChromaDB collection (pure local mode)."""
    # Create the vector database in the user's home directory
    db_path = os.path.expanduser("~/.corecoder_chroma_db")
    chroma_client = chromadb.PersistentClient(path=db_path)

    # Custom embedding is no longer passed.
    # ChromaDB will automatically download the default sentence transformer model (all-MiniLM-L6-v2)
    # in the background during the first run (tens of MBs).
    # Afterward, it runs completely offline without relying on any external APIs.
    return chroma_client.get_or_create_collection(
        name="corecoder_knowledge"
    )


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def ingest_document(file_path: str) -> str:
    """Read a file, ingest it into the database, and return the execution result."""
    if not os.path.exists(file_path):
        return f"Error: File not found '{file_path}'"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        return f"Error: Cannot read file: {e}"

    filename = os.path.basename(file_path)
    chunks = chunk_text(text)

    ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename} for _ in range(len(chunks))]

    collection = get_collection()
    collection.upsert(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    return f"Success: Sliced {filename} into {len(chunks)} chunks and ingested into the knowledge base."