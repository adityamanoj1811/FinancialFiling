"""
chunker.py
----------
Splits long extracted PDF text into smaller overlapping chunks tagged with
detailed metadata (source filing name, page number, chunk id, estimated token count).
"""

import re
from backend.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_pages(pages: list[dict], source_name: str) -> list[dict]:
    """
    Split a list of page objects (from pdf_parser.extract_pages_from_pdf) into
    overlapping chunks, preserving the exact page number metadata for citations.

    Parameters
    ----------
    pages : list of dicts with keys "page_number" and "text".
    source_name : human-readable name of the PDF document.

    Returns
    -------
    list[dict] : chunks with keys:
        - "text": str
        - "source": str
        - "page_number": int
        - "chunk_id": int
        - "char_count": int
        - "token_est": int (~char_count / 4)
    """
    chunks = []
    global_chunk_id = 0

    for page in pages:
        page_num = page.get("page_number", 1)
        text = page.get("text", "").strip()
        if not text:
            continue

        text_length = len(text)
        start = 0

        # If the whole page fits comfortably in one chunk, keep it intact
        if text_length <= CHUNK_SIZE:
            chunks.append({
                "text": text,
                "source": source_name,
                "page_number": page_num,
                "chunk_id": global_chunk_id,
                "char_count": text_length,
                "token_est": max(1, text_length // 4),
            })
            global_chunk_id += 1
            continue

        while start < text_length:
            end = min(start + CHUNK_SIZE, text_length)
            chunk_slice = text[start:end].strip()

            if chunk_slice:
                chunks.append({
                    "text": chunk_slice,
                    "source": source_name,
                    "page_number": page_num,
                    "chunk_id": global_chunk_id,
                    "char_count": len(chunk_slice),
                    "token_est": max(1, len(chunk_slice) // 4),
                })
                global_chunk_id += 1

            if end >= text_length:
                break

            start += (CHUNK_SIZE - CHUNK_OVERLAP)

    return chunks


def chunk_text(text: str, source_name: str) -> list[dict]:
    """
    Fallback chunking function for raw text strings with embedded [PAGE X] tags.
    """
    page_blocks = re.split(r"\[PAGE\s+(\d+)\]", text)
    chunks = []
    global_chunk_id = 0

    # If [PAGE X] delimiters are present
    if len(page_blocks) > 1:
        for i in range(1, len(page_blocks), 2):
            try:
                page_num = int(page_blocks[i])
            except ValueError:
                page_num = 1
            page_text = page_blocks[i + 1].strip() if (i + 1) < len(page_blocks) else ""
            if not page_text:
                continue

            page_chunks = chunk_pages([{"page_number": page_num, "text": page_text}], source_name)
            for c in page_chunks:
                c["chunk_id"] = global_chunk_id
                chunks.append(c)
                global_chunk_id += 1
        return chunks

    # Otherwise chunk raw text directly
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + CHUNK_SIZE, text_length)
        chunk_content = text[start:end].strip()

        if chunk_content:
            chunks.append({
                "text": chunk_content,
                "source": source_name,
                "page_number": 1,
                "chunk_id": global_chunk_id,
                "char_count": len(chunk_content),
                "token_est": max(1, len(chunk_content) // 4),
            })
            global_chunk_id += 1

        if end >= text_length:
            break

        start += (CHUNK_SIZE - CHUNK_OVERLAP)

    return chunks
