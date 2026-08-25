<div align="center">

# 📊 Filing Insight
### Multi-Company Financial Filing Intelligence Platform

**Where Filings Become Intelligence. Decode. Discover. Decide.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.37%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Groq](https://img.shields.io/badge/Groq-LLM%20API-F55036?style=for-the-badge)](https://groq.com)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-0078D7?style=for-the-badge)](https://faiss.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## What Is This?

**Filing Insight** is an enterprise-grade, GenAI-powered financial intelligence platform that enables analysts, researchers, and investors to ingest multiple corporate financial filings — Quarterly Earnings Releases, Annual Reports, 10-Ks, BSE/NSE regulatory disclosures — and instantly extract structured intelligence from them.

The platform is composed of two parts:

| Layer | Tech | Purpose |
|---|---|---|
| **Landing Frontend** | React 18 + Vite + Framer Motion | Cinematic scroll-reveal landing page, portal zoom hero animation, glassmorphic UI, routes to the app |
| **Filing Insight App** | Python + Streamlit + RAG | The full intelligence dashboard — chat, metrics, charts, AI reports, vector explorer |

Built entirely with **free-tier and open tools**: Groq Cloud API (LLM inference), FAISS + fastembed (local CPU vector search), and Streamlit (financial terminal UI).

---

## Core Capabilities

### 💬 1. Multi-Document RAG Chat
Ask complex natural-language questions across **multiple company filings simultaneously**. The system retrieves the most relevant chunks from each document, builds a grounded context block, and streams a precise, citation-backed answer in real time.

- Multi-turn conversational memory (last 4 turns)
- Token-by-token streaming responses
- Page-level citations for every factual claim (e.g. `[TCS_Q1_FY25.pdf, Page 2]`)
- Cross-company comparison mode with markdown tables
- Quick-prompt presets for common financial queries
- Expandable Citation Inspector panel

### 2. Structured Metrics Comparison Table
Auto-extract a standardized set of financial metrics from every uploaded filing and display them in a side-by-side table.

**Extracted Metrics:**
- Total Revenue, Net Profit, EBITDA, Operating Profit (EBIT)
- Earnings Per Share (EPS)
- Operating Margin (%), Net Profit Margin (%)
- Total Assets, Total Liabilities, Total Debt, Cash & Liquid Investments
- Reporting Period

**Derived Ratios (auto-computed):**
- Calculated Net Margin (%)
- Calculated Operating / EBITDA Margin (%)
- Debt to Total Assets (x)

**Export formats:** CSV and Excel (`.xlsx`)

### 3. Interactive Visual Financial Analytics
Rich, interactive [Plotly](https://plotly.com) charts for instant visual comparison:

- **Revenue & Profit Scale Chart** — grouped bar chart comparing absolute revenue and net profit across companies
- **Margin Comparison Chart** — operating and net profit margin benchmarking
- **Cost Structure Breakdown** — revenue vs. profit waterfall visualization
- **Balance Sheet Solvency** — assets, liabilities, and debt stacked comparison

### 4. Institutional Executive Research Report
One-click AI-generated comparative research report, synthesized by the Groq LLM from all loaded filings. Structured like an institutional equity research note:

1. Executive Summary & Comparative Overview
2. Financial Performance & Margin Analysis
3. Balance Sheet Health & Solvency Matrix
4. Strategic Growth Vectors & Technology Initiatives
5. Key Risks & Sector Headwinds
6. Institutional Analyst Verdict

**Export:** Full Markdown export (`.md`)

### 5. Document & FAISS Vector Index Explorer
Audit and inspect the underlying RAG pipeline state:

- **Document Registry Table** — pages indexed, chunks generated, character count, estimated tokens per filing
- **Vector Vault Modal** — total active vectors, embedding architecture details (BAAI/bge-small-en-v1.5, 384 dimensions), FAISS index type
- **Chunk Inspector** — browse all chunks for any document, filter by keyword, inspect raw text and metadata (page number, char count, estimated tokens)
- **Filing Vault Modal** — active document count, total processed pages, ingestion status

---

## Architecture

```
                              User (Browser)
                                    │
              ┌─────────────────────┴──────────────────────┐
              │                                             │
              ▼                                             ▼
 ┌────────────────────────┐             ┌───────────────────────────────────────────┐
 │  frontend/ (React/Vite) │             │     filing-insight/ (Streamlit App)        │
 │                         │             │                                            │
 │  Cinematic landing page │  ─────────▶ │  app.py — Bento-Grid Dashboard UI         │
 │  Scroll portal animation│  localhost  │  ├── Floating Capsule Sidebar              │
 │  Glassmorphic CTA button│  :8501      │  ├── Tab 1: 💬 RAG Chat (streaming)        │
 │  Framer Motion hero     │             │  ├── Tab 2: 📊 Comp Table + Ratios         │
 │  "Know Da Numbers"      │             │  ├── Tab 3: 📈 Plotly Visual Analytics     │
 └────────────────────────┘             │  ├── Tab 4: 📑 Executive AI Report         │
        localhost:3000                  │  └── Tab 5: 🔍 Document/Vector Explorer    │
                                        └──────────────────┬────────────────────────┘
                                                           │ Pure Python calls
                                                           ▼
                                        ┌──────────────────────────────────────────┐
                                        │         backend/ (Logic & Pipeline)       │
                                        │                                           │
                                        │  pdf_parser.py      → PDF extraction      │
                                        │  chunker.py         → Overlapping chunks  │
                                        │  vector_store.py    → FAISS + fastembed   │
                                        │  rag_pipeline.py    → Streaming RAG       │
                                        │  metrics_extractor.py → JSON + ratios     │
                                        │  config.py          → Central config      │
                                        └──────────────────┬────────────────────────┘
                                                           │ HTTPS (streaming)
                                                           ▼
                                                ┌─────────────────────┐
                                                │   Groq Cloud API    │
                                                │  (LLM Inference)    │
                                                │  Multiple models    │
                                                │  with auto-fallback │
                                                └─────────────────────┘
```

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- A free [Groq API key](https://console.groq.com/keys)

---

### 1. Clone the Repository

```bash
git clone https://github.com/adityamanoj1811/FinancialFiling.git
cd FinancialFiling
```

---

### 2. Set Up the Backend (Filing Insight App)

```bash
cd filing-insight

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# Install all Python dependencies
pip install -r requirements.txt
```

**Configure your API Key** — create a `.env` file in the `filing-insight/` directory:

```bash
echo 'GROQ_API_KEY=gsk_your_key_here' > .env
```

>  Get your free Groq API key at [console.groq.com/keys](https://console.groq.com/keys)

**Generate Sample Filing PDFs** (optional — for demo mode):
```bash
python data/generate_sample_filings.py
```
This creates three realistic Q1 FY25 financial filing PDFs:
- `data/Reliance_Industries_Q1_FY25.pdf`
- `data/TCS_Q1_FY25.pdf`
- `data/Infosys_Q1_FY25.pdf`

**Start the Streamlit app:**
```bash
streamlit run app.py
```
→ App runs at **http://localhost:8501**

---

### 3. Set Up the Frontend (Landing Page)

Open a new terminal:

```bash
cd FinancialFiling/frontend

# Install dependencies
npm install

# Start the Vite dev server
npm run dev
```
→ Landing page runs at **http://localhost:3000**

---

### 4. Demo Mode (Zero-Setup Evaluation)

1. Open **http://localhost:8501** directly, or navigate to it via the landing page.
2. Paste your Groq API key in the sidebar (or set it in `.env` beforehand).
3. Click **"Load Sample Filings (Demo)"** in the sidebar.
4. Instantly try:
   - Pre-built quick prompts like *"Compare Total Revenue, Net Profit, and EPS across all filings."*
   - Auto-extracting the structured Comp Table with derived financial ratios.
   - Exploring dynamic Plotly charts and generating the Executive AI Report.

---

## 📂 Repository Structure

```
FinancialFiling/
│
├── frontend/                          # React + Vite cinematic landing page
│   ├── src/
│   │   ├── App.jsx                    # Scroll-reveal portal hero, glassmorphic CTA
│   │   ├── main.jsx                   # React entry point
│   │   └── index.css                  # Global styles
│   ├── public/
│   │   └── assets/
│   │       └── hero-bg.jpg            # Hero background image
│   ├── index.html
│   ├── vite.config.js                 # Vite config (port 3000, host true)
│   ├── tailwind.config.js             # Tailwind CSS config
│   ├── postcss.config.js
│   └── package.json
│
└── filing-insight/                    # Python Streamlit intelligence app
    ├── app.py                         # Main UI: Bento-grid dashboard (1354 lines)
    ├── requirements.txt               # Python dependencies
    ├── pytest.ini                     # Pytest config
    ├── .env.example                   # Environment variable template
    │
    ├── backend/                       # Core logic & ML pipeline
    │   ├── __init__.py
    │   ├── config.py                  # Central config: models, metrics, limits
    │   ├── pdf_parser.py              # PDF text + markdown table extraction
    │   ├── chunker.py                 # Overlapping chunker with page metadata
    │   ├── vector_store.py            # FAISS index + fastembed ONNX embeddings
    │   ├── rag_pipeline.py            # Streaming RAG + multi-turn history
    │   └── metrics_extractor.py      # Metric JSON extraction + ratios + reports
    │
    ├── data/                          # Sample filing PDFs
    │   ├── generate_sample_filings.py # PDF generator script
    │   ├── Reliance_Industries_Q1_FY25.pdf
    │   ├── TCS_Q1_FY25.pdf
    │   └── Infosys_Q1_FY25.pdf
    │
    └── tests/                         # Automated test suite (pytest)
        ├── test_pdf_parser.py
        ├── test_chunker.py
        ├── test_vector_store.py
        ├── test_metrics_extractor.py
        ├── test_rag_pipeline.py
        ├── test_e2e_pipeline.py
        └── test_groq_live.py
```

---

## 🧠 Technical Deep-Dive

### PDF Processing Pipeline

```
PDF Upload / File Path
        │
        ▼
  pdf_parser.py
  ├── pdfplumber extracts page-by-page text
  ├── Tables detected & converted to Markdown format
  ├── Combined: [narrative text] + [STRUCTURED TABLES]
  └── Returns: List[{page_number, text, raw_narrative, tables, char_count}]
        │
        ▼
  chunker.py
  ├── Pages ≤ 1000 chars → kept as single chunk
  ├── Longer pages → split with 150-char overlap
  └── Each chunk tagged: {text, source, page_number, chunk_id, char_count, token_est}
        │
        ▼
  vector_store.py
  ├── fastembed: BAAI/bge-small-en-v1.5 (384-dim ONNX, runs on CPU/Metal)
  ├── L2-normalized vectors → FAISS IndexFlatIP (exact cosine similarity)
  └── Metadata store: parallel list to FAISS index
```

### RAG Query Pipeline

```
User Question
      │
      ▼
retrieve_relevant_chunks()
├── For each active source → vector_store.search(top_k=4 per doc)
└── Over-fetches (5x) when source-filtering; re-ranks to top_k
      │
      ▼
build_context_block()
└── Groups chunks by source, labels with [Page N], joins with ---
      │
      ▼
_prepare_messages()
├── System prompt: Senior financial analyst persona
├── Last 4 turns from chat history (multi-turn memory)
└── User prompt: FILING CONTEXT + USER QUESTION
      │
      ▼
Groq API (streaming)
├── Primary model → fallback chain if unavailable
└── Token-by-token yield → real-time UI streaming
      │
      ▼
Final yield: {__metadata__, sources_used, chunks_used, context_block}
```

### Metric Extraction Pipeline

```
For each indexed filing:
      │
      ▼
_find_most_relevant_chunks_for_metrics()
└── 7 targeted probe queries (revenue, PAT, EBITDA, EPS, assets, liabilities, ratios)
      │
      ▼
Groq LLM (temperature=0.0, JSON mode)
└── Extracts 12 standardized metrics → pure JSON dict
      │
      ▼
compute_financial_ratios()
├── Net Margin = Net Profit / Revenue × 100
├── Operating Margin = EBIT / Revenue × 100
└── Debt-to-Assets = Total Debt / Total Assets
      │
      ▼
Side-by-side Pandas DataFrame → Streamlit table + CSV/Excel export
```

### Embedding & Vector Search

| Property | Value |
|---|---|
| **Embedding model** | `BAAI/bge-small-en-v1.5` |
| **Embedding dimensions** | 384 |
| **Inference** | Local ONNX (CPU / Apple Metal) via fastembed |
| **Index type** | `FAISS IndexFlatIP` (exact, not approximate) |
| **Similarity metric** | Cosine (L2-normalized inner product) |
| **Chunk size** | 1000 characters |
| **Chunk overlap** | 150 characters |
| **Retrieval** | Top-4 per document (configurable) |

---

## 🛠️ Tech Stack

### Backend
| Library | Version | Role |
|---|---|---|
| `streamlit` | ≥1.37 | Web framework & UI rendering |
| `groq` | ≥0.9 | LLM inference (Groq Cloud) |
| `pdfplumber` | ≥0.11 | PDF text & table extraction |
| `faiss-cpu` | ≥1.8 | Vector similarity search index |
| `fastembed` | ≥0.3 | Local ONNX embedding inference |
| `pandas` | ≥2.2 | Data manipulation & tabular display |
| `plotly` | ≥5.24 | Interactive financial charts |
| `numpy` | ≥1.26 | Vector math & normalization |
| `scikit-learn` | ≥1.5 | Supplementary ML utilities |
| `openpyxl` | ≥3.1 | Excel export |
| `reportlab` + `fpdf2` | ≥4.2 / ≥2.8 | PDF generation |
| `python-dotenv` | ≥1.0 | `.env` configuration loading |
| `pytest` | ≥8.0 | Automated testing |

### Frontend
| Library | Version | Role |
|---|---|---|
| `react` | 18.3 | UI framework |
| `vite` | 5.4 | Build tool & dev server |
| `framer-motion` | 11.18 | Scroll-driven animations & spring physics |
| `tailwindcss` | 3.4 | Utility-first styling |
| `lucide-react` | 0.474 | Icon system |
| `clsx` + `tailwind-merge` | latest | Conditional class composition |

### AI / ML
| Component | Details |
|---|---|
| **LLM** | Groq Cloud — multiple models with auto-fallback (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `groq/compound-mini`, `allam-2-7b`) |
| **Embeddings** | BAAI/bge-small-en-v1.5 via fastembed (runs fully locally, zero API cost) |
| **Vector Index** | FAISS IndexFlatIP with L2 normalization (exact cosine similarity) |
| **PDF Parsing** | pdfplumber — extracts both narrative text and structured tables, converts tables to Markdown |

---

## 🧪 Automated Tests

Run the full test suite:

```bash
cd filing-insight
source .venv/bin/activate
pytest -v
```

| Test File | Coverage |
|---|---|
| `test_pdf_parser.py` | PDF text & markdown table extraction, file validation, magic bytes check |
| `test_chunker.py` | Overlapping chunking, page metadata attribution, edge cases |
| `test_vector_store.py` | FAISS indexing, cosine similarity search, source filtering, document deletion |
| `test_metrics_extractor.py` | Numeric string parsing, financial ratio calculation |
| `test_rag_pipeline.py` | Context block building, multi-turn history prompt construction |
| `test_e2e_pipeline.py` | End-to-end pipeline integration: parse → chunk → embed → retrieve |
| `test_groq_live.py` | Live Groq API connectivity & streaming (requires valid API key) |

---

## UI Design System

### Filing Insight App (Streamlit)
- **Fonts:** Plus Jakarta Sans (body), Space Grotesk (headings), JetBrains Mono (monospace/captions)
- **Design Language:** Premium dark theme with glassmorphism — frosted glass panels, soft glowing borders, backdrop-blur
- **Layout:** Custom bento-grid with click-to-expand modals
- **Sidebar:** Floating capsule navigation with avatar, "Switch to Home" pill, API key input, model selector, file uploader
- **Interactive Modals:**
  - **Vector Embeddings modal** — live FAISS vault status, chunk distribution table
  - **Inner Progress modal** — document registry, active vaults count, processed pages

### Landing Frontend (React/Vite)
- **Animation:** Framer Motion scroll-driven portal zoom — a circle mask expands to fill the viewport as the user scrolls
- **Spring physics:** `stiffness: 90, damping: 25` for natural, fluid feel
- **Typography:** Display headline — *"Where Filings Become Intelligence."*
- **Subtitle:** *"Decode. Discover. Decide."*
- **CTA Button:** Glassmorphic pill with amber accent icons, slides up on scroll, routes to `http://localhost:8501`
- **Branding:** "Know Da Numbers" top-left wordmark

---

## Security & Validation

| Guard | Details |
|---|---|
| **PDF magic bytes check** | Validates `%PDF` file signature before processing |
| **File size limit** | Max 50 MB per uploaded PDF |
| **Max PDFs** | 6 documents per session |
| **Query length** | Max 2000 characters per chat query |
| **API timeout** | 90-second timeout on all Groq API calls |
| **API key isolation** | Key stored in `.env`, never committed — use `.env.example` as template |

---

## ☁️ Deployment

### Streamlit Community Cloud (Backend App)

1. Push your repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Connect your repo and set the entry point to `filing-insight/app.py`.
4. Under **Settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
5. Deploy — your app gets a public shareable URL instantly.

### Frontend (Vercel / Netlify)

```bash
cd frontend
npm run build
# dist/ folder is ready for static deployment
```

Upload `frontend/dist/` to Vercel, Netlify, or any static host. Update the CTA button URL in `App.jsx` to point to your deployed Streamlit URL.

---

## 🗺️ Sample Financial Questions to Try

Once filings are loaded, try these in the RAG Chat:

- *"Compare the Total Revenue, Net Profit, and EPS across all filings."*
- *"Which company achieved higher operating margins and profitability efficiency?"*
- *"Compare balance sheet strength, liquid cash reserves, and debt obligations."*
- *"What are the primary business segments and growth drivers described?"*
- *"What are the key risk factors and macroeconomic headwinds noted by management?"*
- *"What artificial intelligence (AI/GenAI) initiatives or platforms were highlighted?"*

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

<div align="center">

**Built with ❤️ using Groq, FAISS, Streamlit, React & Framer Motion**

*For questions, feature requests, or contributions — open an issue or pull request.*

</div>
