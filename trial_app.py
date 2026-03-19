"""
TRIAL - Texas Regulatory Insurance Analysis Layer
Phase 4: Streamlit Demo Interface

A clean web interface for querying Texas insurance law statutes
via the TRIAL RAG pipeline. Displays answers with citations,
retrieval details, and citation validation status.

Prerequisites:
    pip install streamlit openai chromadb python-dotenv

Usage:
    streamlit run trial_app.py
"""

import streamlit as st
from trial_qa import generate_answer

# --- Page Configuration ---

st.set_page_config(
    page_title="TRIAL — Texas Insurance Law Assistant",
    page_icon=None,
    layout="centered",
)

# --- Custom Styling ---

st.markdown("""
<style>
    /* Clean up default Streamlit spacing */
    .block-container { padding-top: 2rem; max-width: 800px; }

    /* Header styling */
    .main-title { font-size: 2rem; font-weight: 700; margin-bottom: 0.2rem; }
    .subtitle { font-size: 1rem; color: #999; margin-bottom: 1.5rem; }

    /* Answer box — works on both light and dark themes */
    .answer-box {
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #4caf50;
        padding: 1.2rem;
        border-radius: 0 6px 6px 0;
        margin: 1rem 0;
        line-height: 1.6;
        color: inherit;
    }

    /* Validation badges */
    .badge-pass {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .badge-fail {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* Hide the top-right running status stickman indicator */
    [data-testid="stStatusWidget"] { display: none !important; }
    header [data-testid="stStatusWidget"] { display: none !important; }
    .stApp [data-testid="stStatusWidget"] { display: none !important; }
    /* Nuclear option: hide any iframe or element in the top-right status area */
    header { visibility: visible; }
    .stDeployButton { display: none !important; }
    #stStatusWidget { display: none !important; }
    div[data-testid="stAppRunningMan"] { display: none !important; }
    .stRunningMan { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- Header ---

st.markdown('<div class="main-title">TRIAL</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">'
    'Texas Regulatory Insurance Analysis Layer — '
    'A RAG system for Texas Insurance Code Title 7 (Life Insurance &amp; Annuities)'
    '</div>',
    unsafe_allow_html=True,
)

# --- Query Input (form makes Enter key submit) ---

with st.form("query_form", clear_on_submit=False):
    query = st.text_input(
        "Ask a question about Texas insurance law",
        placeholder='e.g., "What is the grace period for life insurance?" or "Sec. 1101.006"',
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        top_k = st.selectbox("Chunks", [3, 5, 7, 10], index=1, help="Number of statute sections to retrieve")
    with col2:
        st.markdown("")  # spacer

    run_query = st.form_submit_button("Ask", type="primary", use_container_width=True)

# --- Results ---

if run_query and query:
    # Use a plain status message instead of the stickman spinner
    status_placeholder = st.empty()
    status_placeholder.info("Retrieving statutes and generating answer...")
    result = generate_answer(query, top_k=top_k)
    status_placeholder.empty()

    # Answer
    st.markdown("### Answer")
    st.markdown(f'<div class="answer-box">{result["answer"]}</div>', unsafe_allow_html=True)

    # Citation validation
    citations = result["citations"]
    if citations["all_valid"]:
        badge = '<span class="badge-pass">✓ Citations Valid</span>'
    else:
        hallucinated = ", ".join(citations["hallucinated_citations"])
        badge = f'<span class="badge-fail">✗ Hallucinated: {hallucinated}</span>'

    cited_list = ", ".join(f"Sec. {s}" for s in citations["cited_sections"]) if citations["cited_sections"] else "None"
    st.markdown(f"{badge} &nbsp; Cited: {cited_list}", unsafe_allow_html=True)

    # Retrieved sections (collapsible)
    with st.expander("Retrieved Sections", expanded=False):
        for r in result["retrieval"]:
            score_display = f"{r['score']:.3f}"
            match_label = "exact" if r["match_type"] == "statute_id" else "semantic"
            st.markdown(
                f"**Sec. {r['section_id']}** — {r['section_title']}  \n"
                f"`score: {score_display}` · `{match_label}`"
            )

    # Model info
    st.caption(f"Model: {result['model']} · Retrieved {len(result['retrieval'])} sections")

elif run_query and not query:
    st.warning("Please enter a question.")

# --- Footer ---

st.divider()
st.caption(
    "TRIAL indexes Texas Insurance Code Title 7 (Chapters 1101–1154). "
    "23 chapters, 390 statute sections. "
    "Embeddings: OpenAI text-embedding-3-small. Vector store: ChromaDB. "
    "Generation: GPT-5.4."
)
