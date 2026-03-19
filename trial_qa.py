"""
TRIAL - Texas Regulatory Insurance Analysis Layer
Phase 3: Question Answering with Citations

Takes a natural language question about Texas insurance law, retrieves
relevant statute sections from ChromaDB, and generates a grounded answer
with citations using OpenAI's GPT-5.4 model.

The answer generation pipeline:
  1. Retrieve top-k relevant chunks via trial_retriever.retrieve()
  2. Build a prompt with retrieved statute text as context
  3. Call GPT-5.4 to generate a cited answer
  4. Validate that all cited section IDs actually appear in the context

Prerequisites:
    pip install openai chromadb python-dotenv

Usage:
    python trial_qa.py "What is the grace period for life insurance in Texas?"
    python trial_qa.py "Can an insurer deny coverage based on opioid prescriptions?"
    python trial_qa.py "Sec. 1101.006" --top-k 3
"""

import os
import re
import json
import argparse

from dotenv import load_dotenv
from openai import OpenAI

from trial_retriever import retrieve

# --- Configuration ---

GENERATION_MODEL = "gpt-5.4"
DEFAULT_TOP_K = 5

SYSTEM_PROMPT = """You are a legal research assistant specializing in Texas insurance law. You answer questions using ONLY the statute excerpts provided below. Follow these rules strictly:

1. Base your answer exclusively on the provided statute context. Do not use outside knowledge.
2. Cite specific statute sections by their section number (e.g., "Sec. 1101.005") whenever you reference a provision.
3. If the provided context does not contain enough information to answer the question, say: "The provided statutes do not contain sufficient information to answer this question."
4. Be precise and direct. Summarize what the statute says without editorializing.
5. If multiple statutes are relevant, reference each one.
6. Do not invent or hallucinate section numbers."""

CONTEXT_TEMPLATE = """--- Statute Context ---

{chunks}

--- End of Context ---

Question: {question}"""

CHUNK_TEMPLATE = """[Sec. {section_id}] {section_title}
Chapter {chapter_number}: {chapter_title}
{text}
"""


def format_chunks_for_prompt(results: list[dict]) -> str:
    """Format retrieved chunks into a context block for the LLM prompt."""
    formatted = []
    for r in results:
        m = r["metadata"]
        formatted.append(CHUNK_TEMPLATE.format(
            section_id=m["section_id"],
            section_title=m["section_title"],
            chapter_number=m["chapter_number"],
            chapter_title=m["chapter_title"],
            text=r["text"],
        ))
    return "\n".join(formatted)


def extract_cited_sections(answer: str) -> list[str]:
    """
    Pull all section IDs cited in the LLM's answer.
    Matches patterns like "Sec. 1101.005", "Section 1101.005", or bare "1101.005".
    """
    pattern = re.compile(r"(?:Sec(?:tion)?\.?\s*)?(\d{4}\.\d{3,4}[A-Za-z]?)")
    return list(set(pattern.findall(answer)))


def validate_citations(answer: str, results: list[dict]) -> dict:
    """
    Check whether every section ID cited in the answer was actually
    present in the retrieved context. Returns a validation report.
    """
    cited = extract_cited_sections(answer)
    context_ids = {r["metadata"]["section_id"] for r in results}

    valid = [s for s in cited if s in context_ids]
    hallucinated = [s for s in cited if s not in context_ids]

    return {
        "cited_sections": cited,
        "valid_citations": valid,
        "hallucinated_citations": hallucinated,
        "all_valid": len(hallucinated) == 0,
    }


def generate_answer(
    question: str,
    db_dir: str = "trial_chroma_db",
    top_k: int = DEFAULT_TOP_K,
    api_key: str = None,
) -> dict:
    """
    Full QA pipeline: retrieve context, generate answer, validate citations.

    Returns a dict with:
        - question: the original question
        - answer: the LLM-generated response
        - citations: validation report
        - retrieval: list of retrieved chunk summaries
        - model: the model used for generation
    """
    # Step 1: Retrieve relevant statute chunks
    results = retrieve(question, db_dir=db_dir, top_k=top_k, api_key=api_key)

    if not results:
        return {
            "question": question,
            "answer": "No relevant statute sections were found for this query.",
            "citations": {"cited_sections": [], "valid_citations": [], "hallucinated_citations": [], "all_valid": True},
            "retrieval": [],
            "model": GENERATION_MODEL,
        }

    # Step 2: Build prompt with retrieved context
    context_block = format_chunks_for_prompt(results)
    user_message = CONTEXT_TEMPLATE.format(chunks=context_block, question=question)

    # Step 3: Call GPT-5.4 for answer generation
    if not api_key:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,  # Low temperature for factual, grounded responses
    )

    answer = response.choices[0].message.content

    # Step 4: Validate citations
    citation_report = validate_citations(answer, results)

    # Build retrieval summary for inspection
    retrieval_summary = []
    for r in results:
        retrieval_summary.append({
            "chunk_id": r["chunk_id"],
            "section_id": r["metadata"]["section_id"],
            "section_title": r["metadata"]["section_title"],
            "score": r["score"],
            "match_type": r["match_type"],
        })

    return {
        "question": question,
        "answer": answer,
        "citations": citation_report,
        "retrieval": retrieval_summary,
        "model": GENERATION_MODEL,
    }


def print_result(result: dict) -> None:
    """Pretty-print a QA result to the console."""
    print("=" * 60)
    print(f"Question: {result['question']}")
    print(f"Model:    {result['model']}")
    print("=" * 60)

    print(f"\n{result['answer']}\n")

    print("-" * 60)
    print("Retrieved Sections:")
    for r in result["retrieval"]:
        print(f"  Sec. {r['section_id']:12s} | {r['section_title'][:40]:40s} | "
              f"score={r['score']:.3f} ({r['match_type']})")

    print("-" * 60)
    c = result["citations"]
    print(f"Citation Validation:")
    print(f"  Cited:        {c['cited_sections']}")
    print(f"  Valid:        {c['valid_citations']}")
    print(f"  Hallucinated: {c['hallucinated_citations']}")
    status = "PASS" if c["all_valid"] else "FAIL — hallucinated citations detected"
    print(f"  Status:       {status}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="TRIAL QA — ask questions about Texas insurance law"
    )
    parser.add_argument("question", help="Natural language question or statute reference")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K,
                        help=f"Number of chunks to retrieve (default: {DEFAULT_TOP_K})")
    parser.add_argument("--db-dir", default="trial_chroma_db",
                        help="ChromaDB directory (default: trial_chroma_db)")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON instead of formatted text")
    args = parser.parse_args()

    result = generate_answer(args.question, db_dir=args.db_dir, top_k=args.top_k)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_result(result)


if __name__ == "__main__":
    main()
