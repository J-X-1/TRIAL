# TRIAL — Texas Regulatory Insurance Analysis Layer

A RAG system that indexes Texas Insurance Code Title 7 (Life Insurance and Annuities) and answers natural language questions with cited statute references.

## Setup

Requires Python 3.10+ and an OpenAI API key.

```bash
pip install openai chromadb python-dotenv selenium webdriver-manager streamlit
```

Create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-...
```

## Files

| File | What it does |
|------|-------------|
| `trial_scraper_selenium_v2.py` | Scrapes statute text from the Texas Statutes website (Angular SPA, requires Selenium) |
| `trial_parser.py` | Parses raw text into 390 section-level chunks with metadata → `chunks.json` |
| `trial_embedder.py` | Embeds chunks with OpenAI `text-embedding-3-small`, stores in ChromaDB |
| `trial_retriever.py` | Retrieves relevant chunks via statute ID lookup or semantic search |
| `trial_qa.py` | Generates answers with GPT-5.4 and validates citations against retrieved context |
| `trial_app.py` | Streamlit web interface |

## How to Run

The scraper, parser, and embedder have already been run. Their outputs (`raw_html/`, `chunks.json`, `trial_chroma_db/`) are included. To rebuild from scratch, run them in order:

```bash
python trial_scraper_selenium_v2.py
python trial_parser.py
python trial_embedder.py
```

To query from the command line:
```bash
python trial_qa.py "What is the grace period for life insurance in Texas?"
python trial_qa.py "Sec. 1101.006"
```

To launch the web interface:
```bash
streamlit run trial_app.py
```

## Corpus

23 chapters, 390 statute sections scraped from [statutes.capitol.texas.gov](https://statutes.capitol.texas.gov). Covers life insurance, group life insurance, annuities, credit insurance, variable contracts, and related provisions.

## Evaluation

25 test questions scored against answer keys derived from the statute text. Each response was scored 0-4 points. More info in the `TRIAL eval/` folder.

| Category | Score |
|----------|-------|
| Direct Factual Lookup | 20/20 (100%) |
| Multi-Section Synthesis | 14/16 (87.5%) |
| Statute ID Lookup | 16/16 (100%) |
| Domain-Specific / Nuanced | 20/20 (100%) |
| Out-of-Scope (should decline) | 16/16 (100%) |
| Edge Cases | 10/12 (83.3%) |
| **Total** | **96/100 (96%)** |

Both deductions come from broad questions that needed more than 5 retrieved sections, producing correct but incomplete answers.
