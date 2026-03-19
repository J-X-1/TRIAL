"""
TRIAL - Texas Regulatory Insurance Analysis Layer
Phase 2, Step 3: Retrieval Module

Queries the ChromaDB vector store to find relevant statute sections.
Supports two retrieval modes:
  - Semantic search: embeds the query and finds nearest neighbors
  - Statute ID lookup: matches specific section references (e.g. "Sec. 1101.003")

Prerequisites:
    pip install openai chromadb python-dotenv

Usage:
    python trial_retriever.py "What is the grace period for life insurance?"
    python trial_retriever.py "Sec. 1101.003"
    python trial_retriever.py "incontestability" --top-k 3
"""

import os
import re
import json
import argparse

from dotenv import load_dotenv
from openai import OpenAI
import chromadb

# --- Configuration ---

EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "texas_insurance_code"
DEFAULT_TOP_K = 5

# Matches patterns like "1101.003", "Sec. 1101.003", "Section 1105.0015"
STATUTE_ID_PATTERN = re.compile(r"(?:Sec(?:tion)?\.?\s*)?(\d{4}\.\d{3,4}[A-Za-z]?)")


def get_collection(db_dir: str) -> chromadb.Collection:
    """Open the existing ChromaDB collection."""
    db = chromadb.PersistentClient(path=db_dir)
    return db.get_collection(name=COLLECTION_NAME)


def extract_statute_ids(query: str) -> list[str]:
    """Pull any statute section IDs from the query string."""
    return STATUTE_ID_PATTERN.findall(query)


def retrieve_by_id(collection: chromadb.Collection, section_ids: list[str]) -> list[dict]:
    """Look up specific sections by their section_id metadata."""
    results = []
    for sid in section_ids:
        matches = collection.get(
            where={"section_id": sid},
            include=["documents", "metadatas"],
        )
        for i, doc_id in enumerate(matches["ids"]):
            results.append({
                "chunk_id": doc_id,
                "score": 1.0,  # exact match
                "match_type": "statute_id",
                "text": matches["documents"][i],
                "metadata": matches["metadatas"][i],
            })
    return results


def retrieve_semantic(
    collection: chromadb.Collection,
    query: str,
    client: OpenAI,
    top_k: int = DEFAULT_TOP_K,
) -> list[dict]:
    """Embed the query and find nearest neighbors in ChromaDB."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    query_embedding = response.data[0].embedding

    matches = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    results = []
    for i in range(len(matches["ids"][0])):
        results.append({
            "chunk_id": matches["ids"][0][i],
            "score": 1 - matches["distances"][0][i],  # ChromaDB returns distance; invert for similarity
            "match_type": "semantic",
            "text": matches["documents"][0][i],
            "metadata": matches["metadatas"][0][i],
        })
    return results


def retrieve(
    query: str,
    db_dir: str = "trial_chroma_db",
    top_k: int = DEFAULT_TOP_K,
    api_key: str = None,
) -> list[dict]:
    """
    Main retrieval function. Checks for statute IDs first, falls back
    to semantic search. Returns a list of result dicts.
    """
    collection = get_collection(db_dir)

    # Check if query references specific statute sections
    statute_ids = extract_statute_ids(query)
    if statute_ids:
        id_results = retrieve_by_id(collection, statute_ids)
        if id_results:
            return id_results

    # Semantic search
    if not api_key:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    return retrieve_semantic(collection, query, client, top_k)


def format_result(result: dict, index: int) -> str:
    """Pretty-print a single retrieval result."""
    m = result["metadata"]
    lines = [
        f"--- Result {index + 1} [{result['match_type']}] (score: {result['score']:.3f}) ---",
        f"  Section:    Sec. {m['section_id']}  {m['section_title']}",
        f"  Chapter:    {m['chapter_number']} — {m['chapter_title']}",
    ]
    if m.get("subchapter_label"):
        lines.append(f"  Subchapter: {m['subchapter_label']}. {m['subchapter_title']}")
    lines.append(f"  Text:       {result['text'][:200]}...")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="TRIAL retriever — query the statute vector store")
    parser.add_argument("query", help="Natural language question or statute reference")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K,
                        help=f"Number of results to return (default: {DEFAULT_TOP_K})")
    parser.add_argument("--db-dir", default="trial_chroma_db",
                        help="ChromaDB directory (default: trial_chroma_db)")
    args = parser.parse_args()

    print(f"Query: {args.query}")
    print(f"Top-K: {args.top_k}")
    print("=" * 60)

    results = retrieve(args.query, db_dir=args.db_dir, top_k=args.top_k)

    if not results:
        print("No results found.")
        return

    for i, r in enumerate(results):
        print(format_result(r, i))
        print()


if __name__ == "__main__":
    main()
