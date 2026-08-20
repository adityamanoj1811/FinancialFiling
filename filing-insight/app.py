"""
app.py
------
Filing Insight | Multi-Company Financial Filing Intelligence
CRED-Inspired Luxury Fintech UI / UX Design System.

Features:
- Tactile Obsidian & Brushed-Metal "Company Credit Cards"
- Neo-Fintech Dark Mode with Smooth Micro-Interactions & Radial Glows
- Streaming Multi-Turn RAG Chat with Verifiable Transaction-Slip Citations
- Standardized Comp Table & Computed Financial Ratios
- Luminous Neon Plotly Visual Financial Analytics
- Institutional Executive Research Report Synthesis
- Document & Vector Index Inspector
- Multi-Format Exports (CSV, Excel, Markdown)
"""

import os
import io
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq

from backend.config import (
    APP_TITLE,
    APP_SUBTITLE,
    MAX_PDFS_ALLOWED,
    GROQ_API_KEY_ENV_VAR,
    FINANCIAL_METRICS,
    SAMPLE_QUERIES,
    SAMPLE_FILINGS,
    AVAILABLE_GROQ_MODELS,
    DATA_DIR,
)
from backend.pdf_parser import extract_pages_from_pdf, validate_extracted_text
from backend.chunker import chunk_pages
from backend.vector_store import VectorStore
from backend.rag_pipeline import stream_answer_question, answer_question
from backend.metrics_extractor import (
    extract_metrics,
    parse_numeric_value,
    compute_financial_ratios,
    generate_executive_summary,
)

# ---------------------------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Filing Insight | Institutional Financial Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CRED-INSPIRED LUXURY FINTECH DESIGN SYSTEM (NO EMOJIS, OBSIDIAN & GOLD)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap');

    /* Global Dark Backdrop & Typography */
    .stApp {
        background-color: #08080A;
        background-image: 
            radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.12) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.06) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(139, 92, 246, 0.05) 0px, transparent 50%);
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: #E2E8F0;
    }

    /* Top CRED Hero Banner */
    .cred-hero {
        background: linear-gradient(145deg, #101015 0%, #15151E 50%, #0A0A0F 100%);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    .cred-hero::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 320px;
        height: 100%;
        background: radial-gradient(circle at 100% 0%, rgba(59, 130, 246, 0.15), transparent 70%);
        pointer-events: none;
    }
    .cred-hero-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #60A5FA;
        margin-bottom: 8px;
    }
    .cred-hero-title {
        font-family: 'Space Grotesk', 'Plus Jakarta Sans', sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        line-height: 1.15;
        margin-bottom: 6px;
    }
    .cred-hero-sub {
        font-size: 0.92rem;
        color: #94A3B8;
        letter-spacing: 0.01em;
        max-width: 780px;
        margin: 0;
    }

    /* Tactile Company Credit Cards (CRED Style) */
    .company-card {
        background: linear-gradient(135deg, #181822 0%, #121218 60%, #0D0D12 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 16px;
        position: relative;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.15);
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease;
    }
    .company-card:hover {
        transform: translateY(-4px);
        border-color: rgba(96, 165, 250, 0.4);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(59, 130, 246, 0.15);
    }
    .card-chip {
        width: 36px;
        height: 26px;
        background: linear-gradient(135deg, #E2B96F 0%, #C59B47 50%, #E8CD94 100%);
        border-radius: 4px;
        margin-bottom: 14px;
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.4), 0 2px 4px rgba(0, 0, 0, 0.4);
        position: relative;
    }
    .card-chip::after {
        content: '';
        position: absolute;
        top: 6px;
        left: 0;
        right: 0;
        height: 1px;
        background: rgba(0, 0, 0, 0.25);
    }
    .card-company-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        color: #F8FAFC;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .card-meta-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        letter-spacing: 0.16em;
        color: #64748B;
        margin-bottom: 16px;
    }
    .card-metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        padding-top: 12px;
    }
    .card-stat-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #94A3B8;
        font-weight: 600;
    }
    .card-stat-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.05rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 2px;
    }
    .stat-accent-green {
        color: #10B981;
    }
    .stat-accent-blue {
        color: #60A5FA;
    }

    /* CRED Black KPI Cards */
    .cred-kpi {
        background: #111116;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .cred-kpi-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: #64748B;
        font-weight: 600;
    }
    .cred-kpi-val {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.45rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 4px;
        letter-spacing: -0.02em;
    }

    /* Transaction Slip Grounding & Citations */
    .citation-slip {
        background: #12121A;
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 10px 0;
        font-size: 0.83rem;
        color: #CBD5E1;
    }
    .slip-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #60A5FA;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
    }

    /* Badges & Pills */
    .cred-pill {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .cred-pill-live {
        background: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .cred-pill-neutral {
        background: rgba(255, 255, 255, 0.05);
        color: #94A3B8;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* CRED Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 2px;
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.88rem;
        font-weight: 500;
        color: #64748B;
        padding: 10px 18px;
        border-radius: 8px 8px 0 0;
        border: none;
        transition: color 0.15s ease;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.04) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #3B82F6 !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
        transition: all 0.2s ease;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "metrics_table" not in st.session_state:
    st.session_state.metrics_table = {}
if "ratios_table" not in st.session_state:
    st.session_state.ratios_table = {}
if "executive_summary" not in st.session_state:
    st.session_state.executive_summary = ""
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


def reset_session():
    st.session_state.vector_store = None
    st.session_state.processed_files = []
    st.session_state.chat_history = []
    st.session_state.metrics_table = {}
    st.session_state.ratios_table = {}
    st.session_state.executive_summary = ""
    st.session_state.pending_query = None
    st.rerun()


# ---------------------------------------------------------------------------
# SIDEBAR -- CRED OBSIDIAN CONTROL CONSOLE
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div style="font-family: \'Space Grotesk\', sans-serif; font-size: 1.3rem; font-weight: 700; letter-spacing: 0.08em; color: #FFFFFF;">FILING INSIGHT</div>', unsafe_allow_html=True)
    st.caption("Institutional Financial Intelligence Terminal")

    st.markdown("---")
    st.markdown('<span style="font-family: \'JetBrains Mono\'; font-size: 0.72rem; letter-spacing: 0.18em; color: #64748B; text-transform: uppercase;">1. API AUTHENTICATION</span>', unsafe_allow_html=True)

    env_key = os.environ.get(GROQ_API_KEY_ENV_VAR, "")
    raw_key = st.text_input(
        "Groq API Key",
        value=env_key,
        type="password",
        help="Free API key from console.groq.com. Powers fast Llama inference.",
    )
    groq_api_key = raw_key.strip().strip("'").strip('"') if raw_key else ""

    if groq_api_key:
        st.markdown('<span class="cred-pill cred-pill-live">CONNECTED / READY</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="cred-pill cred-pill-neutral">AWAITING API KEY</span>', unsafe_allow_html=True)

    selected_model = st.selectbox(
        "Inference Model",
        options=AVAILABLE_GROQ_MODELS,
        index=0,
        help="Select primary Groq model. If unavailable or deprecated, automatic fallback models will be used.",
    )

    st.markdown("---")
    st.markdown('<span style="font-family: \'JetBrains Mono\'; font-size: 0.72rem; letter-spacing: 0.18em; color: #64748B; text-transform: uppercase;">2. PRESET WORKSPACE</span>', unsafe_allow_html=True)
    st.caption("Instantly load verified filings for Reliance Industries, TCS, and Infosys:")

    demo_btn = st.button("Load Sample Filings", use_container_width=True, type="secondary")

    st.markdown("---")
    st.markdown('<span style="font-family: \'JetBrains Mono\'; font-size: 0.72rem; letter-spacing: 0.18em; color: #64748B; text-transform: uppercase;">3. CUSTOM FILINGS</span>', unsafe_allow_html=True)
    st.caption(f"Upload PDF disclosures (up to {MAX_PDFS_ALLOWED} documents):")

    uploaded_files = st.file_uploader(
        "Select PDF filings",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload company financial filings in PDF format.",
    )

    if uploaded_files and len(uploaded_files) > MAX_PDFS_ALLOWED:
        st.warning(f"Only the first {MAX_PDFS_ALLOWED} files will be processed.")
        uploaded_files = uploaded_files[:MAX_PDFS_ALLOWED]

    process_btn = st.button("Process & Index Uploads", type="primary", use_container_width=True)

    if st.session_state.processed_files:
        st.markdown("---")
        st.markdown('<span style="font-family: \'JetBrains Mono\'; font-size: 0.72rem; letter-spacing: 0.18em; color: #64748B; text-transform: uppercase;">ACTIVE VAULT</span>', unsafe_allow_html=True)
        for doc_name in st.session_state.processed_files:
            c1, c2 = st.columns([4, 1])
            c1.caption(f"`{doc_name}`")
            if c2.button("X", key=f"del_{doc_name}", help=f"Remove {doc_name}"):
                if st.session_state.vector_store:
                    st.session_state.vector_store.remove_source(doc_name)
                st.session_state.processed_files.remove(doc_name)
                st.session_state.metrics_table.pop(doc_name, None)
                st.session_state.ratios_table.pop(doc_name, None)
                st.rerun()

        if st.button("Reset Vault", use_container_width=True):
            reset_session()


# ---------------------------------------------------------------------------
# INGESTION CONTROLS
# ---------------------------------------------------------------------------
if demo_btn:
    with st.spinner("Indexing sample corporate filings into FAISS vault..."):
        if st.session_state.vector_store is None:
            st.session_state.vector_store = VectorStore()

        sample_paths = [
            DATA_DIR / "Reliance_Industries_Q1_FY25.pdf",
            DATA_DIR / "TCS_Q1_FY25.pdf",
            DATA_DIR / "Infosys_Q1_FY25.pdf",
        ]

        loaded_count = 0
        for p in sample_paths:
            if p.exists() and p.name not in st.session_state.processed_files:
                pages = extract_pages_from_pdf(str(p))
                chunks = chunk_pages(pages, source_name=p.name)
                st.session_state.vector_store.add_chunks(chunks)
                st.session_state.processed_files.append(p.name)
                loaded_count += 1

        if loaded_count > 0:
            st.success(f"Indexed {loaded_count} corporate filing(s).")
            st.rerun()
        else:
            st.info("Sample filings already loaded.")

if process_btn:
    if not uploaded_files:
        st.sidebar.error("Please upload at least one PDF file.")
    else:
        if st.session_state.vector_store is None:
            with st.spinner("Initializing FastEmbed vector index..."):
                st.session_state.vector_store = VectorStore()

        progress_bar = st.progress(0, text="Ingesting...")
        total = len(uploaded_files)

        for i, pdf_file in enumerate(uploaded_files):
            if pdf_file.name in st.session_state.processed_files:
                continue

            progress_bar.progress(i / total, text=f"Parsing {pdf_file.name}...")
            pages = extract_pages_from_pdf(pdf_file)
            full_text = "\n\n".join(p["text"] for p in pages)

            if not validate_extracted_text(full_text):
                st.warning(f"'{pdf_file.name}' contains minimal extractable text.")

            progress_bar.progress((i + 0.5) / total, text=f"Indexing {pdf_file.name} into FAISS...")
            chunks = chunk_pages(pages, source_name=pdf_file.name)
            st.session_state.vector_store.add_chunks(chunks)
            st.session_state.processed_files.append(pdf_file.name)

        progress_bar.progress(1.0, text="Indexing complete.")
        st.success(f"Successfully indexed {len(uploaded_files)} filing(s).")
        st.rerun()


# ---------------------------------------------------------------------------
# MAIN CRED-STYLE INTERFACE
# ---------------------------------------------------------------------------

# Hero Banner
st.markdown(
    f"""
    <div class="cred-hero">
        <div class="cred-hero-tag">INSTITUTIONAL INTELLIGENCE</div>
        <div class="cred-hero-title">{APP_TITLE}</div>
        <div class="cred-hero-sub">{APP_SUBTITLE}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.processed_files:
    st.info("To activate the intelligence vault, click 'Load Sample Filings' in the sidebar or upload corporate PDF disclosures.")

    st.markdown('<div style="font-family: \'JetBrains Mono\'; font-size: 0.78rem; letter-spacing: 0.18em; color: #64748B; text-transform: uppercase; margin-bottom: 12px;">SYSTEM ARCHITECTURE</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="cred-kpi">
                <div class="cred-kpi-label">Multi-Document RAG</div>
                <div style="font-size: 0.86rem; color: #94A3B8; margin-top: 8px; line-height: 1.4;">
                    Natural-language financial queries across multiple enterprise filings with strict page-level citation slips.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="cred-kpi">
                <div class="cred-kpi-label">Standardized Comp Matrix</div>
                <div style="font-size: 0.86rem; color: #94A3B8; margin-top: 8px; line-height: 1.4;">
                    Zero-shot structured metric extraction with automated operating leverage and net profit margin analytics.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="cred-kpi">
                <div class="cred-kpi-label">Luminous Visuals</div>
                <div style="font-size: 0.86rem; color: #94A3B8; margin-top: 8px; line-height: 1.4;">
                    Interactive neon financial charts benchmarking revenue scale, margin efficiency, and balance sheet solvency.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    # Top KPI Metrics Overview
    doc_count = len(st.session_state.processed_files)
    stats = st.session_state.vector_store.get_source_stats() if st.session_state.vector_store else {}
    total_chunks = sum(s["chunk_count"] for s in stats.values())
    total_pages = sum(s["page_count"] for s in stats.values())

    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.markdown(
            f"""
            <div class="cred-kpi">
                <div class="cred-kpi-label">Active Filings</div>
                <div class="cred-kpi-val">{doc_count} Vaults</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_k2:
        st.markdown(
            f"""
            <div class="cred-kpi">
                <div class="cred-kpi-label">Processed Pages</div>
                <div class="cred-kpi-val">{total_pages} Pages</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_k3:
        st.markdown(
            f"""
            <div class="cred-kpi">
                <div class="cred-kpi-label">FAISS Vectors</div>
                <div class="cred-kpi-val">{total_chunks} Vectors</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_k4:
        st.markdown(
            """
            <div class="cred-kpi">
                <div class="cred-kpi-label">Inference Model</div>
                <div class="cred-kpi-val" style="font-size: 1.25rem;">Llama-3.3 70B</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Render Tactile "Company Credit Cards" for each filing
    st.markdown('<div style="font-family: \'JetBrains Mono\'; font-size: 0.75rem; letter-spacing: 0.2em; color: #64748B; text-transform: uppercase; margin-top: 14px; margin-bottom: 12px;">ACTIVE CORPORATE DISCLOSURE CARDS</div>', unsafe_allow_html=True)
    card_cols = st.columns(min(3, doc_count))
    for idx, doc_name in enumerate(st.session_state.processed_files[:3]):
        col = card_cols[idx]
        company_clean = doc_name.replace(".pdf", "").replace("_", " ")
        doc_stats = stats.get(doc_name, {})
        metrics = st.session_state.metrics_table.get(doc_name, {})
        ratios = st.session_state.ratios_table.get(doc_name, {})

        rev_display = metrics.get("Total Revenue", "Index Pending")
        pat_display = metrics.get("Net Profit", "Index Pending")
        margin_display = ratios.get("Calculated Operating Margin (%)", metrics.get("Operating Margin (%)", "N/A"))

        with col:
            st.markdown(
                f"""
                <div class="company-card">
                    <div class="card-chip"></div>
                    <div class="card-company-name">{company_clean[:22]}</div>
                    <div class="card-meta-num">INDEX ID •••• {idx+1}024 • Q1 FY25</div>
                    <div class="card-metrics-grid">
                        <div>
                            <div class="card-stat-label">Total Revenue</div>
                            <div class="card-stat-val stat-accent-blue">{rev_display}</div>
                        </div>
                        <div>
                            <div class="card-stat-label">Operating Margin</div>
                            <div class="card-stat-val stat-accent-green">{margin_display}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Primary Navigation Tabs
    tab_chat, tab_metrics, tab_charts, tab_exec, tab_explorer = st.tabs([
        "Interactive Q&A Chat",
        "Structured Comp Table",
        "Visual Analytics",
        "Executive AI Report",
        "Document & Index Explorer",
    ])

    # =========================================================================
    # TAB 1: INTERACTIVE RAG CHAT
    # =========================================================================
    with tab_chat:
        st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.2rem; font-weight: 700; color: #FFFFFF;">Multi-Document Financial RAG</div>', unsafe_allow_html=True)
        st.caption("Submit queries across all active corporate disclosures. Every answer is grounded in retrieved chunks with exact page-level citations.")

        # Quick preset buttons (CRED styled pill buttons)
        st.markdown('<div style="font-family: \'JetBrains Mono\'; font-size: 0.72rem; letter-spacing: 0.16em; color: #64748B; text-transform: uppercase; margin-bottom: 8px;">PRESET QUERIES</div>', unsafe_allow_html=True)
        prompt_cols = st.columns(3)
        for idx, q_text in enumerate(SAMPLE_QUERIES[:6]):
            col = prompt_cols[idx % 3]
            if col.button(q_text, key=f"quick_q_{idx}", use_container_width=True):
                st.session_state.pending_query = q_text
                st.rerun()

        filter_col1, filter_col2 = st.columns([3, 1])
        with filter_col1:
            active_scope = st.multiselect(
                "Filter Scope:",
                options=st.session_state.processed_files,
                default=[],
                placeholder="Searching all indexed filings...",
            )
        with filter_col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        st.markdown("---")

        # Chat history display
        for turn in st.session_state.chat_history:
            with st.chat_message(turn["role"]):
                st.markdown(turn["content"])
                if turn.get("sources"):
                    with st.expander(f"Sources Cited ({len(turn['sources'])} documents)", expanded=False):
                        for s in turn["sources"]:
                            st.write(f"- `{s}`")
                if turn.get("chunks"):
                    with st.expander("Transaction Grounding Slips", expanded=False):
                        for c_idx, ch in enumerate(turn["chunks"][:6]):
                            st.markdown(
                                f"""
                                <div class="citation-slip">
                                    <div class="slip-header">
                                        <span>DOCUMENT: {ch.get('source')}</span>
                                        <span>PAGE {ch.get('page_number', 1)} | SCORE {ch.get('score', 0):.3f}</span>
                                    </div>
                                    <div>{ch.get('text')[:320]}...</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

        user_input = st.chat_input("Query enterprise revenue, EBITDA, margins, segments, or balance sheet health...")
        query_to_run = user_input or st.session_state.pending_query

        if query_to_run:
            st.session_state.pending_query = None

            if not groq_api_key:
                st.error("Enter your Groq API Key in the sidebar to execute LLM queries.")
            else:
                client = Groq(api_key=groq_api_key)

                st.session_state.chat_history.append({"role": "user", "content": query_to_run})
                with st.chat_message("user"):
                    st.markdown(query_to_run)

                with st.chat_message("assistant"):
                    response_container = st.empty()
                    meta_holder = {"sources": [], "chunks": []}

                    def token_stream_generator():
                        for token in stream_answer_question(
                            client=client,
                            question=query_to_run,
                            vector_store=st.session_state.vector_store,
                            chat_history=st.session_state.chat_history[:-1],
                            active_sources=active_scope if active_scope else None,
                            model=selected_model,
                        ):
                            if isinstance(token, dict) and token.get("__metadata__"):
                                meta_holder["sources"] = token.get("sources_used", [])
                                meta_holder["chunks"] = token.get("chunks_used", [])
                            elif isinstance(token, str):
                                yield token

                    full_answer = response_container.write_stream(token_stream_generator())

                    sources_meta = meta_holder["sources"]
                    chunks_meta = meta_holder["chunks"]

                    if sources_meta:
                        st.caption("Sources: " + ", ".join(f"`{s}`" for s in sources_meta))

                    if chunks_meta:
                        with st.expander("Grounding Transaction Slips", expanded=False):
                            for c in chunks_meta:
                                st.markdown(
                                    f"""
                                    <div class="citation-slip">
                                        <div class="slip-header">
                                            <span>DOCUMENT: {c.get('source')}</span>
                                            <span>PAGE {c.get('page_number', 1)} | SIMILARITY: {c.get('score', 0):.3f}</span>
                                        </div>
                                        <div>{c.get('text')}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_answer,
                    "sources": sources_meta,
                    "chunks": chunks_meta,
                })

        if st.session_state.chat_history:
            chat_md = "# Filing Insight — Institutional Chat Transcript\n\n"
            for t in st.session_state.chat_history:
                role_label = "User" if t["role"] == "user" else "Assistant"
                chat_md += f"### {role_label}:\n{t['content']}\n\n"
            st.download_button(
                "Export Transcript (Markdown)",
                data=chat_md,
                file_name="filing_insight_chat.md",
                mime="text/markdown",
            )

    # =========================================================================
    # TAB 2: STRUCTURED FINANCIAL METRICS & COMP TABLE
    # =========================================================================
    with tab_metrics:
        st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.2rem; font-weight: 700; color: #FFFFFF;">Standardized Comp Matrix</div>', unsafe_allow_html=True)
        st.caption("Automated zero-shot extraction of standardized metrics with derived profit margins and capital structure ratios.")

        extract_all_btn = st.button("Extract Financial Metrics", type="primary")

        if extract_all_btn:
            if not groq_api_key:
                st.error("Enter your Groq API Key in the sidebar.")
            else:
                client = Groq(api_key=groq_api_key)
                for src in st.session_state.processed_files:
                    with st.spinner(f"Extracting metrics for {src}..."):
                        metrics = extract_metrics(client, st.session_state.vector_store, src, model=selected_model)
                        ratios = compute_financial_ratios(metrics)
                        st.session_state.metrics_table[src] = metrics
                        st.session_state.ratios_table[src] = ratios
                st.success("Financial metrics extracted across all filings.")
                st.rerun()

        if st.session_state.metrics_table:
            df_metrics = pd.DataFrame(st.session_state.metrics_table)
            df_metrics = df_metrics.reindex(FINANCIAL_METRICS)

            st.dataframe(df_metrics, use_container_width=True)

            if st.session_state.ratios_table:
                st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-top: 20px;">Derived Financial Ratios</div>', unsafe_allow_html=True)
                df_ratios = pd.DataFrame(st.session_state.ratios_table)
                st.dataframe(df_ratios, use_container_width=True)

            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                csv_data = df_metrics.to_csv().encode("utf-8")
                st.download_button(
                    "Download CSV",
                    data=csv_data,
                    file_name="filing_metrics_comparison.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with exp_col2:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    df_metrics.to_excel(writer, sheet_name="Financial Metrics")
                    if st.session_state.ratios_table:
                        df_ratios.to_excel(writer, sheet_name="Financial Ratios")
                st.download_button(
                    "Download Excel (.xlsx)",
                    data=excel_buffer.getvalue(),
                    file_name="filing_metrics_workbook.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
        else:
            st.info("Click 'Extract Financial Metrics' to populate the standardized matrix.")

    # =========================================================================
    # TAB 3: LUMINOUS VISUAL ANALYTICS (PLOTLY DARK NEON)
    # =========================================================================
    with tab_charts:
        st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.2rem; font-weight: 700; color: #FFFFFF;">Luminous Financial Analytics</div>', unsafe_allow_html=True)
        st.caption("Interactive neon visualizations benchmarking revenue scale, operating margins, and balance sheet solvency.")

        if not st.session_state.metrics_table:
            st.info("Extract metrics in the 'Structured Comp Table' tab first to generate charts.")
        else:
            chart_rows = []
            for src, metrics in st.session_state.metrics_table.items():
                short_name = src.replace(".pdf", "").replace("_", " ")
                rev = parse_numeric_value(metrics.get("Total Revenue"))
                pat = parse_numeric_value(metrics.get("Net Profit"))
                ebitda = parse_numeric_value(metrics.get("EBITDA"))
                ebit = parse_numeric_value(metrics.get("Operating Profit (EBIT)"))
                assets = parse_numeric_value(metrics.get("Total Assets"))
                debt = parse_numeric_value(metrics.get("Total Debt"))
                op_margin = parse_numeric_value(metrics.get("Operating Margin (%)"))
                net_margin = parse_numeric_value(metrics.get("Net Profit Margin (%)"))

                if (op_margin is None or op_margin == 0) and rev and ebit:
                    op_margin = round((ebit / rev) * 100, 2)
                if (net_margin is None or net_margin == 0) and rev and pat:
                    net_margin = round((pat / rev) * 100, 2)

                chart_rows.append({
                    "Filing": short_name,
                    "Total Revenue": rev or 0,
                    "Net Profit": pat or 0,
                    "EBITDA": ebitda or 0,
                    "Operating Profit (EBIT)": ebit or 0,
                    "Total Assets": assets or 0,
                    "Total Debt": debt or 0,
                    "Operating Margin (%)": op_margin or 0,
                    "Net Profit Margin (%)": net_margin or 0,
                })

            df_chart = pd.DataFrame(chart_rows)

            c_plot1, c_plot2 = st.columns(2)

            with c_plot1:
                fig_scale = px.bar(
                    df_chart,
                    x="Filing",
                    y=["Total Revenue", "Net Profit", "EBITDA"],
                    barmode="group",
                    title="Revenue, EBITDA & Net Profit Scale",
                    labels={"value": "Amount (Native Units)", "variable": "Metric"},
                    color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B"],
                )
                fig_scale.update_layout(
                    paper_bgcolor="#0D0D12",
                    plot_bgcolor="#0D0D12",
                    font=dict(color="#E2E8F0", family="Plus Jakarta Sans"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=20, r=20, t=50, b=20),
                )
                fig_scale.update_xaxes(gridcolor="rgba(255, 255, 255, 0.05)")
                fig_scale.update_yaxes(gridcolor="rgba(255, 255, 255, 0.05)")
                st.plotly_chart(fig_scale, use_container_width=True)

            with c_plot2:
                fig_margin = px.bar(
                    df_chart,
                    x="Filing",
                    y=["Operating Margin (%)", "Net Profit Margin (%)"],
                    barmode="group",
                    title="Operating vs. Net Profit Margin (%)",
                    labels={"value": "Margin (%)", "variable": "Margin Type"},
                    color_discrete_sequence=["#60A5FA", "#34D399"],
                )
                fig_margin.update_layout(
                    paper_bgcolor="#0D0D12",
                    plot_bgcolor="#0D0D12",
                    font=dict(color="#E2E8F0", family="Plus Jakarta Sans"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=20, r=20, t=50, b=20),
                )
                fig_margin.update_xaxes(gridcolor="rgba(255, 255, 255, 0.05)")
                fig_margin.update_yaxes(gridcolor="rgba(255, 255, 255, 0.05)")
                st.plotly_chart(fig_margin, use_container_width=True)

            c_plot3, c_plot4 = st.columns(2)

            with c_plot3:
                fig_bs = px.bar(
                    df_chart,
                    x="Filing",
                    y=["Total Assets", "Total Debt"],
                    barmode="group",
                    title="Capital Structure: Total Assets vs. Debt",
                    labels={"value": "Amount", "variable": "Metric"},
                    color_discrete_sequence=["#06B6D4", "#EF4444"],
                )
                fig_bs.update_layout(
                    paper_bgcolor="#0D0D12",
                    plot_bgcolor="#0D0D12",
                    font=dict(color="#E2E8F0", family="Plus Jakarta Sans"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=20, r=20, t=50, b=20),
                )
                fig_bs.update_xaxes(gridcolor="rgba(255, 255, 255, 0.05)")
                fig_bs.update_yaxes(gridcolor="rgba(255, 255, 255, 0.05)")
                st.plotly_chart(fig_bs, use_container_width=True)

            with c_plot4:
                fig_scatter = px.scatter(
                    df_chart,
                    x="Operating Margin (%)",
                    y="Net Profit Margin (%)",
                    text="Filing",
                    size=[25] * len(df_chart),
                    color="Filing",
                    title="Margin Efficiency Matrix",
                )
                fig_scatter.update_traces(textposition="top center")
                fig_scatter.update_layout(
                    paper_bgcolor="#0D0D12",
                    plot_bgcolor="#0D0D12",
                    font=dict(color="#E2E8F0", family="Plus Jakarta Sans"),
                    showlegend=False,
                    margin=dict(l=20, r=20, t=50, b=20),
                )
                fig_scatter.update_xaxes(gridcolor="rgba(255, 255, 255, 0.05)")
                fig_scatter.update_yaxes(gridcolor="rgba(255, 255, 255, 0.05)")
                st.plotly_chart(fig_scatter, use_container_width=True)

    # =========================================================================
    # TAB 4: AI EXECUTIVE RESEARCH REPORT
    # =========================================================================
    with tab_exec:
        st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.2rem; font-weight: 700; color: #FFFFFF;">Institutional Research Report</div>', unsafe_allow_html=True)
        st.caption("Comprehensive cross-company comparative synthesis synthesized by Groq Llama-3.3.")

        gen_exec_btn = st.button("Generate Executive Synthesis Report", type="primary")

        if gen_exec_btn:
            if not groq_api_key:
                st.error("Enter your Groq API Key in the sidebar.")
            else:
                client = Groq(api_key=groq_api_key)
                with st.spinner("Synthesizing institutional research report..."):
                    st.session_state.executive_summary = generate_executive_summary(
                        client=client,
                        vector_store=st.session_state.vector_store,
                        sources=st.session_state.processed_files,
                        model=selected_model,
                    )
                st.success("Executive report generated.")

        if st.session_state.executive_summary:
            st.markdown(st.session_state.executive_summary)

            st.download_button(
                "Export Report (Markdown)",
                data=st.session_state.executive_summary,
                file_name="institutional_executive_report.md",
                mime="text/markdown",
            )
        else:
            st.info("Click 'Generate Executive Synthesis Report' to run cross-company synthesis.")

    # =========================================================================
    # TAB 5: DOCUMENT & INDEX EXPLORER
    # =========================================================================
    with tab_explorer:
        st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.2rem; font-weight: 700; color: #FFFFFF;">Document & Vector Index Inspector</div>', unsafe_allow_html=True)
        st.caption("Inspect parsed page structures, vector chunk distributions, and embedding status.")

        if stats:
            st.caption("DOCUMENT REGISTRY")
            stats_rows = []
            for src, s in stats.items():
                stats_rows.append({
                    "Document": src,
                    "Pages Indexed": s["page_count"],
                    "Chunks Generated": s["chunk_count"],
                    "Character Count": f"{s['total_chars']:,}",
                    "Est. Tokens": f"{s['est_tokens']:,}",
                })
            st.table(pd.DataFrame(stats_rows))

            st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-top: 20px;">Chunk Search & Inspection</div>', unsafe_allow_html=True)
            selected_doc = st.selectbox("Select document:", options=list(stats.keys()))

            if selected_doc:
                chunks = st.session_state.vector_store.get_all_chunks(source_filter=selected_doc)
                st.caption(f"Displaying {len(chunks)} chunks for {selected_doc}:")

                search_filter = st.text_input("Filter chunk text by keyword:", "")
                filtered_chunks = [c for c in chunks if search_filter.lower() in c["text"].lower()] if search_filter else chunks

                for c in filtered_chunks[:15]:
                    with st.expander(f"Chunk #{c.get('chunk_id', 0)} | Page {c.get('page_number', 1)} ({c.get('char_count', len(c['text']))} chars)", expanded=False):
                        st.code(c["text"], language="markdown")
                        st.caption(f"Estimated Tokens: ~{c.get('token_est', len(c['text'])//4)}")
