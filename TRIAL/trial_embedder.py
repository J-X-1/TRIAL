"""
TRIAL - Texas Regulatory Insurance Analysis Layer
Phase 2, Step 2: Embed and Store

Reads parsed chunks from chunks.json, generates embeddings via OpenAI's
text-embedding-3-small model, and stores everything (vectors + metadata + text)
in a persistent local ChromaDB collection.

Prerequisites:
    pip install openai chromadb python-dotenv

    Create a .env file in the project root with:
        OPENAI_API_KEY=sk-...

Usage:
    python trial_embedder.py
    python trial_embedder.py --input chunks.json --db-dir trial_chroma_db
"""

import os
import json
import time
import argparse
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
import chromadb

# --- Configuration ---

EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "texas_insurance_code"
BATCH_SIZE = 50  # OpenAI embedding API accepts up to 2048 inputs, but smaller batches are safer


def load_chunks(input_path: str) -> list[dict]:
    """Load parsed chunks from JSON."""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["chunks"]


def embed_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Send a batch of texts to OpenAI and return embedding vectors."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def build_collection(chunks: list[dict], db_dir: str, client: OpenAI) -> None:
    """Embed all chunks and store in ChromaDB."""
    db = chromadb.PersistentClient(path=db_dir)

    # Delete existing collection if re-running (idempotent rebuild)
    try:
        db.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = db.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Texas Insurance Code Title 7 — Life Insurance and Annuities"},
    )

    total = len(chunks)
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"Embedding {total} chunks in {total_batches} batches of up to {BATCH_SIZE}...")

    for batch_num in range(total_batches):
        start = batch_num * BATCH_SIZE
        end = min(start + BATCH_SIZE, total)
        batch = chunks[start:end]

        texts = [c["text"] for c in batch]
        ids = [c["chunk_id"] for c in batch]

        # Metadata for filtered retrieval — ChromaDB requires flat key-value pairs
        metadatas = []
        for c in batch:
            metadatas.append({
                "section_id": c["section_id"],
                "section_title": c["section_title"],
                "chapter_number": c["chapter_number"],
                "chapter_title": c["chapter_title"],
                "subtitle_label": c["subtitle_label"] or "",
                "subtitle": c["subtitle"] or "",
                "subchapter_label": c["subchapter_label"] or "",
                "subchapter_title": c["subchapter_title"] or "",
            })

        # Get embeddings from OpenAI
        embeddings = embed_batch(client, texts)

        # Store in ChromaDB
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        print(f"  Batch {batch_num + 1}/{total_batches}: embedded and stored {len(batch)} chunks")

    print(f"\nCollection '{COLLECTION_NAME}' now has {collection.count()} documents.")


def main():
    parser = argparse.ArgumentParser(description="TRIAL embedder — embed and store statute chunks")
    parser.add_argument("--input", default="chunks.json",
                        help="Path to parsed chunks JSON (default: chunks.json)")
    parser.add_argument("--db-dir", default="trial_chroma_db",
                        help="ChromaDB persistent storage directory (default: trial_chroma_db)")
    args = parser.parse_args()

    # Load API key from .env
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found. Add it to your .env file.")
        return

    print("TRIAL Embedder — Phase 2, Step 2")
    print(f"Input:     {args.input}")
    print(f"Model:     {EMBEDDING_MODEL}")
    print(f"DB dir:    {args.db_dir}")
    print("-" * 50)

    chunks = load_chunks(args.input)
    print(f"Loaded {len(chunks)} chunks")

    client = OpenAI(api_key=api_key)
    build_collection(chunks, args.db_dir, client)

    print("-" * 50)
    print("Done. ChromaDB is ready for retrieval.")


if __name__ == "__main__":
    main()
