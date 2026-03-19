"""
TRIAL - Texas Regulatory Insurance Analysis Layer
Phase 2, Step 1: Statute Text Parser and Chunker

Reads .txt files from raw_html/, parses each into section-level chunks
with hierarchical metadata (chapter, subtitle, subchapter, section ID,
section title), and outputs structured data ready for embedding.

Input:  raw_html/IN_XXXX.txt  (23 files from Phase 1 scraper)
Output: JSON file with all chunks + metadata, plus summary stats

Usage:
    python trial_parser.py
    python trial_parser.py --input-dir raw_html --output chunks.json
"""

import os
import re
import json
import argparse
from pathlib import Path


# --- Text Cleanup ---

def clean_raw_text(text: str) -> str:
    """Strip scraping artifacts and normalize whitespace."""
    # Normalize line endings (CRLF -> LF)
    text = text.replace("\r\n", "\n")

    # Remove the "Courier New (Serif)" artifact on line 2
    text = re.sub(r"^INSURANCE CODE CHAPTER \d+\n.*Courier New.*\n[\s\n]*", "", text)

    # Collapse runs of 3+ blank lines down to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# --- Header Parsing ---

def parse_header(text: str) -> dict:
    """
    Extract chapter-level metadata from the file header block.
    Returns dict with chapter_number, chapter_title, subtitle, title.
    """
    meta = {
        "title": "LIFE INSURANCE AND ANNUITIES",
        "title_number": "7",
        "subtitle": None,
        "subtitle_label": None,
        "chapter_number": None,
        "chapter_title": None,
    }

    # SUBTITLE line: "SUBTITLE A. LIFE INSURANCE IN GENERAL"
    m = re.search(r"SUBTITLE\s+([A-Z])\.\s+(.+)", text)
    if m:
        meta["subtitle_label"] = m.group(1)
        meta["subtitle"] = m.group(2).strip()

    # CHAPTER line: "CHAPTER 1101. LIFE INSURANCE"
    m = re.search(r"CHAPTER\s+(\d+)\.\s+(.+)", text)
    if m:
        meta["chapter_number"] = int(m.group(1))
        meta["chapter_title"] = m.group(2).strip()

    return meta


# --- Section Splitting ---

# Matches lines like: "Sec. 1101.001.  APPLICABILITY OF SUBCHAPTER."
# The section title runs from the section number to the next period followed
# by two spaces or end-of-line (the convention used in these statutes).
SECTION_PATTERN = re.compile(
    r"^(Sec\.\s+(\d+\.\d+[A-Za-z]?)\.\s\s+(.+?)\.)\s{2}",
    re.MULTILINE
)

SUBCHAPTER_PATTERN = re.compile(
    r"^SUBCHAPTER\s+([A-Z])\.\s*(.+)$",
    re.MULTILINE
)


def split_into_sections(text: str, chapter_meta: dict) -> list[dict]:
    """
    Split cleaned statute text into section-level chunks.
    Each chunk carries full metadata for downstream retrieval.
    """
    # First, find all subchapter boundaries so we can tag each section
    subchapter_spans = []
    for m in SUBCHAPTER_PATTERN.finditer(text):
        subchapter_spans.append({
            "label": m.group(1),
            "title": m.group(2).strip(),
            "start": m.start(),
        })

    def get_subchapter_at(pos: int) -> dict:
        """Return the subchapter active at a given character position."""
        current = {"label": None, "title": None}
        for sc in subchapter_spans:
            if sc["start"] <= pos:
                current = {"label": sc["label"], "title": sc["title"]}
            else:
                break
        return current

    # Find all section start positions
    section_starts = list(SECTION_PATTERN.finditer(text))

    if not section_starts:
        return []

    chunks = []
    for i, match in enumerate(section_starts):
        section_id = match.group(2)       # e.g. "1101.001"
        section_title = match.group(3)    # e.g. "APPLICABILITY OF SUBCHAPTER"

        # Section text runs from this match start to the next section start
        start = match.start()
        end = section_starts[i + 1].start() if i + 1 < len(section_starts) else len(text)
        section_text = text[start:end].strip()

        # Determine which subchapter this section falls under
        sc = get_subchapter_at(start)

        chunks.append({
            "chunk_id": f"TX-IN-{section_id}",
            "section_id": section_id,
            "section_title": section_title,
            "chapter_number": chapter_meta["chapter_number"],
            "chapter_title": chapter_meta["chapter_title"],
            "subtitle_label": chapter_meta["subtitle_label"],
            "subtitle": chapter_meta["subtitle"],
            "subchapter_label": sc["label"],
            "subchapter_title": sc["title"],
            "text": section_text,
        })

    return chunks


# --- Main Pipeline ---

def parse_file(filepath: str) -> list[dict]:
    """Parse a single .txt statute file into chunks."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    cleaned = clean_raw_text(raw)
    meta = parse_header(cleaned)

    if meta["chapter_number"] is None:
        print(f"  WARNING: Could not parse chapter number from {filepath}")
        return []

    chunks = split_into_sections(cleaned, meta)
    return chunks


def parse_all(input_dir: str, output_path: str) -> list[dict]:
    """Parse all .txt files in input_dir and write chunks to JSON."""
    txt_files = sorted(Path(input_dir).glob("IN_*.txt"))

    if not txt_files:
        print(f"No IN_*.txt files found in {input_dir}")
        return []

    print(f"TRIAL Parser — Phase 2, Step 1")
    print(f"Input directory: {input_dir}")
    print(f"Found {len(txt_files)} statute files")
    print("-" * 50)

    all_chunks = []
    for filepath in txt_files:
        chunks = parse_file(str(filepath))
        print(f"  {filepath.name}: {len(chunks)} sections")
        all_chunks.extend(chunks)

    # Write output
    output = {
        "source": "Texas Insurance Code, Title 7 — Life Insurance and Annuities",
        "parser_version": "1.0",
        "total_files": len(txt_files),
        "total_chunks": len(all_chunks),
        "chunks": all_chunks,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Summary stats
    print("-" * 50)
    print(f"Total chunks: {len(all_chunks)}")
    text_lengths = [len(c["text"]) for c in all_chunks]
    if text_lengths:
        avg_len = sum(text_lengths) / len(text_lengths)
        print(f"Chunk sizes: min={min(text_lengths)}, avg={avg_len:.0f}, max={max(text_lengths)} chars")
    print(f"Output: {output_path}")

    return all_chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TRIAL statute text parser")
    parser.add_argument("--input-dir", default="raw_html",
                        help="Directory containing IN_XXXX.txt files (default: raw_html)")
    parser.add_argument("--output", default="chunks.json",
                        help="Output JSON file path (default: chunks.json)")
    args = parser.parse_args()

    parse_all(args.input_dir, args.output)
