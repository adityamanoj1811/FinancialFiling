# 📊 Filing Insight — Multi-Company Financial Filing Analyzer

An enterprise-grade, GenAI-powered financial intelligence application that allows analysts, researchers, and investors to ingest multiple corporate financial filings (Quarterly Earnings Releases, Annual Reports, 10-Ks, BSE/NSE regulatory disclosures) and:

1. **Chat with Filings using Multi-Document RAG**: Ask complex natural-language comparison questions across several companies with real-time streaming answers, multi-turn conversational context, and verifiable page-level citations.
2. **Auto-Extract Structured Comparison Tables**: Extract standardized metrics (Revenue, Net Profit, EBITDA, EBIT, EPS, Assets, Liabilities, Debt) alongside automated financial ratios (Net Margin %, Operating Margin %, Debt-to-Assets).
3. **Interactive Visual Financial Analytics**: Compare company scales, profit margins, cost structures, and balance sheet solvency with rich, interactive Plotly charts.
4. **Institutional Executive Research Reports**: Generate one-click comparative research summaries synthesized by Groq Llama-3.3.
5. **Document & FAISS Vector Explorer**: Audit parsed page structures, chunk distributions, relevance scores, and vector embeddings.

Built entirely with free-tier and open tools: **Groq Cloud API** (Llama-3.3 70B LLM inference), **FAISS + fastembed** (local CPU ONNX vector semantic search), and **Streamlit** (modern financial terminal UI).

---

## 🏗️ Architecture

```
                                  User (Browser)
                                        │
                                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               app.py (Streamlit Frontend)                              │
│  - Modern Financial Terminal UI with Custom CSS Design System                          │
│  - 1-Click "Load Sample Filings" Demo Mode (Reliance, TCS, Infosys)                    │
│  - Tab 1: 💬 Streaming Multi-Turn RAG Chat with Citation Inspector                     │
│  - Tab 2: 📊 Structured Metrics Comp Table + Derived Ratios (CSV & Excel Export)       │
│  - Tab 3: 📈 Interactive Plotly Visual Analytics (Scale, Margins, Solvency)            │
│  - Tab 4: 📑 Institutional Executive Comparative Report (Markdown Export)              │
│  - Tab 5: 🔍 Document & FAISS Chunk Explorer                                           │
└───────────────────────────────────────┬────────────────────────────────────────────────┘
                                        │ Pure Python Function Calls
                                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               backend/ (Logic & Pipeline Layer)                         │
│                                                                                        │
│  pdf_parser.py        → Extracts page-by-page text & structured markdown tables        │
│  chunker.py           → Overlapping chunks with exact page-number metadata attribution │
│  vector_store.py      → Local fastembed ONNX embeddings + FAISS cosine index           │
│  rag_pipeline.py      → Streaming generation, multi-turn history & grounding prompts   │
│  metrics_extractor.py → Structured JSON extraction, ratio calculation & AI reports     │
│  config.py            → Central configuration, financial metrics schema & presets      │
└───────────────────────────────────────┬────────────────────────────────────────────────┘
                                        │ HTTPS API (Streaming & Non-Streaming)
                                        ▼
                              ┌───────────────────┐
                              │  Groq Cloud API   │ (Llama-3.3-70B-Versatile)
                              └───────────────────┘
```

---

## ⚡ Quick Start

### Local Home → Dashboard Flow

Run the landing page and the dashboard in separate terminals:

```bash
# Terminal 1 - Home page
cd frontend
npm run dev

# Terminal 2 - Dashboard
cd filing-insight
.venv/bin/streamlit run app.py
```

Open `http://localhost:5173`. The **File Your Insights** button opens the
dashboard at `http://localhost:8501`, and **Switch to Home** returns to the
landing page. For deployment, set `VITE_FILING_INSIGHT_URL` for the landing
page and `FILING_INSIGHT_HOME_URL` for the dashboard.

### 1. Set Up Environment & Install Dependencies
```bash
# Clone the repository
git clone <repo-url>
cd filing-insight

# Create and activate a Python 3.10+ virtual environment
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install all requirements
pip install -r requirements.txt
```

### 2. Generate or Inspect Sample Filings
We provide a built-in generator that creates 3 realistic financial filing PDFs in `data/`:
```bash
python data/generate_sample_filings.py
```
This generates:
- `data/Reliance_Industries_Q1_FY25.pdf`
- `data/TCS_Q1_FY25.pdf`
- `data/Infosys_Q1_FY25.pdf`

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```

### 4. Demo Mode (Zero-Setup Evaluation)
1. Paste your free Groq API key in the sidebar (or set `export GROQ_API_KEY="gsk_..."`).
2. Click **"🚀 Load Sample Filings (Demo)"** in the sidebar.
3. Instantly test:
   - Clicking quick prompts like *"Compare the Total Revenue, Net Profit, and EPS across all filings"*.
   - Extracting the standardized side-by-side Comp Table.
   - Exploring the dynamic Plotly charts and generating the Executive AI Report.

---

## 🧪 Automated Testing

Run the automated test suite with pytest:
```bash
pytest -v
```

Tests cover:
- PDF text & table markdown extraction (`test_pdf_parser.py`)
- Overlapping chunking and page metadata attribution (`test_chunker.py`)
- FAISS vector indexing, similarity search & document deletion (`test_vector_store.py`)
- Numeric string parsing & financial ratio calculations (`test_metrics_extractor.py`)
- RAG context preparation & multi-turn history prompts (`test_rag_pipeline.py`)

---

## 📂 Project Structure

```
filing-insight/
├── app.py                      # Modern Streamlit UI & Visual Dashboard
├── requirements.txt            # Project dependencies
├── pytest.ini                  # Pytest configuration
├── README.md                   # Complete documentation & methodology
├── backend/
│   ├── __init__.py
│   ├── config.py                # Constants, metric schemas, query presets
│   ├── pdf_parser.py            # PDF text & table extraction with page tagging
│   ├── chunker.py               # Overlapping chunker with metadata attribution
│   ├── vector_store.py          # FastEmbed + FAISS index & doc stats
│   ├── rag_pipeline.py          # Streaming RAG, multi-turn history & citations
│   └── metrics_extractor.py     # JSON metric extraction, ratios & executive report
├── data/
│   ├── generate_sample_filings.py # Script generating sample filing PDFs
│   ├── Reliance_Industries_Q1_FY25.pdf
│   ├── TCS_Q1_FY25.pdf
│   └── Infosys_Q1_FY25.pdf
└── tests/
    ├── test_pdf_parser.py
    ├── test_chunker.py
    ├── test_vector_store.py
    ├── test_metrics_extractor.py
    └── test_rag_pipeline.py
```

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push your repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Connect your repository and select `app.py` as the entry point.
4. Under **Settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
5. Deploy! Your app is live with a shareable URL.
