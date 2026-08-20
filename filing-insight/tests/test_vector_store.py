"""
test_vector_store.py
---------------------
Unit and integration tests for VectorStore with FastEmbed + FAISS.
"""

from backend.vector_store import VectorStore


def test_vector_store_add_and_search():
    vs = VectorStore()
    sample_chunks = [
        {"text": "TCS reported consolidated revenue of 62,613 crore in Q1 FY25.", "source": "TCS.pdf", "page_number": 1, "chunk_id": 0},
        {"text": "Reliance reported gross revenue of 2,57,823 crore driven by retail and oil.", "source": "Reliance.pdf", "page_number": 1, "chunk_id": 1},
        {"text": "Infosys achieved operating margin of 21.1% in Q1.", "source": "Infosys.pdf", "page_number": 1, "chunk_id": 2},
    ]
    vs.add_chunks(sample_chunks)

    assert vs.index.ntotal == 3
    sources = vs.get_all_sources()
    assert "TCS.pdf" in sources
    assert "Reliance.pdf" in sources
    assert "Infosys.pdf" in sources

    # Search for TCS revenue
    results = vs.search("What is TCS revenue?", top_k=2)
    assert len(results) > 0
    assert results[0]["source"] == "TCS.pdf"

    # Search with source filter
    filtered_results = vs.search("revenue", top_k=2, source_filter="Infosys.pdf")
    assert len(filtered_results) > 0
    assert all(r["source"] == "Infosys.pdf" for r in filtered_results)


def test_vector_store_stats_and_removal():
    vs = VectorStore()
    sample_chunks = [
        {"text": "Chunk A1", "source": "DocA.pdf", "page_number": 1, "chunk_id": 0, "char_count": 8, "token_est": 2},
        {"text": "Chunk A2", "source": "DocA.pdf", "page_number": 2, "chunk_id": 1, "char_count": 8, "token_est": 2},
        {"text": "Chunk B1", "source": "DocB.pdf", "page_number": 1, "chunk_id": 2, "char_count": 8, "token_est": 2},
    ]
    vs.add_chunks(sample_chunks)

    stats = vs.get_source_stats()
    assert "DocA.pdf" in stats
    assert stats["DocA.pdf"]["chunk_count"] == 2
    assert stats["DocA.pdf"]["page_count"] == 2
    assert stats["DocB.pdf"]["chunk_count"] == 1

    # Remove DocA
    vs.remove_source("DocA.pdf")
    assert vs.get_all_sources() == ["DocB.pdf"]
    assert vs.index.ntotal == 1
