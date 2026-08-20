"""
pdf_parser.py
-------------
Extracts clean, structured text, tables, and page metadata from PDF documents.
Handles in-memory Streamlit UploadedFile streams as well as local file paths.
"""

import io
import os
from typing import Union
import pdfplumber


def _format_table_to_markdown(table: list[list]) -> str:
    """
    Convert a 2D table grid from pdfplumber into clean Markdown table format
    so the LLM and retriever can easily parse rows and column relationships.
    """
    if not table or not any(table):
        return ""

    cleaned_rows = []
    for row in table:
        cleaned_row = [str(cell).strip().replace("\n", " ") if cell is not None else "" for cell in row]
        if any(cleaned_row):
            cleaned_rows.append(cleaned_row)

    if not cleaned_rows:
        return ""

    max_cols = max(len(row) for row in cleaned_rows)
    normalized_rows = [row + [""] * (max_cols - len(row)) for row in cleaned_rows]

    header = normalized_rows[0]
    header_line = "| " + " | ".join(header) + " |"
    separator_line = "| " + " | ".join(["---"] * max_cols) + " |"

    body_lines = ["| " + " | ".join(row) + " |" for row in normalized_rows[1:]]

    return "\n".join([header_line, separator_line] + body_lines)


def extract_pages_from_pdf(uploaded_file: Union[str, bytes, io.BytesIO, object]) -> list[dict]:
    """
    Extract text, tables, and page numbers from a PDF file as a list of page dicts.

    Parameters
    ----------
    uploaded_file : UploadedFile (Streamlit), file path str, or bytes stream.

    Returns
    -------
    list[dict] : List of dicts, each with keys:
        - "page_number": int
        - "text": str (combined narrative + markdown tables)
        - "raw_narrative": str
        - "tables": list of list of str
        - "char_count": int
    """
    if hasattr(uploaded_file, "seek"):
        try:
            uploaded_file.seek(0)
        except Exception:
            pass

    if isinstance(uploaded_file, str):
        file_stream = open(uploaded_file, "rb")
        is_opened_file = True
    elif isinstance(uploaded_file, (bytes, bytearray)):
        file_stream = io.BytesIO(uploaded_file)
        is_opened_file = False
    elif hasattr(uploaded_file, "read"):
        content = uploaded_file.read()
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        file_stream = io.BytesIO(content)
        is_opened_file = False
    else:
        file_stream = uploaded_file
        is_opened_file = False

    pages_data = []

    try:
        with pdfplumber.open(file_stream) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                tables = page.extract_tables() or []

                table_md_blocks = []
                for table in tables:
                    md_table = _format_table_to_markdown(table)
                    if md_table:
                        table_md_blocks.append(md_table)

                combined_parts = []
                if page_text.strip():
                    combined_parts.append(page_text.strip())

                if table_md_blocks:
                    combined_parts.append("\n[STRUCTURED TABLES]\n" + "\n\n".join(table_md_blocks))

                full_page_text = "\n\n".join(combined_parts)

                pages_data.append({
                    "page_number": page_idx,
                    "text": full_page_text,
                    "raw_narrative": page_text,
                    "tables": tables,
                    "char_count": len(full_page_text),
                })
    finally:
        if is_opened_file:
            file_stream.close()

    return pages_data


def extract_text_from_pdf(uploaded_file: Union[str, bytes, io.BytesIO, object]) -> str:
    """
    Extract all readable text from a PDF file, formatted with clear page delimiters.

    Returns
    -------
    str : The complete text of the PDF with [PAGE X] headers.
    """
    pages_data = extract_pages_from_pdf(uploaded_file)
    full_text_blocks = []

    for page in pages_data:
        full_text_blocks.append(f"[PAGE {page['page_number']}]\n{page['text']}")

    return "\n\n".join(full_text_blocks)


def validate_extracted_text(text: str, min_chars: int = 150) -> bool:
    """
    Validate that the extracted text is substantial enough to index.
    Flag scanned/image-only PDFs that lack a text layer.
    """
    return len(text.strip()) >= min_chars
