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
GROQ_MODEL = "llama-3.1-70b-versatile"

AVAILABLE_GROQ_MODELS = [
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "llama-3.3-70b-versatile",
    "llama-3.3-70b-specdec",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

GROQ_FALLBACK_MODELS = [
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

# ---------------------------------------------------------------------------
# PDF CHUNKING & EMBEDDING CONFIGURATION
# ---------------------------------------------------------------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K_PER_DOCUMENT = 4

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
