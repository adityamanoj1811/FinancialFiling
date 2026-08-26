"""
generate_sample_filings.py
--------------------------
Generates realistic multi-page financial filing PDFs for sample Indian enterprises:
1. Reliance Industries Limited (Q1 FY25)
2. Tata Consultancy Services Limited (Q1 FY25)
3. Infosys Limited (Q1 FY25)

These sample PDFs contain realistic financial tables (Income Statement,
Balance Sheet, Segment Revenue, EBITDA, EPS, Key Ratios) and narrative sections
(MD&A, Risk Disclosures, Strategic Outlook) so users can immediately demo and
evaluate the multi-company RAG and metrics comparison features.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable


def create_reliance_filing(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6,
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("RELIANCE INDUSTRIES LIMITED", title_style))
    story.append(Paragraph("Quarterly Financial Results & Operational Performance Disclosures — Q1 FY2024-25 (Period Ended June 30, 2024)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=10))

    # Executive Overview
    story.append(Paragraph("1. Executive Financial Highlights", h2_style))
    overview_text = (
        "Reliance Industries Limited (RIL) delivered resilient consolidated operational and financial performance "
        "for the first quarter of fiscal year 2024-25 (Q1 FY25). Growth was driven by sustained momentum in consumer "
        "businesses (Jio Platforms and Reliance Retail) alongside steady contributions from the Oil & Gas exploration segment, "
        "which partially offset lower downstream chemical margins."
    )
    story.append(Paragraph(overview_text, body_style))

    # Financial Summary Table
    story.append(Paragraph("Key Consolidated Financial Figures", h2_style))
    fin_data = [
        ["Financial Metric", "Q1 FY25 (₹ Cr)", "Q1 FY24 (₹ Cr)", "YoY Change (%)"],
        ["Total Revenue (Gross)", "2,57,823", "2,31,132", "+11.5%"],
        ["Operating Revenue", "2,36,217", "2,07,559", "+13.8%"],
        ["EBITDA", "42,748", "41,982", "+1.8%"],
        ["Operating Expenses", "1,93,469", "1,65,577", "+16.8%"],
        ["Depreciation & Amortization", "13,596", "11,775", "+15.5%"],
        ["Finance Costs / Interest", "5,876", "5,837", "+0.7%"],
        ["Net Profit (Profit After Tax)", "17,445", "18,258", "-4.5%"],
        ["Earnings Per Share (EPS) — Basic (₹)", "25.78", "26.98", "-4.4%"],
        ["Operating Margin (%)", "18.1%", "20.2%", "-210 bps"],
        ["Net Profit Margin (%)", "7.4%", "8.8%", "-140 bps"],
    ]

    t = Table(fin_data, colWidths=[180, 110, 110, 110])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Segment Breakdown
    story.append(Paragraph("2. Segment Performance Breakdown", h2_style))
    seg_data = [
        ["Business Segment", "Segment Revenue (₹ Cr)", "Segment EBITDA (₹ Cr)", "EBITDA Margin (%)"],
        ["Oil to Chemicals (O2C)", "1,57,133", "13,093", "8.3%"],
        ["Oil & Gas Exploration", "6,179", "5,210", "84.3%"],
        ["Reliance Retail Ventures", "75,615", "5,664", "7.5%"],
        ["Digital Services (Jio)", "34,548", "14,638", "42.4%"],
        ["Others / Unallocated", "4,348", "4,143", "N/A"],
    ]
    t_seg = Table(seg_data, colWidths=[160, 120, 120, 110])
    t_seg.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_seg)
    story.append(Spacer(1, 10))

    # Balance Sheet & Capital Structure (Page 2)
    story.append(PageBreak())
    story.append(Paragraph("3. Consolidated Balance Sheet & Capital Structure Summary", h2_style))
    bs_text = (
        "As of June 30, 2024, the consolidated balance sheet maintains strong liquidity buffers. "
        "Net debt stood controlled through continued operational cash generation and discipline in capital expenditure."
    )
    story.append(Paragraph(bs_text, body_style))

    bs_data = [
        ["Balance Sheet Item", "As of June 30, 2024 (₹ Cr)", "As of March 31, 2024 (₹ Cr)"],
        ["Total Assets", "18,42,150", "17,98,420"],
        ["Property, Plant & Equipment", "8,95,430", "8,70,120"],
        ["Cash and Cash Equivalents", "2,15,400", "2,08,340"],
        ["Total Liabilities", "10,24,650", "9,98,210"],
        ["Total Debt / Gross Borrowings", "3,32,450", "3,24,620"],
        ["Net Debt (Gross Debt less Cash)", "1,17,050", "1,16,280"],
        ["Total Equity / Shareholders' Funds", "8,17,500", "8,00,210"],
        ["Debt-to-Equity Ratio", "0.41x", "0.41x"],
    ]
    t_bs = Table(bs_data, colWidths=[240, 140, 130])
    t_bs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_bs)
    story.append(Spacer(1, 10))

    # Management Discussion & Risk Factors
    story.append(Paragraph("4. Management Discussion and Key Risk Factors", h2_style))
    mda_text = (
        "<b>Capex Outlook:</b> Consolidated capital expenditure for Q1 FY25 was ₹28,785 crore ($3.5 billion), "
        "primarily directed toward 5G network densification, retail store expansion, and new energy giga-factories in Jamnagar.<br/><br/>"
        "<b>Risk Factors & Macro Headwinds:</b> Geopolitical tensions, volatile crude oil benchmark crack spreads, "
        "and potential supply chain disruptions remain key monitoring points. Downstream chemical demand in Asian markets "
        "experienced margin compression due to global oversupply."
    )
    story.append(Paragraph(mda_text, body_style))

    doc.build(story)


def create_tcs_filing(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0D3880"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1A56B2"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6,
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("TATA CONSULTANCY SERVICES LIMITED", title_style))
    story.append(Paragraph("Audited Consolidated Financial Results under Ind AS for Q1 FY2024-25 (Three Months Ended June 30, 2024)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0D3880"), spaceAfter=10))

    # Executive Overview
    story.append(Paragraph("1. Performance Summary", h2_style))
    overview_text = (
        "Tata Consultancy Services (TCS) reported steady financial performance for Q1 FY25, characterized by resilient order book bookings "
        "(Total Contract Value of $8.3 billion), solid operating margin expansion of 150 bps YoY to 24.7%, and continued leadership in "
        "enterprise AI transformations and cloud migration services."
    )
    story.append(Paragraph(overview_text, body_style))

    # Financial Highlights Table
    story.append(Paragraph("Key Consolidated Financial Highlights", h2_style))
    fin_data = [
        ["Financial Metric", "Q1 FY25 (₹ Cr)", "Q1 FY24 (₹ Cr)", "YoY Growth (%)"],
        ["Total Revenue from Operations", "62,613", "59,381", "+5.4%"],
        ["Revenue (USD $ Mn)", "$7,505 Mn", "$7,226 Mn", "+3.9%"],
        ["EBITDA", "16,842", "15,112", "+11.4%"],
        ["Operating Profit (EBIT)", "15,444", "13,755", "+12.3%"],
        ["Operating Expenses", "47,169", "45,626", "+3.4%"],
        ["Net Profit (Profit After Tax)", "12,040", "11,074", "+8.7%"],
        ["Earnings Per Share (EPS) — Basic (₹)", "33.28", "30.26", "+10.0%"],
        ["Operating Margin (%)", "24.7%", "23.2%", "+150 bps"],
        ["Net Profit Margin (%)", "19.2%", "18.6%", "+60 bps"],
        ["Dividend Declared per Share", "₹10.00", "₹9.00", "+11.1%"],
    ]

    t = Table(fin_data, colWidths=[180, 110, 110, 110])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0D3880")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Industry Verticals Breakdown
    story.append(Paragraph("2. Industry Vertical Performance (USD Growth)", h2_style))
    vert_data = [
        ["Industry Vertical", "Revenue Contribution (%)", "YoY Growth (Constant Currency)"],
        ["Banking, Financial Services & Insurance (BFSI)", "37.2%", "-0.8%"],
        ["Consumer Business & Retail", "15.4%", "+2.1%"],
        ["Life Sciences & Healthcare", "11.0%", "+4.0%"],
        ["Manufacturing", "9.8%", "+9.4%"],
        ["Technology & Services", "8.9%", "+1.5%"],
        ["Communication & Media", "6.4%", "-4.2%"],
        ["Energy, Resources & Utilities", "6.3%", "+5.7%"],
        ["Regional Markets & Others", "5.0%", "+14.4%"],
    ]
    t_vert = Table(vert_data, colWidths=[190, 160, 160])
    t_vert.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A56B2")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_vert)
    story.append(Spacer(1, 10))

    # Balance Sheet & Capital Allocation (Page 2)
    story.append(PageBreak())
    story.append(Paragraph("3. Consolidated Balance Sheet & Cash Position", h2_style))
    bs_text = (
        "TCS operates as a virtually zero-debt enterprise with pristine balance sheet health and exceptional return on equity (ROE > 48%). "
        "Free cash flow generation remained strong at ₹11,040 crore for the quarter."
    )
    story.append(Paragraph(bs_text, body_style))

    bs_data = [
        ["Balance Sheet Parameter", "As of June 30, 2024 (₹ Cr)", "As of March 31, 2024 (₹ Cr)"],
        ["Total Assets", "1,52,430", "1,48,920"],
        ["Cash, Bank Balances & Investments", "48,250", "45,830"],
        ["Trade Receivables", "41,120", "39,870"],
        ["Total Liabilities", "44,180", "42,750"],
        ["Total Debt / Borrowings", "0 (Debt-Free)", "0 (Debt-Free)"],
        ["Total Equity / Net Worth", "1,08,250", "1,06,170"],
        ["Debt-to-Equity Ratio", "0.00x", "0.00x"],
        ["Headcount (Total Employees)", "6,06,998", "6,01,546"],
        ["IT Services LTM Attrition Rate", "12.1%", "12.5%"],
    ]
    t_bs = Table(bs_data, colWidths=[240, 140, 130])
    t_bs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0D3880")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_bs)
    story.append(Spacer(1, 10))

    # GenAI & Strategic Outlook
    story.append(Paragraph("4. AI & Strategic Highlights", h2_style))
    strat_text = (
        "<b>Enterprise GenAI Pipeline:</b> TCS doubled its active GenAI engagements pipeline to $1.5 billion in Q1 FY25, "
        "with over 300,000 employees trained in foundational AI concepts through the TCS AI WisdomNext platform.<br/><br/>"
        "<b>Risks & Cautions:</b> Macroeconomic uncertainty in North American discretionary IT spending and delayed decision cycles "
        "in telecommunications remain downside risks."
    )
    story.append(Paragraph(strat_text, body_style))

    doc.build(story)


def create_infosys_filing(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#005A9C"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0077CC"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6,
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("INFOSYS LIMITED", title_style))
    story.append(Paragraph("Condensed Consolidated Financial Statements & Earnings Release — Q1 FY2024-25 (Quarter Ended June 30, 2024)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#005A9C"), spaceAfter=10))

    # Executive Overview
    story.append(Paragraph("1. Executive Financial Summary", h2_style))
    overview_text = (
        "Infosys delivered strong financial results for Q1 FY25, clocking 3.6% YoY revenue growth in constant currency terms, "
        "securing large deal TCV of $3.4 billion, and raising FY25 constant currency revenue guidance to 3.0% - 4.0%. "
        "Operating margin was robust at 21.1%, supported by Project Maximus cost optimization initiatives."
    )
    story.append(Paragraph(overview_text, body_style))

    # Financial Highlights Table
    story.append(Paragraph("Key Consolidated Financial Figures", h2_style))
    fin_data = [
        ["Financial Metric", "Q1 FY25 (₹ Cr)", "Q1 FY24 (₹ Cr)", "YoY Growth (%)"],
        ["Total Revenue from Operations", "39,315", "37,933", "+3.6%"],
        ["Revenue in US Dollars ($ Mn)", "$4,714 Mn", "$4,617 Mn", "+2.1%"],
        ["EBITDA", "9,425", "8,914", "+5.7%"],
        ["Operating Profit (EBIT)", "8,288", "7,891", "+5.0%"],
        ["Operating Expenses", "31,027", "30,042", "+3.3%"],
        ["Net Profit (Profit After Tax)", "6,368", "5,945", "+7.1%"],
        ["Earnings Per Share (EPS) — Basic (₹)", "15.42", "14.36", "+7.4%"],
        ["Operating Margin (%)", "21.1%", "20.8%", "+30 bps"],
        ["Net Profit Margin (%)", "16.2%", "15.7%", "+50 bps"],
        ["Free Cash Flow (FCF)", "₹9,161 Cr", "₹5,997 Cr", "+52.8%"],
    ]

    t = Table(fin_data, colWidths=[180, 110, 110, 110])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#005A9C")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Geographic Revenue Breakdown
    story.append(Paragraph("2. Geographic Revenue Breakdown", h2_style))
    geo_data = [
        ["Geographic Region", "Revenue Share (%)", "YoY Growth (Constant Currency)"],
        ["North America", "58.9%", "-1.2%"],
        ["Europe", "28.6%", "+9.8%"],
        ["Rest of the World", "9.7%", "+4.5%"],
        ["India", "2.8%", "+21.2%"],
    ]
    t_geo = Table(geo_data, colWidths=[190, 160, 160])
    t_geo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0077CC")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_geo)
    story.append(Spacer(1, 10))

    # Balance Sheet (Page 2)
    story.append(PageBreak())
    story.append(Paragraph("3. Consolidated Balance Sheet & Capital Resources", h2_style))
    bs_text = (
        "Infosys continues to maintain a pristine, debt-free balance sheet with high liquid cash reserves and an ROE of 31.8%. "
        "The company returned substantial capital to shareholders via dividends and share buyback programs."
    )
    story.append(Paragraph(bs_text, body_style))

    bs_data = [
        ["Balance Sheet Item", "As of June 30, 2024 (₹ Cr)", "As of March 31, 2024 (₹ Cr)"],
        ["Total Assets", "98,750", "95,420"],
        ["Cash, Cash Equivalents & Liquid Investments", "32,480", "29,610"],
        ["Trade Receivables", "28,640", "27,810"],
        ["Total Liabilities", "24,850", "23,940"],
        ["Total Debt / Borrowings", "0 (Debt-Free)", "0 (Debt-Free)"],
        ["Total Equity / Net Worth", "73,900", "71,480"],
        ["Debt-to-Equity Ratio", "0.00x", "0.00x"],
        ["Total Employee Headcount", "3,15,332", "3,17,240"],
        ["LTM Voluntary Attrition", "12.7%", "12.6%"],
    ]
    t_bs = Table(bs_data, colWidths=[240, 140, 130])
    t_bs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#005A9C")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_bs)
    story.append(Spacer(1, 10))

    # Topaz AI Suite & Risk Disclosures
    story.append(Paragraph("4. Generative AI (Infosys Topaz) & Risk Assessment", h2_style))
    topaz_text = (
        "<b>Infosys Topaz™ Momentum:</b> Infosys has integrated AI capabilities across 100+ client projects, "
        "leveraging its suite of 12,000+ AI assets. Enterprise clients are utilizing Topaz for autonomous code generation, "
        "customer service automation, and supply chain telemetry.<br/><br/>"
        "<b>Key Operational Risks:</b> Wage inflation in niche technical talent, potential foreign exchange volatility (USD/INR, EUR/INR), "
        "and geopolitical exposure across European accounts are identified as primary external risk factors."
    )
    story.append(Paragraph(topaz_text, body_style))

    doc.build(story)


def main():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(data_dir, exist_ok=True)

    rel_path = os.path.join(data_dir, "Reliance_Industries_Q1_FY25.pdf")
    tcs_path = os.path.join(data_dir, "TCS_Q1_FY25.pdf")
    infy_path = os.path.join(data_dir, "Infosys_Q1_FY25.pdf")

    print("Generating sample financial filing PDFs...")
    create_reliance_filing(rel_path)
    print(f"Generated: {rel_path}")

    create_tcs_filing(tcs_path)
    print(f"Generated: {tcs_path}")

    create_infosys_filing(infy_path)
    print(f"Generated: {infy_path}")
    print("All sample filings successfully generated in data/ folder!")


if __name__ == "__main__":
    main()
