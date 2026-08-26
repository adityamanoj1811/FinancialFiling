"""
test_pdf_parser.py
-------------------
Unit tests for PDF text & structured table extraction.
"""

import os
import io
import pytest
from backend.pdf_parser import (
    extract_text_from_pdf,
    extract_pages_from_pdf,
    validate_extracted_text,
    validate_pdf_file,
    _format_table_to_markdown,
)
from backend.config import DATA_DIR, MAX_PDF_SIZE_BYTES


def test_format_table_to_markdown():
    table = [
        ["Metric", "FY25", "FY24"],
        ["Revenue", "1000", "900"],
        ["Net Profit", "200", "180"],
    ]
    md = _format_table_to_markdown(table)
    assert "| Metric | FY25 | FY24 |" in md
    assert "| Revenue | 1000 | 900 |" in md
    assert "| Net Profit | 200 | 180 |" in md


def test_validate_extracted_text():
    assert validate_extracted_text("A" * 200, min_chars=150) is True
    assert validate_extracted_text("Short text", min_chars=150) is False


def test_validate_pdf_file_valid():
    valid_pdf_bytes = b"%PDF-1.4 sample content"
    is_valid, err = validate_pdf_file(valid_pdf_bytes)
    assert is_valid is True
    assert err == ""


def test_validate_pdf_file_invalid_signature():
    fake_file_bytes = b"<html><head></head><body>Not a PDF</body></html>"
    is_valid, err = validate_pdf_file(fake_file_bytes)
    assert is_valid is False
    assert "missing %PDF" in err or "signature" in err


def test_validate_pdf_file_oversized():
    oversized_bytes = b"%PDF" + b"0" * (MAX_PDF_SIZE_BYTES + 100)
    is_valid, err = validate_pdf_file(oversized_bytes)
    assert is_valid is False
    assert "exceeds maximum allowed limit" in err


def test_extract_from_sample_pdf():
    sample_pdf = os.path.join(DATA_DIR, "TCS_Q1_FY25.pdf")
    if not os.path.exists(sample_pdf):
        pytest.skip("Sample PDF not found, skipping extraction test.")

    is_valid, err = validate_pdf_file(sample_pdf)
    assert is_valid is True

    pages = extract_pages_from_pdf(sample_pdf)
    assert len(pages) >= 2
    assert pages[0]["page_number"] == 1
    assert "TATA CONSULTANCY SERVICES" in pages[0]["text"]
    assert len(pages[0]["text"]) > 100

    full_text = extract_text_from_pdf(sample_pdf)
    assert "[PAGE 1]" in full_text
    assert "Operating Margin" in full_text
