"""
test_e2e_pipeline.py
--------------------
End-to-end integration test verifying the complete pipeline:
PDF text & table extraction -> chunking -> vector indexing -> retrieval -> metrics parsing & ratios.
"""

import os
import pytest
from backend.config import DATA_DIR
from backend.pdf_parser import extract_pages_from_pdf
from backend.chunker import chunk_pages
from backend.vector_store import VectorStore
from backend.metrics_extractor import parse_numeric_value, compute_financial_ratios


def test_full_pipeline_on_sample_filings():
    sample_files = [
        os.path.join(DATA_DIR, "Reliance_Industries_Q1_FY25.pdf"),
        os.path.join(DATA_DIR, "TCS_Q1_FY25.pdf"),
        os.path.join(DATA_DIR, "Infosys_Q1_FY25.pdf"),
    ]

    # Verify all 3 sample PDFs exist
    for sf in sample_files:
        assert os.path.exists(sf), f"Missing sample filing: {sf}"

    # 1. Ingestion & Chunking
    vs = VectorStore()
    for sf in sample_files:
        doc_name = os.path.basename(sf)
        pages = extract_pages_from_pdf(sf)
        assert len(pages) >= 2, f"Expected at least 2 pages for {doc_name}"
        chunks = chunk_pages(pages, source_name=doc_name)
        assert len(chunks) >= 2, f"Expected at least 2 chunks for {doc_name}"
        vs.add_chunks(chunks)

    # 2. Vector Store indexing verification
    sources = vs.get_all_sources()
    assert len(sources) == 3
    stats = vs.get_source_stats()
    assert all(stats[s]["chunk_count"] > 0 for s in sources)

    # 3. Cross-Document Retrieval
    query = "What is the operating margin and revenue for TCS and Infosys?"
    results = vs.search(query, top_k=4)
    assert len(results) > 0
    retrieved_sources = {r["source"] for r in results}
    assert any("TCS" in s or "Infosys" in s for s in retrieved_sources)

    # 4. Source-Filtered Retrieval
    ril_results = vs.search("Oil to Chemicals segment revenue and EBITDA", top_k=3, source_filter="Reliance_Industries_Q1_FY25.pdf")
    assert len(ril_results) > 0
    assert all(r["source"] == "Reliance_Industries_Q1_FY25.pdf" for r in ril_results)
    assert any("Oil to Chemicals" in r["text"] or "O2C" in r["text"] or "Retail" in r["text"] for r in ril_results)

    # 5. Financial ratios computation check
    mock_extracted_ril = {
        "Total Revenue": "2,57,823",
        "Net Profit": "17,445",
        "EBITDA": "42,748",
        "Operating Profit (EBIT)": "29,152",
        "Total Assets": "18,42,150",
        "Total Debt": "3,32,450",
    }
    ratios = compute_financial_ratios(mock_extracted_ril)
    assert "Calculated Net Margin (%)" in ratios
    assert "Calculated Operating Margin (%)" in ratios
    assert "Debt to Total Assets" in ratios
    assert "6.77%" in ratios["Calculated Net Margin (%)"]
    assert ratios["Debt to Total Assets"] == "0.18x"
