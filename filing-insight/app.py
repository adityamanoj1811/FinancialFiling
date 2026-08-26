"""
app.py
------
Filing Insight | Multi-Company Financial Filing Intelligence
Custom Bento-Grid Modern Dashboard UI with Glassmorphic Tabs & Report Modals.

Features:
- Left floating capsule navigation sidebar (Avatar, Switch to Home button, API Key, Model selector, Sample & Custom Uploads)
- Top banner: "Hello, Ayushi." with subtitle and dynamic date pill
- Bento-grid layout with generous spacing, soft glowing borders, and interactive click triggers:
  * Clicking "Vector Embeddings" opens an Institutional System Telemetry & Vector Health Popup Modal
  * Clicking "Inner Progress" opens an Institutional Document Filing & Registry Report Popup Modal
- Premium Frosted Glassmorphism Tabs:
  * Beautifully spread across the full width with flex layout
  * True transparent backdrop-blur frosted glass look
  * Subtle 1px white border, soft top specular line, and zero orange/red underline artifacts
- Direct access to all original capabilities:
  1. Interactive Q&A Chat (RAG)
  2. Structured Comp Table & Ratios
  3. Visual Analytics (Charts)
  4. Executive AI Report
  5. Document & Index Explorer
"""

import os
# macOS can load separate OpenMP runtimes through FAISS and the local ML stack.
# Set before importing either dependency so the Streamlit process can safely use both.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
import io
import datetime
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
    MAX_PDF_SIZE_MB,
    MAX_QUERY_LENGTH,
    GROQ_API_TIMEOUT_SECONDS,
    GROQ_API_KEY_ENV_VAR,
    FINANCIAL_METRICS,
    SAMPLE_QUERIES,
    SAMPLE_FILINGS,
    AVAILABLE_GROQ_MODELS,
    DATA_DIR,
    HOME_PAGE_URL,
)
from backend.pdf_parser import (
    extract_pages_from_pdf,
    validate_extracted_text,
    validate_pdf_file,
)
from backend.chunker import chunk_pages
from backend.vector_store import VectorStore
from backend.rag_pipeline import stream_answer_question
from backend.metrics_extractor import (
    extract_metrics,
    extract_metrics_from_vector_store,
    parse_numeric_value,
    compute_financial_ratios,
    generate_executive_summary,
)

# ---------------------------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Filing Insight | Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# MODERN BENTO-GRID DESIGN SYSTEM WITH REFINED GLASSMORPHISM
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

    /* ── Global Background ──────────────────────────────────────────────── */
    .stApp {
        background-color: #000000;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: #F3F4F6;
    }

    /* Main Container Spacing */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 1400px;
    }

    /* ── Sidebar: fully let Streamlit handle toggle/collapse ───────────── */
    [data-testid="stSidebar"] {
        background-color: #0D120E !important;
        border-right: 1px solid rgba(74, 222, 128, 0.12);
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
    }
    /* Collapsed sidebar toggle button */
    [data-testid="stSidebarCollapsedControl"] {
        z-index: 999 !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        top: 1rem !important;
        left: 1rem !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 10px !important;
        color: rgba(255, 255, 255, 0.75) !important;
        width: 36px !important;
        height: 36px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: background 0.2s ease, border-color 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
    }
    [data-testid="stSidebarCollapsedControl"] button:hover {
        background: rgba(255, 255, 255, 0.16) !important;
        border-color: rgba(255, 255, 255, 0.35) !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebarCollapsedControl"] button svg {
        width: 16px !important;
        height: 16px !important;
    }

    /* Sidebar Profile Card */
    .sidebar-avatar-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 24px;
        text-align: center;
    }
    .sidebar-avatar {
        width: 68px;
        height: 68px;
        border-radius: 50%;
        background: linear-gradient(135deg, rgba(74, 222, 128, 0.22) 0%, rgba(255, 255, 255, 0.04) 100%);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #FFFFFF;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45), inset 0 1px 2px rgba(255, 255, 255, 0.25);
        margin-bottom: 14px;
        border: 1px solid rgba(74, 222, 128, 0.3);
    }
    .sidebar-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 16px;
    }
    .sidebar-switch-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: rgba(74, 222, 128, 0.08);
        border: 1px solid rgba(74, 222, 128, 0.22);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        color: #FFFFFF;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 9px 20px;
        border-radius: 9999px;
        text-decoration: none;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
        width: 100%;
        margin-bottom: 16px;
        transition: all 0.25s ease;
    }
    .sidebar-switch-pill:hover {
        background: rgba(74, 222, 128, 0.18);
        color: #FFFFFF;
        border-color: rgba(74, 222, 128, 0.45);
        transform: translateY(-1px);
    }

    /* ENTRANCE KEYFRAME ANIMATIONS (POP UP / POP DOWN ONE BY ONE) */
    @keyframes popDown {
        0% {
            opacity: 0;
            transform: translateY(-28px) scale(0.96);
        }
        60% {
            transform: translateY(4px) scale(1.01);
        }
        100% {
            opacity: 1;
            transform: translateY(0px) scale(1);
        }
    }

    @keyframes popUp {
        0% {
            opacity: 0;
            transform: translateY(32px) scale(0.95);
        }
        60% {
            transform: translateY(-4px) scale(1.01);
        }
        100% {
            opacity: 1;
            transform: translateY(0px) scale(1);
        }
    }

    @keyframes popIn {
        0% {
            opacity: 0;
            transform: scale(0.92);
        }
        65% {
            transform: scale(1.03);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }

    /* Staggered Element Bindings */
    .bento-header-container {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 32px;
        animation: popDown 0.65s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    .bento-card-1 {
        animation: popUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.12s both;
    }

    .bento-card-2 {
        animation: popUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.22s both;
    }

    .bento-card-3 {
        animation: popUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.32s both;
    }

    /* Bento action buttons popping up */
    [data-testid="column"]:nth-of-type(2) button {
        animation: popUp 0.65s cubic-bezier(0.16, 1, 0.3, 1) 0.28s both;
    }
    [data-testid="column"]:nth-of-type(3) button {
        animation: popUp 0.65s cubic-bezier(0.16, 1, 0.3, 1) 0.38s both;
    }

    /* Navigation tabs popping in with staggered effect */
    .stTabs [data-baseweb="tab-list"] {
        animation: popUp 0.75s cubic-bezier(0.16, 1, 0.3, 1) 0.44s both;
    }

    .stTabs [data-baseweb="tab"]:nth-child(1) { animation: popIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.46s both; }
    .stTabs [data-baseweb="tab"]:nth-child(2) { animation: popIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.52s both; }
    .stTabs [data-baseweb="tab"]:nth-child(3) { animation: popIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.58s both; }
    .stTabs [data-baseweb="tab"]:nth-child(4) { animation: popIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.64s both; }
    .stTabs [data-baseweb="tab"]:nth-child(5) { animation: popIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.70s both; }

    /* Floating Capsule Sidebar Entrance */
    [data-testid="stSidebar"] {
        animation: popDown 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    /* Header: Hello, Ayushi. */
    .bento-greeting {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.025em;
        line-height: 1.1;
    }
    .bento-greeting span {
        color: #FF7B60;
    }
    .bento-subtext {
        font-size: 1rem;
        color: #9CA3AF;
        margin-top: 8px;
        font-weight: 400;
    }
    .bento-date-pill {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.14);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        padding: 10px 22px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #E5E7EB;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
    }

    /* Bento Grid Tiles Styles */
    .bento-card {
        border-radius: 30px;
        padding: 28px 32px;
        position: relative;
        overflow: hidden;
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease;
        margin-bottom: 24px;
    }
    .bento-card:hover {
        transform: translateY(-4px);
    }

    /* Card 1: Warm Peach Main Feature Card */
    .bento-peach {
        background: #FCECE5;
        color: #1A1210;
        box-shadow: 0 20px 40px -12px rgba(252, 236, 229, 0.22);
    }
    .bento-peach .bento-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.65rem;
        font-weight: 800;
        color: #1A1210;
        margin-bottom: 10px;
    }
    .bento-peach .bento-desc {
        font-size: 0.92rem;
        color: #6B4E47;
        line-height: 1.5;
        margin-bottom: 28px;
        max-width: 90%;
    }
    .bento-peach .bento-link {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #B84338;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Card 2 & 3: Deep Indigo / Navy Vertical Cards */
    .bento-navy {
        background: linear-gradient(145deg, #171E2D 0%, #121722 100%);
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.07);
        box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.55);
    }
    .bento-navy .bento-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 8px;
    }
    .bento-navy .bento-desc {
        font-size: 0.82rem;
        color: #8C9CB8;
        margin-top: 4px;
    }

    /* Bento Interactive Trigger Button */
    .bento-trigger-btn {
        margin-top: 10px;
    }
    .bento-trigger-btn button {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        backdrop-filter: blur(12px) !important;
        color: #E2E8F0 !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        border-radius: 9999px !important;
        padding: 6px 14px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    .bento-trigger-btn button:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(255, 255, 255, 0.35) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }

    /* MINIMALIST LUMINOUS TEXT TABS (NO GLASS PILL, FLOATING TEXT WITH BOTTOM GLOW) */
    .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: flex-start !important;
        align-items: center !important;
        gap: 24px !important;
        background: transparent !important;
        padding: 10px 0px 14px 0px !important;
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 28px !important;
        width: 100% !important;
    }

    .stTabs [data-baseweb="tab"] {
        text-align: center !important;
        justify-content: center !important;
        align-items: center !important;
        border-radius: 0px !important;
        color: #A1A1AA !important;
        font-family: 'Space Grotesk', 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.96rem !important;
        padding: 8px 14px !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        white-space: nowrap !important;
        outline: none !important;
        box-shadow: none !important;
        position: relative !important;
        cursor: pointer !important;
    }

    .stTabs [data-baseweb="tab"] > div,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] p {
        margin: 0 !important;
        line-height: normal !important;
        color: inherit !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #FFFFFF !important;
        background: transparent !important;
        transform: translateY(-2px);
    }

    .stTabs [data-baseweb="tab"]:focus,
    .stTabs [data-baseweb="tab"]:focus-visible,
    .stTabs [data-baseweb="tab"]:active {
        outline: none !important;
        box-shadow: none !important;
    }

    /* Active State: Text moves up, brightens, and radiates a subtle bottom glow */
    @keyframes gentleFloat {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
        100% { transform: translateY(0px); }
    }

    .stTabs [aria-selected="true"],
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: transparent !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        transform: translateY(-2px);
        text-shadow: 0 0 16px rgba(255, 255, 255, 0.7), 0 0 30px rgba(255, 123, 96, 0.45);
        animation: gentleFloat 3s ease-in-out infinite;
    }

    .stTabs [aria-selected="true"]::after,
    .stTabs [data-baseweb="tab"][aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: -4px;
        left: 50%;
        transform: translateX(-50%);
        width: 32px;
        height: 3px;
        border-radius: 9999px;
        background: linear-gradient(90deg, transparent, #FF7B60, transparent);
        box-shadow: 0 0 12px #FF7B60, 0 0 20px rgba(255, 123, 96, 0.6);
    }

    /* Remove default Streamlit tab highlight underline */
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Remove default Streamlit tab active bottom line & border */
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"],
    .stTabs hr {
        display: none !important;
        height: 0px !important;
        opacity: 0 !important;
    }

    /* Citation Slips & Grounding */
    .citation-slip {
        background: #171E2D;
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        padding: 16px 20px;
        margin: 12px 0;
        font-size: 0.85rem;
        color: #D1D5DB;
    }
    .slip-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #FF7B60;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
    }

    /* Modal / Dialog Glassmorphic Styling */
    div[data-testid="stDialog"] {
        background: rgba(14, 12, 12, 0.88) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 24px !important;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.75) !important;
    }

    /* Custom Glass Buttons */
    .stButton > button {
        border-radius: 14px;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 9px 20px;
        transition: all 0.2s ease;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Gradient background: faded light grey top → black bottom
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom, #2a2a2a 0%, #111111 40%, #000000 100%) !important;
        min-height: 100vh !important;
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
if "active_groq_api_key" not in st.session_state:
    st.session_state.active_groq_api_key = os.environ.get(GROQ_API_KEY_ENV_VAR, "").strip().strip("'").strip('"')


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
# POPUP DIALOGS FOR BENTO CARDS (ST.DIALOG)
# ---------------------------------------------------------------------------
@st.dialog("Vector Embeddings & Index Health Report")
def show_vector_modal(stats, total_chunks):
    st.markdown("### FAISS Vector Vault Status")
    st.caption("Active neural vector embeddings, dimensional projection & similarity indexing:")
    
    st.markdown(
        f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 18px 22px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px;">
            <div style="font-family: 'Space Grotesk'; font-size: 1.8rem; font-weight: 700; color: #60A5FA;">
                {total_chunks} Total Vectors
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">
                Embedding Architecture: <b>BAAI/bge-small-en-v1.5 (384 Dimensions)</b>
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 2px;">
                Vector Search Index: <b>FAISS L2 Normalized Euclidean Space</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if stats:
        st.markdown("#### Indexed Document Chunks Distribution")
        rows = []
        for src, s in stats.items():
            rows.append({
                "Document Name": src,
                "Chunks Indexed": s["chunk_count"],
                "Total Characters": f"{s['total_chars']:,}",
                "Estimated Tokens": f"{s['est_tokens']:,}",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No active document vectors indexed. Load sample filings or upload PDFs to populate.")


@st.dialog("Inner Progress & Filing Vault Registry")
def show_progress_modal(stats, total_pages, doc_count):
    st.markdown("### Document Ingestion & Page Registry")
    st.caption("Comprehensive parsed page distribution across verified company filings:")

    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; margin-bottom: 20px;">
            <div style="background: rgba(255, 255, 255, 0.05); padding: 14px 18px; border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.08);">
                <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-family: 'JetBrains Mono';">Active Vaults</div>
                <div style="font-family: 'Space Grotesk'; font-size: 1.5rem; font-weight: 700; color: #FFFFFF; margin-top: 4px;">{doc_count} Filings</div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.05); padding: 14px 18px; border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.08);">
                <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-family: 'JetBrains Mono';">Processed Pages</div>
                <div style="font-family: 'Space Grotesk'; font-size: 1.5rem; font-weight: 700; color: #FF7B60; margin-top: 4px;">{total_pages} Pages</div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.05); padding: 14px 18px; border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.08);">
                <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-family: 'JetBrains Mono';">System Status</div>
                <div style="font-family: 'Space Grotesk'; font-size: 1.5rem; font-weight: 700; color: #34D399; margin-top: 4px;">Flow State</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if stats:
        st.markdown("#### Page Registry Table")
        p_rows = []
        for src, s in stats.items():
            p_rows.append({
                "Filing Identifier": src,
                "Pages Processed": s["page_count"],
                "Vector Chunks": s["chunk_count"],
                "Storage Status": "Verified in Memory",
            })
        st.dataframe(pd.DataFrame(p_rows), use_container_width=True)
    else:
        st.info("No active corporate disclosures loaded yet.")


# ---------------------------------------------------------------------------
# SIDEBAR -- FLOATING CAPSULE NAVIGATION CONSOLE
# ---------------------------------------------------------------------------
with st.sidebar:
    # Avatar Profile Header (Clean, Glassmorphic)
    st.markdown(
        f"""
        <div class="sidebar-avatar-container">
            <div class="sidebar-avatar">U</div>
            <div class="sidebar-name">User</div>
            <a href="{HOME_PAGE_URL}" target="_self" class="sidebar-switch-pill">
                SWITCH TO HOME
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown('<div style="font-family: \'JetBrains Mono\'; font-size: 0.7rem; letter-spacing: 0.15em; color: #6B7280; text-transform: uppercase; margin-bottom: 8px;">API & MODEL</div>', unsafe_allow_html=True)

    with st.form("groq_api_key_form", clear_on_submit=False):
        raw_key = st.text_input(
            "Groq API Key",
            value=st.session_state.active_groq_api_key,
            type="password",
            help="API key from console.groq.com. The key is kept only for this browser session.",
        )
        apply_api_key = st.form_submit_button(
            "Apply Groq API Key",
            type="primary",
            use_container_width=True,
        )

    if apply_api_key:
        cleaned_key = raw_key.strip().strip("'").strip('"') if raw_key else ""
        if cleaned_key:
            st.session_state.active_groq_api_key = cleaned_key
            st.success("Groq API key applied for this session.")
        else:
            st.session_state.active_groq_api_key = ""
            st.warning("Enter a Groq API key before applying it.")

    groq_api_key = st.session_state.active_groq_api_key
    if groq_api_key:
        st.caption("Groq API key is active for this session.")

    selected_model = st.selectbox(
        "Inference Model",
        options=AVAILABLE_GROQ_MODELS,
        index=0,
        help="Select primary Groq model.",
    )

    st.markdown("---")
    st.markdown('<div style="font-family: \'JetBrains Mono\'; font-size: 0.7rem; letter-spacing: 0.15em; color: #6B7280; text-transform: uppercase; margin-bottom: 8px;">WORKSPACE PRESETS</div>', unsafe_allow_html=True)
    st.caption("Instantly load verified filings for Reliance, TCS, and Infosys:")

    demo_btn = st.button("Load Sample Filings", use_container_width=True, type="secondary")

    st.markdown("---")
    st.markdown('<div style="font-family: \'JetBrains Mono\'; font-size: 0.7rem; letter-spacing: 0.15em; color: #6B7280; text-transform: uppercase; margin-bottom: 8px;">CUSTOM UPLOADS</div>', unsafe_allow_html=True)
    st.caption(f"Upload PDF disclosures (up to {MAX_PDFS_ALLOWED} documents):")

    uploaded_files = st.file_uploader(
        "Select PDF filings",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload company financial filings in PDF format.",
    )
    fast_upload_mode = st.checkbox(
        "Fast indexing (recommended)",
        value=True,
        help="Uses the PDF text layer and skips slow table reconstruction. Turn this off only for filings whose financial tables are missing from extracted text.",
    )

    if uploaded_files and len(uploaded_files) > MAX_PDFS_ALLOWED:
        st.warning(f"Only the first {MAX_PDFS_ALLOWED} files will be processed.")
        uploaded_files = uploaded_files[:MAX_PDFS_ALLOWED]

    process_btn = st.button("Process & Index Uploads", type="primary", use_container_width=True)

    if st.session_state.processed_files:
        st.markdown("---")
        st.markdown('<div style="font-family: \'JetBrains Mono\'; font-size: 0.7rem; letter-spacing: 0.15em; color: #6B7280; text-transform: uppercase; margin-bottom: 8px;">ACTIVE VAULT</div>', unsafe_allow_html=True)
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

        progress_bar = st.progress(0, text="Preparing fast PDF ingestion...")
        total = len(uploaded_files)

        indexed_count = 0
        for i, pdf_file in enumerate(uploaded_files):
            if pdf_file.name in st.session_state.processed_files:
                continue

            is_valid, err_msg = validate_pdf_file(pdf_file)
            if not is_valid:
                st.error(f"Skipping '{pdf_file.name}': {err_msg}")
                continue

            mode_label = "fast text extraction" if fast_upload_mode else "text and tables"
            progress_bar.progress(i / total, text=f"Parsing {pdf_file.name} ({mode_label})...")
            try:
                def update_parse_progress(done_pages, total_pages):
                    document_progress = 0.5 * done_pages / max(total_pages, 1)
                    progress_bar.progress(
                        (i + document_progress) / total,
                        text=f"Parsing {pdf_file.name}: page {done_pages}/{total_pages} ({mode_label})...",
                    )

                pages = extract_pages_from_pdf(
                    pdf_file,
                    include_tables=not fast_upload_mode,
                    progress_callback=update_parse_progress,
                )
            except Exception as e:
                st.error(f"Failed to parse '{pdf_file.name}': {e}")
                continue

            if not pages:
                st.warning(f"'{pdf_file.name}' had no readable pages.")
                continue

            extracted_chars = sum(p["char_count"] for p in pages)
            if extracted_chars < 150:
                st.warning(f"'{pdf_file.name}' contains minimal extractable text.")

            progress_bar.progress((i + 0.5) / total, text=f"Preparing {pdf_file.name} for FAISS indexing...")
            chunks = chunk_pages(pages, source_name=pdf_file.name)
            if not chunks:
                st.warning(f"'{pdf_file.name}' did not produce indexable text chunks.")
                continue

            def update_index_progress(done_chunks, total_chunks):
                document_progress = 0.5 + 0.49 * done_chunks / max(total_chunks, 1)
                progress_bar.progress(
                    (i + document_progress) / total,
                    text=f"Indexing {pdf_file.name}: {done_chunks}/{total_chunks} chunks into FAISS...",
                )

            try:
                st.session_state.vector_store.add_chunks(
                    chunks,
                    progress_callback=update_index_progress,
                )
            except Exception as e:
                st.error(f"Failed to index '{pdf_file.name}' in FAISS: {e}")
                continue
            st.session_state.processed_files.append(pdf_file.name)
            indexed_count += 1

        progress_bar.progress(1.0, text="Indexing complete.")
        if indexed_count > 0:
            st.success(f"Successfully indexed {indexed_count} filing(s).")
            st.rerun()
        else:
            st.info("No new valid filings to index.")


# ---------------------------------------------------------------------------
# MAIN DASHBOARD INTERFACE (BENTO GRID DESIGN)
# ---------------------------------------------------------------------------

# Current Date String
current_date_str = datetime.datetime.now().strftime("%A, %B %d")

# Top Header: "Hello, User."
st.markdown(
    f"""
    <div class="bento-header-container">
        <div>
            <div class="bento-greeting">Hello, <span>User</span>.</div>
            <div class="bento-subtext">Your financial filing workspace is ready. Intelligence models active.</div>
        </div>
        <div class="bento-date-pill">
            {current_date_str}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# BENTO GRID METRICS SECTION (SPREAD OUT WITH POPUP TRIGGERS)
# ---------------------------------------------------------------------------
row1_col1, row1_col2, row1_col3 = st.columns([1.7, 1.15, 1.15])

doc_count = len(st.session_state.processed_files)
stats = st.session_state.vector_store.get_source_stats() if st.session_state.vector_store else {}
total_chunks = sum(s["chunk_count"] for s in stats.values())
total_pages = sum(s["page_count"] for s in stats.values())

with row1_col1:
    st.markdown(
        f"""
        <div class="bento-card bento-peach bento-card-1" style="min-height: 250px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div class="bento-title">Filing Shield</div>
                <div class="bento-desc">
                    Detect & analyze financial risk, operating margin shifts, and multi-company filing disclosures with RAG-powered accuracy.
                </div>
            </div>
            <div class="bento-link">
                ACTIVE VAULT: {doc_count} ENTERPRISE FILINGS &rarr;
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with row1_col2:
    st.markdown(
        f"""
        <div class="bento-card bento-navy bento-card-2" style="min-height: 250px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-family: 'JetBrains Mono'; font-size: 0.7rem; letter-spacing: 0.15em; color: #60A5FA; text-transform: uppercase;">VECTOR EMBEDDINGS</div>
                <div class="bento-title">{total_chunks} Vectors</div>
                <div class="bento-desc">FastEmbed + FAISS Index</div>
            </div>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.72rem; color: #A78BFA;">
                STATUS: READY
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("View Vector Health Report", key="btn_vector_modal", use_container_width=True):
        show_vector_modal(stats, total_chunks)

with row1_col3:
    st.markdown(
        f"""
        <div class="bento-card bento-navy bento-card-3" style="min-height: 250px; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-family: 'Space Grotesk'; font-size: 0.92rem; font-weight: 700; color: #FFFFFF;">Inner Progress</span>
                <span style="background: rgba(255, 255, 255, 0.1); color: #FFFFFF; font-size: 0.65rem; font-weight: 700; padding: 3px 10px; border-radius: 9999px; border: 1px solid rgba(255, 255, 255, 0.15);">FLOW STATE</span>
            </div>
            <div style="margin: 14px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #FF7B60;"></div>
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #FF7B60;"></div>
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #FF7B60;"></div>
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #FF7B60;"></div>
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #FF7B60;"></div>
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #FF7B60;"></div>
                </div>
                <div style="height: 2px; background: #FF7B60; width: 100%; border-radius: 2px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #9CA3AF; font-family: 'JetBrains Mono';">
                <span>ENERGY: 100%</span>
                <span>{total_pages} PAGES</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("View Filing Registry Report", key="btn_progress_modal", use_container_width=True):
        show_progress_modal(stats, total_pages, doc_count)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# MAIN WORKSPACE TABS (SPREAD OUT & FROSTED GLASS DESIGN)
# ---------------------------------------------------------------------------
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
    st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">Multi-Document Financial RAG</div>', unsafe_allow_html=True)
    st.caption("Submit queries across all active corporate disclosures. Every answer is grounded in retrieved chunks with exact page-level citations.")

    if not st.session_state.processed_files:
        st.info("Load sample filings from the sidebar or upload custom PDFs to begin.")
    else:
        # Quick preset buttons
        st.markdown('<div style="font-family: \'JetBrains Mono\'; font-size: 0.72rem; letter-spacing: 0.16em; color: #9CA3AF; text-transform: uppercase; margin-bottom: 8px;">PRESET QUERIES</div>', unsafe_allow_html=True)
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
                    with st.expander("Grounding Slips", expanded=False):
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

            if len(query_to_run) > MAX_QUERY_LENGTH:
                st.warning(f"Query truncated to maximum allowed {MAX_QUERY_LENGTH} characters.")
                query_to_run = query_to_run[:MAX_QUERY_LENGTH]

            if not groq_api_key:
                st.error("Enter your Groq API Key in the sidebar to execute LLM queries.")
            else:
                client = Groq(api_key=groq_api_key, timeout=GROQ_API_TIMEOUT_SECONDS)

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
                        with st.expander("Grounding Slips", expanded=False):
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
    st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">Standardized Comp Matrix</div>', unsafe_allow_html=True)
    st.caption("Automated extraction of standardized metrics with derived profit margins and capital structure ratios.")

    if not st.session_state.processed_files:
        st.info("Load sample filings or upload PDFs first to enable metric extraction.")
    else:
        extraction_mode = st.radio(
            "Extraction mode",
            ["Automatic (from filing text)", "Groq (cloud)", "Fine-tuned Flan-T5 (local)"],
            horizontal=True,
        )
        extract_all_btn = st.button("Extract Financial Metrics", type="primary")

        if extract_all_btn:
            if extraction_mode == "Groq (cloud)" and not groq_api_key:
                st.error("Enter your Groq API Key in the sidebar.")
            else:
                client = (
                    Groq(api_key=groq_api_key, timeout=GROQ_API_TIMEOUT_SECONDS)
                    if extraction_mode == "Groq (cloud)"
                    else None
                )
                extraction_completed = True
                for src in st.session_state.processed_files:
                    with st.spinner(f"Extracting metrics for {src}..."):
                        try:
                            if extraction_mode == "Automatic (from filing text)":
                                metrics = extract_metrics_from_vector_store(
                                    st.session_state.vector_store, src
                                )
                            elif client:
                                metrics = extract_metrics(
                                    client,
                                    st.session_state.vector_store,
                                    src,
                                    model=selected_model,
                                )
                            else:
                                # Import lazily so regular Groq sessions do not pay the
                                # PyTorch startup cost.
                                from backend.local_extractor import extract_metrics_locally
                                metrics = extract_metrics_locally(st.session_state.vector_store, src)
                        except FileNotFoundError as exc:
                            extraction_completed = False
                            st.error(f"Local model unavailable. Train it first, then retry. Details: {exc}")
                            break
                        ratios = compute_financial_ratios(metrics)
                        st.session_state.metrics_table[src] = metrics
                        st.session_state.ratios_table[src] = ratios
                if extraction_completed:
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
# TAB 3: LUMINOUS VISUAL ANALYTICS (PLOTLY)
# =========================================================================
with tab_charts:
    st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">Visual Analytics</div>', unsafe_allow_html=True)
    st.caption("Interactive visualizations benchmarking revenue scale, operating margins, and balance sheet solvency.")

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
                "Total Revenue": rev,
                "Net Profit": pat,
                "EBITDA": ebitda,
                "Operating Profit (EBIT)": ebit,
                "Total Assets": assets,
                "Total Debt": debt,
                "Operating Margin (%)": op_margin,
                "Net Profit Margin (%)": net_margin,
            })

        df_chart = pd.DataFrame(chart_rows)
        chart_metric_columns = [
            "Total Revenue",
            "Net Profit",
            "EBITDA",
            "Operating Profit (EBIT)",
            "Total Assets",
            "Total Debt",
            "Operating Margin (%)",
            "Net Profit Margin (%)",
        ]
        # A filing can legitimately omit a metric.  Convert all chart columns
        # together so Plotly receives a consistent numeric dtype; NaN values
        # are simply omitted from their respective bars/scatter points.
        df_chart[chart_metric_columns] = df_chart[chart_metric_columns].apply(
            pd.to_numeric, errors="coerce"
        )

        c_plot1, c_plot2 = st.columns(2)

        with c_plot1:
            fig_scale = px.bar(
                df_chart,
                x="Filing",
                y=["Total Revenue", "Net Profit", "EBITDA"],
                barmode="group",
                title="Revenue, EBITDA & Net Profit Scale",
                labels={"value": "Amount (Native Units)", "variable": "Metric"},
                color_discrete_sequence=["#FF7B60", "#FF4B72", "#F59E0B"],
            )
            fig_scale.update_layout(
                paper_bgcolor="#141212",
                plot_bgcolor="#141212",
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
                paper_bgcolor="#141212",
                plot_bgcolor="#141212",
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
                paper_bgcolor="#141212",
                plot_bgcolor="#141212",
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
                paper_bgcolor="#141212",
                plot_bgcolor="#141212",
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
    st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">Institutional Research Report</div>', unsafe_allow_html=True)
    st.caption("Comprehensive cross-company comparative synthesis synthesized by Groq Llama-3.3.")

    if not st.session_state.processed_files:
        st.info("Load filings first to synthesize executive research reports.")
    else:
        gen_exec_btn = st.button("Generate Executive Synthesis Report", type="primary")

        if gen_exec_btn:
            if not groq_api_key:
                st.error("Enter your Groq API Key in the sidebar.")
            else:
                client = Groq(api_key=groq_api_key, timeout=GROQ_API_TIMEOUT_SECONDS)
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
    st.markdown('<div style="font-family: \'Space Grotesk\'; font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">Document & Vector Index Inspector</div>', unsafe_allow_html=True)
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
