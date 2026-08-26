"""
metrics_extractor.py
---------------------
Extracts structured financial metrics from corporate filings into normalized
tables, computes derived financial ratios, and generates automated executive
comparative synthesis reports with automatic model fallback recovery.
"""

import json
import re
from typing import Dict, Any, List, Optional
from groq import Groq
from backend.config import GROQ_FALLBACK_MODELS, FINANCIAL_METRICS, GROQ_API_TIMEOUT_SECONDS


# Common labels in annual reports, statutory accounts, and earnings releases.
# This deterministic pass makes the comparison views useful even when the user
# has not configured Groq or semantic retrieval does not surface a table page.
METRIC_LABELS = {
    "Total Revenue": ["revenue from operations", "total revenue", "net revenue", "turnover", "total income"],
    "Net Profit": ["profit after tax", "net profit", "profit for the period", "profit for the year"],
    "EBITDA": ["ebitda", "earnings before interest, tax, depreciation and amortisation", "earnings before interest tax depreciation and amortization"],
    "Operating Profit (EBIT)": ["operating profit", "profit from operations", "ebit", "earnings before interest and tax"],
    "Earnings Per Share (EPS)": ["earnings per share", "basic eps", "diluted eps"],
    "Operating Margin (%)": ["operating margin", "ebit margin", "operating profit margin"],
    "Net Profit Margin (%)": ["net profit margin", "profit after tax margin", "pat margin"],
    "Total Assets": ["total assets"],
    "Total Liabilities": ["total liabilities"],
    "Total Debt": ["total debt", "total borrowings", "borrowings", "financial liabilities"],
    "Cash & Liquid Investments": ["cash and cash equivalents", "cash & cash equivalents", "cash and bank balances", "cash and liquid investments"],
}

_NUMBER_AFTER_LABEL = re.compile(
    r"(?:[:\-–]\s*|\s{2,})(?P<value>\(?[₹$€£]?\s?[-+]?\d[\d,]*(?:\.\d+)?\)?(?:\s*(?:cr(?:ore)?s?|mn|million|bn|billion|lakh|lakhs|%))?)",
    re.IGNORECASE,
)


def _value_after_label(text: str, labels: List[str]) -> Optional[str]:
    """Return the first plausible value adjacent to any financial row label."""
    candidates = []
    for label in labels:
        pattern = re.compile(rf"\b{re.escape(label)}\b(?P<tail>.{{0,90}})", re.IGNORECASE)
        for match in pattern.finditer(text):
            value_match = _NUMBER_AFTER_LABEL.search(match.group("tail"))
            if not value_match:
                continue
            value = re.sub(r"\s+", " ", value_match.group("value")).strip(" .;,")
            score = 0
            if any(marker in value.lower() for marker in ("₹", "$", "cr", "mn", "bn", "lakh", "%")):
                score += 3
            if "," in value or "." in value:
                score += 1
            if len(re.sub(r"\D", "", value)) >= 3:
                score += 1
            candidates.append((score, match.start(), value))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (-item[0], item[1]))
    return candidates[0][2]


def extract_metrics_from_text(text: str) -> Dict[str, str]:
    """Extract a best-effort metric set directly from filing text, without an LLM."""
    metrics = {metric: "Not Found" for metric in FINANCIAL_METRICS}
    normalized_text = re.sub(r"\s+", " ", text)
    for metric, labels in METRIC_LABELS.items():
        value = _value_after_label(normalized_text, labels)
        if value:
            metrics[metric] = value

    period = re.search(
        r"(?:for (?:the )?(?:quarter|year|period) ended|quarter ended|year ended)\s+([A-Za-z0-9, ]{6,45})",
        normalized_text,
        re.IGNORECASE,
    )
    if period:
        metrics["Reporting Period"] = period.group(0).strip(" .;,")
    return metrics


def extract_metrics_from_vector_store(vector_store, source_name: str) -> Dict[str, str]:
    """Use every indexed chunk for deterministic metric extraction of one filing."""
    chunks = sorted(
        vector_store.get_all_chunks(source_filter=source_name),
        key=lambda chunk: (chunk.get("page_number", 1), chunk.get("chunk_id", 0)),
    )
    return extract_metrics_from_text("\n".join(chunk.get("text", "") for chunk in chunks))



def _find_most_relevant_chunks_for_metrics(vector_store, source_name: str, top_k: int = 6) -> str:
    """
    Execute targeted probe queries against the vector store to collect high-signal
    chunks covering all key financial statements (P&L, Balance Sheet, Ratios, MD&A).
    """
    probe_queries = [
        "total revenue from operations and gross income",
        "net profit after tax PAT profit for the period",
        "operating profit EBIT EBITDA operating margin",
        "earnings per share basic diluted EPS",
        "total assets cash bank balance investments balance sheet",
        "total liabilities total debt borrowings equity",
        "quarterly financial highlights reporting period",
    ]

    seen_chunk_texts = set()
    combined_chunks = []
    for query in probe_queries:
        results = vector_store.search(query, top_k=top_k, source_filter=source_name)
        for chunk in results:
            if chunk["text"] not in seen_chunk_texts:
                seen_chunk_texts.add(chunk["text"])
                combined_chunks.append(f"[Page {chunk.get('page_number', 1)}]\n{chunk['text']}")

    return "\n---\n".join(combined_chunks)


def _get_candidate_models(requested_model: Optional[str]) -> List[str]:
    """Build list of models to try with fallback resilience."""
    models_to_try = []
    if requested_model:
        models_to_try.append(requested_model)
    for m in GROQ_FALLBACK_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)
    return models_to_try


def extract_metrics(client: Groq, vector_store, source_name: str, model: Optional[str] = None) -> Dict[str, str]:
    """
    Extract a structured dictionary of financial metrics for a single filing using Groq LLM.
    """
    deterministic_metrics = extract_metrics_from_vector_store(vector_store, source_name)
    context_text = _find_most_relevant_chunks_for_metrics(vector_store, source_name)
    metrics_list_str = "\n".join(f"- {metric}" for metric in FINANCIAL_METRICS)

    system_prompt = (
        "You are an expert financial analyst and data extraction system. "
        "Extract key financial metrics from the provided filing excerpts.\n\n"
        f"TARGET METRICS:\n{metrics_list_str}\n\n"
        "RULES:\n"
        "1. Return ONLY a valid JSON object mapping each metric name exactly as listed above to its extracted value.\n"
        "2. Keep the exact currency symbols and units found in the text (e.g. '₹2,57,823 Cr', '$7,505 Mn', '24.7%').\n"
        "3. If a metric is not mentioned in the excerpts, set its value to 'Not Found'.\n"
        "4. Do NOT wrap output in any conversational filler. Return pure JSON."
    )

    user_prompt = f"DOCUMENT: {source_name}\n\nFILING EXCERPTS:\n{context_text}"
    models_to_try = _get_candidate_models(model)
    response = None

    for m in models_to_try:
        try:
            response = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                timeout=GROQ_API_TIMEOUT_SECONDS,
            )
            break
        except Exception:
            continue

    if response is None:
        return deterministic_metrics

    raw_output = response.choices[0].message.content.strip()
    cleaned_output = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_output, flags=re.MULTILINE).strip()

    try:
        extracted = json.loads(cleaned_output)
    except json.JSONDecodeError:
        extracted = {}
        for metric in FINANCIAL_METRICS:
            match = re.search(rf'"{re.escape(metric)}"\s*:\s*"([^"]+)"', cleaned_output)
            if match:
                extracted[metric] = match.group(1)
            else:
                extracted[metric] = "Not Found"

    for metric in FINANCIAL_METRICS:
        if metric not in extracted or not extracted[metric]:
            extracted[metric] = "Not Found"
        if extracted[metric] == "Not Found" and deterministic_metrics[metric] != "Not Found":
            extracted[metric] = deterministic_metrics[metric]

    return extracted


def parse_numeric_value(val_str: str) -> Optional[float]:
    """
    Parse a numeric float from human-formatted financial strings
    (e.g., '₹2,57,823 Cr' -> 257823.0, '24.7%' -> 24.7, '$7,505 Mn' -> 7505.0).
    """
    if not val_str or val_str == "Not Found":
        return None

    cleaned = str(val_str).replace(",", "").replace("₹", "").replace("$", "").replace("Cr", "").replace("Mn", "").replace("%", "").strip()
    is_negative = cleaned.startswith("(") and cleaned.endswith(")")

    match = re.search(r"[-+]?\d*\.?\d+", cleaned)
    if match:
        try:
            value = float(match.group(0))
            return -value if is_negative else value
        except ValueError:
            return None
    return None


def compute_financial_ratios(extracted_metrics: Dict[str, str]) -> Dict[str, Any]:
    """
    Compute derived financial ratios (Margins, Debt Ratios) from extracted metrics.
    """
    rev = parse_numeric_value(extracted_metrics.get("Total Revenue", ""))
    pat = parse_numeric_value(extracted_metrics.get("Net Profit", ""))
    ebitda = parse_numeric_value(extracted_metrics.get("EBITDA", ""))
    ebit = parse_numeric_value(extracted_metrics.get("Operating Profit (EBIT)", ""))
    assets = parse_numeric_value(extracted_metrics.get("Total Assets", ""))
    debt = parse_numeric_value(extracted_metrics.get("Total Debt", ""))

    ratios = {}

    if rev and pat and rev > 0:
        ratios["Calculated Net Margin (%)"] = f"{(pat / rev) * 100:.2f}%"
    else:
        ratios["Calculated Net Margin (%)"] = extracted_metrics.get("Net Profit Margin (%)", "N/A")

    if rev and ebit and rev > 0:
        ratios["Calculated Operating Margin (%)"] = f"{(ebit / rev) * 100:.2f}%"
    elif rev and ebitda and rev > 0:
        ratios["Calculated EBITDA Margin (%)"] = f"{(ebitda / rev) * 100:.2f}%"
    else:
        ratios["Calculated Operating Margin (%)"] = extracted_metrics.get("Operating Margin (%)", "N/A")

    if debt is not None and assets and assets > 0:
        ratios["Debt to Total Assets"] = f"{(debt / assets):.2f}x"
    else:
        ratios["Debt to Total Assets"] = "N/A"

    return ratios


def generate_executive_summary(client: Groq, vector_store, sources: List[str], model: Optional[str] = None) -> str:
    """
    Generate an in-depth AI-powered executive comparative report across all uploaded filings with model fallback.
    """
    all_chunks = []
    for source in sources:
        results = vector_store.search("executive summary financial performance revenue net profit risks strategy", top_k=5, source_filter=source)
        all_chunks.extend(results)

    grouped_context = {}
    for c in all_chunks:
        grouped_context.setdefault(c["source"], []).append(f"[Page {c.get('page_number', 1)}] {c['text']}")

    context_lines = []
    for src, chunks in grouped_context.items():
        context_lines.append(f"### {src}\n" + "\n---\n".join(chunks))
    combined_context = "\n\n".join(context_lines)

    system_prompt = (
        "You are an executive managing director of equity research. Produce a comprehensive, "
        "institutional-grade comparative research report evaluating the companies whose filings are provided.\n\n"
        "Structure the report with the following markdown sections:\n"
        "1. **Executive Summary & Comparative Overview** (Key rankings, growth velocity, standout performers)\n"
        "2. **Financial Performance & Margin Analysis** (Revenue scale, operating leverage, net profitability)\n"
        "3. **Balance Sheet Health & Solvency Matrix** (Debt burdens, cash liquidity, capital allocation)\n"
        "4. **Strategic Growth Vectors & Technology Initiatives** (GenAI, enterprise platforms, new markets)\n"
        "5. **Key Risks & Sector Headwinds** (Vulnerabilities, cost pressures, macro challenges)\n"
        "6. **Institutional Analyst Verdict** (Final summary takeaway for investment decision makers)\n\n"
        "Cite specific numbers, percentages, and page numbers accurately."
    )

    user_prompt = f"FILING CONTEXT:\n{combined_context}\n\nProduce the complete institutional research report."
    models_to_try = _get_candidate_models(model)
    response = None
    last_err = None

    for m in models_to_try:
        try:
            response = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                timeout=GROQ_API_TIMEOUT_SECONDS,
            )
            break
        except Exception as e:
            last_err = e
            continue

    if response is None:
        return f"Error: Unable to generate executive summary. Models attempted: {models_to_try}. Details: {last_err}"

    return response.choices[0].message.content
