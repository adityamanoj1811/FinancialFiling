"""
test_metrics_extractor.py
--------------------------
Unit tests for financial metrics extraction, numeric parsing, and ratio calculations.
"""

from backend.metrics_extractor import parse_numeric_value, compute_financial_ratios


def test_parse_numeric_value():
    assert parse_numeric_value("₹2,57,823 Cr") == 257823.0
    assert parse_numeric_value("$7,505 Mn") == 7505.0
    assert parse_numeric_value("24.7%") == 24.7
    assert parse_numeric_value("0 (Debt-Free)") == 0.0
    assert parse_numeric_value("Not Found") is None
    assert parse_numeric_value("") is None


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
