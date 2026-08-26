"""
test_rag_pipeline.py
---------------------
Unit tests for RAG prompt construction and message preparation.
"""

from backend.rag_pipeline import build_context_block, _prepare_messages


def test_build_context_block():
    chunks = [
        {"source": "Reliance.pdf", "page_number": 1, "text": "Reliance Q1 revenue was strong."},
        {"source": "Reliance.pdf", "page_number": 2, "text": "Reliance retail EBITDA grew."},
        {"source": "TCS.pdf", "page_number": 1, "text": "TCS EBIT margin reached 24.7%."},
    ]
    block = build_context_block(chunks)
    assert "### Source Document: Reliance.pdf" in block
    assert "### Source Document: TCS.pdf" in block
    assert "[Page 1]" in block
    assert "[Page 2]" in block


def test_prepare_messages_with_history():
    history = [
        {"role": "user", "content": "What is TCS's net profit?"},
        {"role": "assistant", "content": "TCS reported ₹12,040 crore net profit."},
    ]
    messages = _prepare_messages(
        question="How does their operating margin compare?",
        context_block="Sample context text",
        chat_history=history,
    )
    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"
    assert messages[3]["role"] == "user"
    assert "FILING CONTEXT:" in messages[3]["content"]
