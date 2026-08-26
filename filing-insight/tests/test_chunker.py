"""
test_chunker.py
----------------
Unit tests for document chunking and metadata attribution.
"""

from backend.chunker import chunk_pages, chunk_text


def test_chunk_pages_preserves_page_numbers():
    pages = [
        {"page_number": 1, "text": "This is page 1 content. " * 50},
        {"page_number": 2, "text": "This is page 2 content. " * 50},
    ]
    chunks = chunk_pages(pages, source_name="Test_Doc.pdf")

    assert len(chunks) > 0
    page_numbers = {c["page_number"] for c in chunks}
    assert 1 in page_numbers
    assert 2 in page_numbers
    assert all(c["source"] == "Test_Doc.pdf" for c in chunks)
    assert all("token_est" in c for c in chunks)


def test_chunk_text_fallback():
    raw_text = "[PAGE 1]\nPage 1 intro.\n\n[PAGE 2]\nPage 2 details."
    chunks = chunk_text(raw_text, source_name="Report.pdf")

    assert len(chunks) >= 2
    assert chunks[0]["page_number"] == 1
    assert chunks[1]["page_number"] == 2
    assert chunks[0]["source"] == "Report.pdf"
