"""
test_metrics_extractor.py
--------------------------
Unit tests for financial metrics extraction, numeric parsing, and ratio calculations.
"""

from backend.metrics_extractor import extract_metrics_from_text, parse_numeric_value, compute_financial_ratios


def test_parse_numeric_value():
    assert parse_numeric_value("₹2,57,823 Cr") == 257823.0
    assert parse_numeric_value("$7,505 Mn") == 7505.0
    assert parse_numeric_value("24.7%") == 24.7
    assert parse_numeric_value("0 (Debt-Free)") == 0.0
    assert parse_numeric_value("Not Found") is None
    assert parse_numeric_value("") is None
    assert parse_numeric_value("(1,240.5)") == -1240.5


def test_extract_metrics_from_filing_text_without_llm():
    text = """
    Consolidated results for the quarter ended 30 June 2026.
    Revenue from operations: ₹2,57,823 Cr
    Profit after tax: ₹17,445 Cr
    EBITDA: ₹42,748 Cr
    Earnings per share: ₹25.40
    Operating margin: 16.6%
    Total assets: ₹18,42,150 Cr
    Total borrowings: ₹3,32,450 Cr
    Cash and cash equivalents: ₹45,100 Cr
    """
    metrics = extract_metrics_from_text(text)
    assert metrics["Total Revenue"] == "₹2,57,823 Cr"
    assert metrics["Net Profit"] == "₹17,445 Cr"
    assert metrics["EBITDA"] == "₹42,748 Cr"
    assert metrics["Total Assets"] == "₹18,42,150 Cr"
    assert metrics["Total Debt"] == "₹3,32,450 Cr"


def test_compute_financial_ratios():
    sample_metrics = {
        "Total Revenue": "62,613",
        "Net Profit": "12,040",
        "Operating Profit (EBIT)": "15,444",
        "Total Assets": "1,52,430",
        "Total Debt": "0",
    }
    ratios = compute_financial_ratios(sample_metrics)

    assert "Calculated Net Margin (%)" in ratios
    assert "19.23%" in ratios["Calculated Net Margin (%)"]
    assert "Calculated Operating Margin (%)" in ratios
    assert "24.67%" in ratios["Calculated Operating Margin (%)"]
    assert ratios["Debt to Total Assets"] == "0.00x"
