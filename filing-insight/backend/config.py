"""
config.py
---------
Central configuration file for the Filing Insight application.
Clean, professional settings for institutional financial intelligence.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file automatically if present
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ---------------------------------------------------------------------------
# GROQ API CONFIGURATION
# ---------------------------------------------------------------------------
GROQ_API_KEY_ENV_VAR = "GROQ_API_KEY"

# Primary & Available Groq models
GROQ_MODEL = "openai/gpt-oss-120b"

AVAILABLE_GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "groq/compound-mini",
    "allam-2-7b",
]

GROQ_FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "groq/compound-mini",
    "allam-2-7b",
]

# ---------------------------------------------------------------------------
# PDF CHUNKING & EMBEDDING CONFIGURATION
# ---------------------------------------------------------------------------
# Larger chunks materially reduce the number of local embedding calls for long
# filings while still preserving page-level citations.
CHUNK_SIZE = 2400
CHUNK_OVERLAP = 240
TOP_K_PER_DOCUMENT = 4
# Keep each ONNX inference unit small enough for long annual reports.  This also
# gives the UI a chance to report useful progress between FAISS additions.
EMBEDDING_BATCH_SIZE = 8
# Let ONNX use one worker.  On macOS this avoids contention with FAISS/OpenMP
# and prevents the native recursive-mutex failure seen with automatic threads.
EMBEDDING_THREADS = 1

# FastEmbed ONNX embedding model (lightweight, runs locally on CPU / Metal)
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# ---------------------------------------------------------------------------
# FINANCIAL METRICS TO EXTRACT
# ---------------------------------------------------------------------------
FINANCIAL_METRICS = [
    "Total Revenue",
    "Net Profit",
    "EBITDA",
    "Operating Profit (EBIT)",
    "Earnings Per Share (EPS)",
    "Operating Margin (%)",
    "Net Profit Margin (%)",
    "Total Assets",
    "Total Liabilities",
    "Total Debt",
    "Cash & Liquid Investments",
    "Reporting Period",
]

NUMERICAL_CHART_METRICS = [
    "Total Revenue",
    "Net Profit",
    "EBITDA",
    "Operating Profit (EBIT)",
    "Operating Margin (%)",
    "Net Profit Margin (%)",
]

# ---------------------------------------------------------------------------
# SAMPLE PROMPT PRESETS FOR CHAT (CLEAN - NO EMOJIS)
# ---------------------------------------------------------------------------
SAMPLE_QUERIES = [
    "Compare Total Revenue, Net Profit, and EPS across all filings.",
    "Which company achieved higher operating margins and profitability efficiency?",
    "Compare balance sheet strength, liquid cash reserves, and debt obligations.",
    "What are the primary business segments and growth drivers described?",
    "What are the key risk factors and macroeconomic headwinds noted by management?",
    "What artificial intelligence (AI/GenAI) initiatives or platforms were highlighted?",
]

# ---------------------------------------------------------------------------
# SAMPLE FILINGS METADATA
# ---------------------------------------------------------------------------
SAMPLE_FILINGS = [
    {
        "filename": "Reliance_Industries_Q1_FY25.pdf",
        "company": "Reliance Industries Limited",
        "period": "Q1 FY25",
        "description": "Conglomerate (O2C, Retail, Telecom Jio, Oil & Gas)",
    },
    {
        "filename": "TCS_Q1_FY25.pdf",
        "company": "Tata Consultancy Services Limited",
        "period": "Q1 FY25",
        "description": "IT & Consulting Leader (BFSI, Cloud, AI WisdomNext)",
    },
    {
        "filename": "Infosys_Q1_FY25.pdf",
        "company": "Infosys Limited",
        "period": "Q1 FY25",
        "description": "Digital Services & Consulting (Topaz GenAI, Cloud)",
    },
]

# ---------------------------------------------------------------------------
# APP-WIDE SETTINGS
# ---------------------------------------------------------------------------
MAX_PDFS_ALLOWED = 6
APP_TITLE = "Filing Insight | Multi-Company Financial Filing Analyzer"
APP_SUBTITLE = "Institutional Financial RAG, Comparative Analytics & Structured Disclosures"
# React/Vite landing page URL used by the dashboard's return navigation.
HOME_PAGE_URL = os.environ.get("FILING_INSIGHT_HOME_URL", "http://localhost:5173")

# ---------------------------------------------------------------------------
# SECURITY & VALIDATION SETTINGS
# ---------------------------------------------------------------------------
MAX_PDF_SIZE_MB = 50                  # Max size per uploaded PDF (bytes check in app)
MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024
MAX_QUERY_LENGTH = 2000               # Max characters allowed in a chat query
GROQ_API_TIMEOUT_SECONDS = 90        # Timeout for all Groq API calls
PDF_MAGIC_BYTES = b"%PDF"            # First 4 bytes of a valid PDF file
