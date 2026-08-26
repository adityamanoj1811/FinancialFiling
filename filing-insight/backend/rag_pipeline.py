"""
rag_pipeline.py
----------------
Generation engine for Filing Insight RAG. Retrieves relevant context chunks from
indexed filings, integrates conversation history for multi-turn follow-ups, and
calls Groq LLM with streaming support and automatic fallback model recovery.
"""

from typing import Generator, Union, Dict, Any, List, Optional
from groq import Groq, NotFoundError
from backend.config import GROQ_FALLBACK_MODELS, TOP_K_PER_DOCUMENT, GROQ_API_TIMEOUT_SECONDS


def build_context_block(retrieved_chunks: List[dict]) -> str:
    """
    Format retrieved chunks into a clearly-labeled text block for the LLM prompt.
    Labels each chunk with its source document and page number for precise citations.
    """
    if not retrieved_chunks:
        return "No relevant context was found in the uploaded filings."

    grouped: Dict[str, List[dict]] = {}
    for chunk in retrieved_chunks:
        grouped.setdefault(chunk["source"], []).append(chunk)

    context_sections = []
    for source_name, chunks in grouped.items():
        chunk_lines = []
        for c in chunks:
            page_info = f"[Page {c.get('page_number', 1)}]"
            chunk_lines.append(f"{page_info}\n{c['text']}")
        chunk_texts = "\n---\n".join(chunk_lines)
        context_sections.append(f"### Source Document: {source_name}\n{chunk_texts}")

    return "\n\n".join(context_sections)


def _build_system_prompt() -> str:
    return (
        "You are an expert senior financial analyst assistant. "
        "You analyze corporate financial filings (quarterly results, annual reports, SEC 10-K, "
        "BSE/NSE disclosures, earnings transcripts) with rigorous precision.\n\n"
        "Instructions:\n"
        "1. GROUNDING: Answer the user's question using ONLY the provided filing excerpts. "
        "Do NOT invent numbers or rely on unverified assumptions.\n"
        "2. CITATIONS: Cite the specific document name and page number (e.g. '[TCS_Q1_FY25.pdf, Page 2]') "
        "for every factual or numeric claim.\n"
        "3. CROSS-COMPANY COMPARISON: If multiple filings are present and the user asks a comparative "
        "question, provide a side-by-side comparison (using markdown tables where helpful) contrasting "
        "metrics, growth rates, margins, and strategic differences.\n"
        "4. ABSENCE OF DATA: If a metric or detail is not present in the excerpts, clearly state: "
        "'This information is not provided in the uploaded excerpts.'\n"
        "5. TONE & STRUCTURE: Professional, concise, structured with bullet points and bold highlights for numbers."
    )


def _prepare_messages(
    question: str,
    context_block: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> List[Dict[str, str]]:
    """Build the message array with system prompt, recent history, and contextual question."""
    system_prompt = _build_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]

    if chat_history:
        recent_history = chat_history[-4:]
        for turn in recent_history:
            if turn.get("role") in ("user", "assistant"):
                messages.append({
                    "role": turn["role"],
                    "content": turn["content"],
                })

    user_prompt = f"FILING CONTEXT:\n{context_block}\n\nUSER QUESTION:\n{question}"
    messages.append({"role": "user", "content": user_prompt})

    return messages


def retrieve_relevant_chunks(
    vector_store,
    question: str,
    active_sources: Optional[List[str]] = None,
    top_k: int = TOP_K_PER_DOCUMENT,
) -> List[dict]:
    """Retrieve top matching chunks across all or selected documents."""
    sources = active_sources if active_sources else vector_store.get_all_sources()
    retrieved_chunks = []
    for source in sources:
        retrieved_chunks.extend(
            vector_store.search(question, top_k=top_k, source_filter=source)
        )
    return retrieved_chunks


def _get_candidate_models(requested_model: Optional[str]) -> List[str]:
    """Build list of models to try with fallback resilience."""
    models_to_try = []
    if requested_model:
        models_to_try.append(requested_model)
    for m in GROQ_FALLBACK_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)
    return models_to_try


def stream_answer_question(
    client: Groq,
    question: str,
    vector_store,
    chat_history: Optional[List[Dict[str, str]]] = None,
    active_sources: Optional[List[str]] = None,
    model: Optional[str] = None,
) -> Generator[Union[str, Dict[str, Any]], None, None]:
    """
    Stream the LLM answer token-by-token with automatic fallback retry if a model is unavailable.
    """
    retrieved_chunks = retrieve_relevant_chunks(vector_store, question, active_sources)
    context_block = build_context_block(retrieved_chunks)
    messages = _prepare_messages(question, context_block, chat_history)

    models_to_try = _get_candidate_models(model)
    response_stream = None
    last_err = None

    for m in models_to_try:
        try:
            response_stream = client.chat.completions.create(
                model=m,
                messages=messages,
                temperature=0.1,
                stream=True,
                timeout=GROQ_API_TIMEOUT_SECONDS,
            )
            break
        except Exception as e:
            last_err = e
            continue

    if response_stream is None:
        err_str = str(last_err)
        if "401" in err_str or "invalid_api_key" in err_str:
            yield "Invalid Groq API Key (401). Please check your key at https://console.groq.com/keys, create a new API key, and paste it into the sidebar."
        else:
            yield f"Error connecting to Groq models ({models_to_try}). Details: {last_err}"
        return

    for chunk in response_stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

    sources_used = sorted(set(c["source"] for c in retrieved_chunks))
    yield {
        "__metadata__": True,
        "sources_used": sources_used,
        "chunks_used": retrieved_chunks,
        "context_block": context_block,
    }


def answer_question(
    client: Groq,
    question: str,
    vector_store,
    chat_history: Optional[List[Dict[str, str]]] = None,
    active_sources: Optional[List[str]] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Synchronous non-streaming answer generation with automatic fallback recovery.
    """
    retrieved_chunks = retrieve_relevant_chunks(vector_store, question, active_sources)
    context_block = build_context_block(retrieved_chunks)
    messages = _prepare_messages(question, context_block, chat_history)

    models_to_try = _get_candidate_models(model)
    response = None
    last_err = None

    for m in models_to_try:
        try:
            response = client.chat.completions.create(
                model=m,
                messages=messages,
                temperature=0.1,
                stream=False,
                timeout=GROQ_API_TIMEOUT_SECONDS,
            )
            break
        except Exception as e:
            last_err = e
            continue

    if response is None:
        err_str = str(last_err)
        if "401" in err_str or "invalid_api_key" in err_str:
            err_msg = "Invalid Groq API Key (401). Please check your key at https://console.groq.com/keys, create a new API key, and paste it into the sidebar."
        else:
            err_msg = f"Error: Groq models unavailable. Details: {last_err}"
        return {
            "answer": err_msg,
            "sources_used": [],
            "chunks_used": retrieved_chunks,
            "context_block": context_block,
        }

    answer_text = response.choices[0].message.content
    sources_used = sorted(set(c["source"] for c in retrieved_chunks))

    return {
        "answer": answer_text,
        "sources_used": sources_used,
        "chunks_used": retrieved_chunks,
        "context_block": context_block,
    }
