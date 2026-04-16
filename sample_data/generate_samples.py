#!/usr/bin/env python3
"""
Generate synthetic financial PDFs and CSVs for testing.

PDFs:
  - TechCorp_Annual_Report_2023.pdf     - full annual report (exec summary, P&L, balance sheet, cash flow, outlook)
  - TechCorp_Q4_2023_Earnings.pdf       - quarterly earnings release with cloud deep-dive
  - TechCorp_Risk_Assessment_2023.pdf    - enterprise risk factors and mitigation

CSVs:
  - quarterly_financials.csv             - Monthly P&L (Revenue, COGS, EBITDA, Net Income)
  - sales_by_region_product.csv          - Sales by region x product x month
  - budget_vs_actuals.csv                - Departmental budget vs actual spending
  - annual_financials.csv                - 5-year P&L summary
  - quarterly_segments.csv               - Revenue by business segment per quarter
  - monthly_cashflow_2023.csv            - Monthly operating/investing/financing cash flows
  - investment_portfolio.csv             - Asset allocation and returns
  - employee_headcount.csv               - Headcount by department and quarter
"""
from pathlib import Path

import pandas as pd
from fpdf import FPDF

OUTPUT = Path(__file__).parent
OUTPUT.mkdir(parents=True, exist_ok=True)

COMPANY = "TechCorp Inc."
TICKER = "TCHC"
CURRENCY = "USD"


# ═══════════════════════════════════════════════════════════════════════════════
#  PDF helpers
# ═══════════════════════════════════════════════════════════════════════════════

class FinancialPDF(FPDF):
    def __init__(self, title: str):
        super().__init__()
        self.doc_title = title
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, f"{COMPANY} - {self.doc_title}", align="L")
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | Confidential", align="C")
        self.set_text_color(0, 0, 0)

    def section_title(self, text: str):
        self.ln(6)
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 9, text, fill=True, ln=True)
        self.ln(2)

    def subsection(self, text: str):
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 7, text, ln=True)
        self.ln(1)

    def body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def kv(self, label: str, value: str):
        self.set_font("Helvetica", "B", 10)
        self.cell(80, 6, label + ":", ln=False)
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, value, ln=True)

    def table(self, headers: list[str], rows: list[list[str]], col_widths: list[int] | None = None):
        if col_widths is None:
            w = int(170 / len(headers))
            col_widths = [w] * len(headers)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(50, 80, 160)
        self.set_text_color(255, 255, 255)
        for h, cw in zip(headers, col_widths):
            self.cell(cw, 7, str(h), border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 9)
        self.set_text_color(0, 0, 0)
        for i, row in enumerate(rows):
            self.set_fill_color(245, 248, 255) if i % 2 == 0 else self.set_fill_color(255, 255, 255)
            for cell, cw in zip(row, col_widths):
                self.cell(cw, 6, str(cell), border=1, fill=True)
            self.ln()
        self.ln(3)

    def cover(self, subtitle: str, date: str):
        self.add_page()
        self.ln(30)
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(30, 60, 140)
        self.cell(0, 12, COMPANY, align="C", ln=True)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, subtitle, align="C", ln=True)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, date, align="C", ln=True)
        self.ln(8)
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, f"Ticker: {TICKER}  |  Currency: {CURRENCY} Millions", align="C", ln=True)
        self.set_text_color(0, 0, 0)


# ��══════════════════════════════════════════════════════════════════════════════
#  PDF 1 - Annual Report 2023
# ═══════════════════════════════════════════════════════════════════════════════

def generate_annual_report():
    pdf = FinancialPDF("Annual Report 2023")
    pdf.cover("Annual Report - Fiscal Year 2023", "March 15, 2024")

    # ── Executive Summary ──
    pdf.add_page()
    pdf.section_title("Executive Summary")
    pdf.body(
        "Fiscal year 2023 marked a pivotal year for TechCorp Inc. The company achieved record "
        "operating income of $4.2 billion despite a challenging macroeconomic environment "
        "characterized by elevated interest rates and softening enterprise IT spending. Revenue "
        "grew 8.4% year-over-year to $18.7 billion, driven by strong performance in our Cloud "
        "Services division (+31% YoY) and recurring subscription revenue now representing 62% "
        "of total revenue, up from 54% in 2022.\n\n"
        "The company returned $2.1 billion to shareholders through share buybacks and dividends. "
        "We ended the year with $6.8 billion in cash and short-term investments, providing "
        "significant strategic flexibility for organic investment and potential M&A activity.\n\n"
        "Looking ahead to 2024, management is guiding for revenue growth of 10-12%, operating "
        "margin expansion of approximately 150 basis points, and continued aggressive investment "
        "in artificial intelligence capabilities across all product lines."
    )

    pdf.section_title("Key Financial Highlights - FY2023")
    pdf.table(
        headers=["Metric", "FY2023", "FY2022", "Change"],
        rows=[
            ["Total Revenue", "$18,742M", "$17,289M", "+8.4%"],
            ["Gross Profit", "$9,371M", "$8,299M", "+12.9%"],
            ["Gross Margin", "50.0%", "48.0%", "+200 bps"],
            ["Operating Income", "$4,217M", "$3,631M", "+16.1%"],
            ["Operating Margin", "22.5%", "21.0%", "+150 bps"],
            ["Net Income", "$3,412M", "$2,918M", "+16.9%"],
            ["Diluted EPS", "$7.84", "$6.54", "+19.9%"],
            ["Free Cash Flow", "$3,891M", "$3,245M", "+19.9%"],
            ["Cash & Equivalents", "$6,842M", "$5,631M", "+21.5%"],
        ],
        col_widths=[60, 38, 38, 34],
    )

    # ── Revenue Breakdown ──
    pdf.section_title("Revenue by Business Segment")
    pdf.body(
        "TechCorp operates through three reportable segments: Cloud Services, Enterprise "
        "Software, and Professional Services. Cloud Services continued to be the primary "
        "growth engine, benefiting from accelerating digital transformation initiatives globally."
    )
    pdf.table(
        headers=["Segment", "FY2023 Revenue", "FY2022 Revenue", "YoY Growth", "% of Total"],
        rows=[
            ["Cloud Services", "$7,124M", "$5,438M", "+31.0%", "38%"],
            ["Enterprise Software", "$8,412M", "$8,203M", "+2.5%", "45%"],
            ["Professional Services", "$3,206M", "$3,648M", "-12.1%", "17%"],
            ["Total", "$18,742M", "$17,289M", "+8.4%", "100%"],
        ],
        col_widths=[50, 35, 35, 30, 20],
    )
    pdf.body(
        "The Professional Services segment decline reflects our deliberate strategic shift "
        "toward higher-margin recurring software revenue. We expect this segment to stabilize "
        "in 2024 as implementation backlogs clear and new managed service contracts ramp up."
    )

    # ── Income Statement ──
    pdf.add_page()
    pdf.section_title("Consolidated Income Statement (USD Millions)")
    pdf.table(
        headers=["Line Item", "FY2023", "FY2022", "FY2021"],
        rows=[
            ["Revenue", "18,742", "17,289", "14,831"],
            ["Cost of Revenue", "9,371", "8,990", "8,158"],
            ["Gross Profit", "9,371", "8,299", "6,673"],
            ["R&D Expenses", "2,249", "2,075", "1,780"],
            ["Sales & Marketing", "1,874", "1,902", "1,631"],
            ["General & Administrative", "1,031", "691", "594"],
            ["Total Operating Expenses", "5,154", "4,668", "4,005"],
            ["Operating Income", "4,217", "3,631", "2,668"],
            ["Interest Income", "312", "187", "89"],
            ["Interest Expense", "(124)", "(98)", "(76)"],
            ["Pre-tax Income", "4,405", "3,720", "2,681"],
            ["Income Tax Expense", "(993)", "(802)", "(590)"],
            ["Net Income", "3,412", "2,918", "2,091"],
        ],
        col_widths=[70, 34, 34, 32],
    )

    # ── Balance Sheet ──
    pdf.section_title("Consolidated Balance Sheet - December 31, 2023 (USD Millions)")
    pdf.subsection("Assets")
    pdf.table(
        headers=["Asset", "2023", "2022"],
        rows=[
            ["Cash & Cash Equivalents", "4,231", "3,412"],
            ["Short-term Investments", "2,611", "2,219"],
            ["Accounts Receivable (net)", "3,187", "2,934"],
            ["Inventory", "412", "389"],
            ["Prepaid Expenses & Other", "687", "542"],
            ["Total Current Assets", "11,128", "9,496"],
            ["Property, Plant & Equipment", "4,312", "3,876"],
            ["Goodwill", "6,841", "6,312"],
            ["Intangible Assets (net)", "1,923", "2,187"],
            ["Other Long-term Assets", "891", "743"],
            ["Total Assets", "25,095", "22,614"],
        ],
        col_widths=[90, 40, 40],
    )
    pdf.subsection("Liabilities & Shareholders' Equity")
    pdf.table(
        headers=["Item", "2023", "2022"],
        rows=[
            ["Accounts Payable", "1,243", "1,187"],
            ["Accrued Liabilities", "2,134", "1,876"],
            ["Deferred Revenue (current)", "1,892", "1,654"],
            ["Total Current Liabilities", "5,269", "4,717"],
            ["Long-term Debt", "4,500", "4,500"],
            ["Deferred Revenue (long-term)", "987", "876"],
            ["Other Long-term Liabilities", "643", "589"],
            ["Total Liabilities", "11,399", "10,682"],
            ["Common Stock & APIC", "7,234", "6,812"],
            ["Retained Earnings", "8,341", "6,534"],
            ["Accumulated OCI", "(1,879)", "(1,414)"],
            ["Total Shareholders' Equity", "13,696", "11,932"],
            ["Total Liabilities & Equity", "25,095", "22,614"],
        ],
        col_widths=[90, 40, 40],
    )

    # ── Cash Flow ──
    pdf.add_page()
    pdf.section_title("Cash Flow Summary (USD Millions)")
    pdf.table(
        headers=["Activity", "FY2023", "FY2022", "FY2021"],
        rows=[
            ["Net Income", "3,412", "2,918", "2,091"],
            ["D&A and Amortization", "891", "812", "743"],
            ["Stock-based Compensation", "634", "587", "512"],
            ["Changes in Working Capital", "(312)", "(241)", "(187)"],
            ["Other Operating", "187", "143", "112"],
            ["Cash from Operations", "4,812", "4,219", "3,271"],
            ["Capital Expenditures", "(921)", "(974)", "(812)"],
            ["Acquisitions", "(412)", "(1,243)", "(234)"],
            ["Investment Purchases (net)", "(392)", "(312)", "(198)"],
            ["Cash from Investing", "(1,725)", "(2,529)", "(1,244)"],
            ["Share Repurchases", "(1,500)", "(1,200)", "(800)"],
            ["Dividends Paid", "(612)", "(543)", "(421)"],
            ["Debt Repayment", "-", "(500)", "-"],
            ["Cash from Financing", "(2,112)", "(2,243)", "(1,221)"],
            ["Net Change in Cash", "975", "(553)", "806"],
            ["Free Cash Flow", "3,891", "3,245", "2,459"],
        ],
        col_widths=[80, 30, 30, 30],
    )

    # ── Geographic Revenue ──
    pdf.section_title("Revenue by Geography (USD Millions)")
    pdf.table(
        headers=["Region", "FY2023", "FY2022", "YoY Growth"],
        rows=[
            ["North America", "9,371", "8,818", "+6.3%"],
            ["Europe", "5,247", "4,843", "+8.3%"],
            ["Asia Pacific", "2,999", "2,594", "+15.6%"],
            ["Rest of World", "1,125", "1,034", "+8.8%"],
            ["Total", "18,742", "17,289", "+8.4%"],
        ],
        col_widths=[60, 38, 38, 34],
    )

    # ── Outlook ──
    pdf.add_page()
    pdf.section_title("Fiscal Year 2024 Guidance")
    pdf.body(
        "Management provides the following guidance for fiscal year 2024, reflecting current "
        "business conditions and macroeconomic assumptions:"
    )
    pdf.table(
        headers=["Metric", "FY2024 Guidance", "FY2023 Actual"],
        rows=[
            ["Revenue", "$20.6B - $21.0B", "$18.74B"],
            ["Revenue Growth", "10% - 12%", "8.4%"],
            ["Gross Margin", "51.0% - 52.0%", "50.0%"],
            ["Operating Margin", "23.5% - 24.5%", "22.5%"],
            ["Diluted EPS", "$8.90 - $9.20", "$7.84"],
            ["Free Cash Flow", "$4.3B - $4.6B", "$3.89B"],
            ["Capital Expenditures", "$850M - $950M", "$921M"],
        ],
        col_widths=[70, 55, 45],
    )
    pdf.body(
        "Key assumptions: USD/EUR exchange rate of 1.08; no material acquisitions; continued "
        "investment in AI R&D of approximately $600M; effective tax rate of 22-23%."
    )

    out = OUTPUT / "TechCorp_Annual_Report_2023.pdf"
    pdf.output(str(out))
    print(f"Created: {out}")


# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 2 - Q4 2023 Earnings
# ═══════════════════════════════════════════════════════════════════════════════

def generate_q4_earnings():
    pdf = FinancialPDF("Q4 2023 Earnings Release")
    pdf.cover("Q4 & Full Year 2023 Earnings Release", "February 1, 2024")

    pdf.add_page()
    pdf.section_title("Q4 2023 Highlights")
    pdf.body(
        "TechCorp reported fourth quarter 2023 revenue of $5,124 million, up 11.2% "
        "year-over-year and above the high end of our guidance range of $4,900-5,000 million. "
        "Q4 operating income reached $1,231 million, representing an operating margin of 24.0%, "
        "our highest quarterly margin to date. Cloud Services bookings of $2.8 billion in Q4 "
        "represent a record quarter and imply an annualized recurring revenue (ARR) run-rate "
        "of $9.4 billion entering 2024."
    )
    pdf.table(
        headers=["Metric", "Q4 2023", "Q4 2022", "QoQ", "YoY"],
        rows=[
            ["Revenue", "$5,124M", "$4,607M", "+3.2%", "+11.2%"],
            ["Gross Profit", "$2,664M", "$2,258M", "+4.1%", "+18.0%"],
            ["Gross Margin", "52.0%", "49.0%", "+90 bps", "+300 bps"],
            ["Operating Income", "$1,231M", "$1,005M", "+8.3%", "+22.5%"],
            ["Operating Margin", "24.0%", "21.8%", "+120 bps", "+220 bps"],
            ["Net Income", "$987M", "$812M", "+9.0%", "+21.6%"],
            ["Diluted EPS", "$2.28", "$1.83", "+9.1%", "+24.6%"],
            ["Cloud ARR", "$9,412M", "$7,234M", "+5.6%", "+30.1%"],
        ],
        col_widths=[52, 30, 30, 26, 26],
    )

    pdf.section_title("Quarterly Revenue Trend (USD Millions)")
    pdf.table(
        headers=["Quarter", "Revenue", "YoY Growth", "Operating Margin"],
        rows=[
            ["Q1 2023", "4,312", "+6.1%", "21.2%"],
            ["Q2 2023", "4,687", "+7.8%", "22.0%"],
            ["Q3 2023", "4,619", "+8.5%", "22.4%"],
            ["Q4 2023", "5,124", "+11.2%", "24.0%"],
            ["Full Year 2023", "18,742", "+8.4%", "22.5%"],
        ],
        col_widths=[50, 40, 40, 40],
    )

    pdf.add_page()
    pdf.section_title("Cloud Services Deep Dive")
    pdf.body(
        "Cloud Services represented 40% of Q4 revenue, up from 33% in Q4 2022. "
        "The segment benefits from three compounding tailwinds: (1) existing on-premise "
        "customers migrating to cloud-native versions at an accelerating pace, (2) new logo "
        "acquisition driven by our AI-powered analytics suite launched in Q2 2023, and "
        "(3) expansion revenue from existing cloud customers increasing seat counts and "
        "storage consumption."
    )
    pdf.table(
        headers=["Cloud Metric", "Q4 2023", "Q4 2022", "YoY"],
        rows=[
            ["Cloud Revenue", "$2,052M", "$1,521M", "+34.9%"],
            ["% of Total Revenue", "40.0%", "33.0%", "+700 bps"],
            ["Annual Recurring Revenue", "$9,412M", "$7,234M", "+30.1%"],
            ["Net Revenue Retention", "118%", "112%", "+600 bps"],
            ["Customers > $1M ARR", "412", "318", "+29.6%"],
            ["Customers > $100K ARR", "3,241", "2,687", "+20.6%"],
        ],
        col_widths=[72, 34, 34, 30],
    )

    pdf.section_title("Q1 2024 Guidance")
    pdf.table(
        headers=["Metric", "Q1 2024 Guidance"],
        rows=[
            ["Revenue", "$5,050M - $5,150M"],
            ["Revenue Growth (YoY)", "17% - 19%"],
            ["Operating Income", "$1,160M - $1,210M"],
            ["Operating Margin", "22.5% - 23.5%"],
            ["Diluted EPS", "$2.16 - $2.26"],
        ],
        col_widths=[80, 90],
    )

    out = OUTPUT / "TechCorp_Q4_2023_Earnings.pdf"
    pdf.output(str(out))
    print(f"Created: {out}")


# ═══════════════════════════════════════════════════════════════════════════════
#  PDF 3 - Risk Assessment
# ═══════════════════════════════════════════════════════════════════════════════

def generate_risk_report():
    pdf = FinancialPDF("Risk Assessment Report 2023")
    pdf.cover("Enterprise Risk Assessment Report", "FY2023 | Internal Document")

    pdf.add_page()
    pdf.section_title("Risk Overview")
    pdf.body(
        "This report summarizes TechCorp's principal risk factors as assessed by the Enterprise "
        "Risk Management (ERM) team for fiscal year 2023. Risks are rated on a 5x5 matrix "
        "combining likelihood (1=Rare, 5=Almost Certain) and impact (1=Negligible, "
        "5=Catastrophic). Risk scores are the product of these two dimensions (max = 25)."
    )

    pdf.section_title("Top Risks Summary")
    pdf.table(
        headers=["Risk", "Category", "Likelihood", "Impact", "Score", "Trend"],
        rows=[
            ["AI Competition", "Strategic", "4", "5", "20", "Increasing"],
            ["Cybersecurity Breach", "Operational", "3", "5", "15", "Stable"],
            ["Key Talent Attrition", "People", "4", "4", "16", "Increasing"],
            ["Regulatory / GDPR", "Compliance", "3", "4", "12", "Increasing"],
            ["Customer Concentration", "Financial", "2", "5", "10", "Stable"],
            ["FX Rate Volatility", "Financial", "4", "3", "12", "Stable"],
            ["Supply Chain (Hardware)", "Operational", "2", "3", "6", "Decreasing"],
            ["Data Center Capacity", "Operational", "3", "3", "9", "Stable"],
            ["Interest Rate Risk", "Financial", "4", "2", "8", "Increasing"],
            ["Geopolitical (APAC)", "Strategic", "3", "4", "12", "Increasing"],
        ],
        col_widths=[52, 28, 22, 20, 18, 30],
    )

    pdf.add_page()
    pdf.section_title("1. Strategic Risk: AI Competition")
    pdf.kv("Risk Score", "20/25 - HIGH")
    pdf.kv("Risk Owner", "Chief Strategy Officer")
    pdf.body(
        "The rapid commoditization of AI capabilities poses an existential threat to TechCorp's "
        "Enterprise Software segment, which historically derived pricing power from proprietary "
        "algorithms now being replicated by open-source models. Competitors including HyperCloud "
        "Corp and DataSphere AI have launched directly competing products at 30-40% lower price "
        "points.\n\n"
        "Mitigation: $600M incremental R&D investment in FY2024 targeting AI-native product "
        "rebuilds. Strategic partnership with two Tier-1 LLM providers signed in December 2023. "
        "Target: maintain gross margin above 50% in Enterprise Software through FY2025."
    )

    pdf.section_title("2. Operational Risk: Cybersecurity")
    pdf.kv("Risk Score", "15/25 - HIGH")
    pdf.kv("Risk Owner", "Chief Information Security Officer")
    pdf.body(
        "As TechCorp processes over 4.2 petabytes of customer data daily across 18 data "
        "centers, cybersecurity incidents represent a material financial and reputational risk. "
        "The company experienced 3 attempted intrusions in FY2023 (vs 1 in FY2022), all "
        "successfully contained. Average cost of a data breach in the enterprise software "
        "sector is estimated at $4.7M per incident (IBM Security Report 2023).\n\n"
        "Mitigation: Security budget increased 34% to $187M in FY2023. Zero-trust architecture "
        "rollout 78% complete as of December 2023. SOC 2 Type II certification renewed in "
        "Q3 2023. Cyber insurance coverage: $250M per occurrence."
    )

    pdf.section_title("3. Financial Risk: Customer Concentration")
    pdf.kv("Risk Score", "10/25 - MEDIUM")
    pdf.kv("Risk Owner", "Chief Financial Officer")
    pdf.body(
        "TechCorp's top 10 customers represent 28% of total revenue ($5.2B). The largest "
        "single customer (FinServ Global) accounts for 6.1% of revenue under a contract "
        "expiring in Q3 2025. While renewal probability is assessed at 85%, non-renewal would "
        "reduce annual revenue by approximately $1.14B and trigger covenant testing on our "
        "revolving credit facility.\n\n"
        "Mitigation: Dedicated enterprise success team of 45 FTEs assigned to top-20 accounts. "
        "Product integration depth increased (average 4.2 modules per top-10 customer vs 2.8 "
        "in 2021). FinServ Global renewal negotiations commenced Q4 2023, preliminary feedback "
        "positive."
    )

    pdf.section_title("4. Financial Risk: FX Exposure")
    pdf.kv("Risk Score", "12/25 - MEDIUM")
    pdf.kv("Risk Owner", "VP Treasury")
    pdf.body(
        "With 50% of revenue derived outside North America, TechCorp has material exposure "
        "to EUR, GBP, JPY, and AUD. A 10% adverse movement in all currencies simultaneously "
        "would reduce reported revenue by approximately $940M and operating income by $210M.\n\n"
        "The company hedges approximately 60% of anticipated foreign currency cash flows on a "
        "rolling 12-month basis using forward contracts. Unhedged exposure of $3.7B represents "
        "the primary residual financial risk.\n\n"
        "FX headwind in FY2023: $(312)M on revenue, $(87)M on operating income."
    )

    out = OUTPUT / "TechCorp_Risk_Assessment_2023.pdf"
    pdf.output(str(out))
    print(f"Created: {out}")


# ═══════════════════════════════════════════════════════════════════════════════
#  CSVs
# ═══════════════════════════════════════════════════════════════════════════════

def generate_csvs():
    # 1. Monthly P&L (quarterly_financials.csv)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pd.DataFrame({
        "Month": months,
        "Revenue_USD_M": [1412, 1389, 1623, 1498, 1534, 1687, 1521, 1567, 1743, 1612, 1689, 1867],
        "COGS_USD_M": [748, 736, 860, 794, 813, 894, 806, 831, 924, 854, 895, 990],
        "Gross_Profit_USD_M": [664, 653, 763, 704, 721, 793, 715, 736, 819, 758, 794, 877],
        "EBITDA_USD_M": [423, 412, 498, 451, 467, 521, 462, 478, 543, 498, 521, 587],
        "Net_Income_USD_M": [284, 276, 341, 302, 312, 356, 308, 321, 367, 334, 352, 401],
    }).to_csv(OUTPUT / "quarterly_financials.csv", index=False)
    print(f"Created: quarterly_financials.csv")

    # 2. Sales by region x product x month
    sales_data = {
        ("North America", "Cloud Services"): [312, 328, 345, 361, 378, 401],
        ("North America", "Enterprise Software"): [421, 418, 435, 428, 441, 456],
        ("North America", "Professional Services"): [156, 148, 162, 154, 159, 167],
        ("Europe", "Cloud Services"): [187, 195, 208, 218, 228, 243],
        ("Europe", "Enterprise Software"): [234, 229, 241, 238, 245, 253],
        ("Europe", "Professional Services"): [89, 84, 92, 87, 91, 96],
        ("Asia Pacific", "Cloud Services"): [121, 128, 139, 148, 157, 169],
        ("Asia Pacific", "Enterprise Software"): [156, 152, 163, 159, 167, 174],
        ("Asia Pacific", "Professional Services"): [45, 42, 48, 46, 49, 53],
    }
    rows = []
    for (region, product), sales in sales_data.items():
        for month, amount in zip(months[:6], sales):
            rows.append({"Month": month, "Region": region, "Product": product, "Sales_USD_M": amount})
    pd.DataFrame(rows).to_csv(OUTPUT / "sales_by_region_product.csv", index=False)
    print(f"Created: sales_by_region_product.csv")

    # 3. Budget vs actuals
    departments = ["Engineering", "Sales", "Marketing", "Customer Success",
                    "G&A", "R&D", "Legal & Compliance", "IT Infrastructure"]
    budgets = [3240, 2180, 890, 1120, 760, 2100, 312, 680]
    actuals = [3412, 2034, 923, 1087, 1031, 2249, 298, 712]
    pd.DataFrame({
        "Department": departments,
        "Budget_USD_M": budgets,
        "Actual_USD_M": actuals,
        "Variance_USD_M": [a - b for a, b in zip(actuals, budgets)],
        "Variance_Pct": [round((a - b) / b * 100, 1) for a, b in zip(actuals, budgets)],
    }).to_csv(OUTPUT / "budget_vs_actuals.csv", index=False)
    print(f"Created: budget_vs_actuals.csv")

    # 4. 5-year annual financials
    pd.DataFrame({
        "Year": [2019, 2020, 2021, 2022, 2023],
        "Revenue_USD_M": [11_234, 12_891, 14_831, 17_289, 18_742],
        "Cost_of_Revenue_USD_M": [6_204, 7_012, 8_158, 8_990, 9_371],
        "Gross_Profit_USD_M": [5_030, 5_879, 6_673, 8_299, 9_371],
        "Gross_Margin_Pct": [44.8, 45.6, 45.0, 48.0, 50.0],
        "RnD_Expense_USD_M": [1_236, 1_432, 1_780, 2_075, 2_249],
        "SalesMarketing_USD_M": [1_123, 1_289, 1_631, 1_902, 1_874],
        "GA_Expense_USD_M": [421, 498, 594, 691, 1_031],
        "Operating_Income_USD_M": [2_250, 2_660, 2_668, 3_631, 4_217],
        "Operating_Margin_Pct": [20.0, 20.6, 18.0, 21.0, 22.5],
        "Net_Income_USD_M": [1_634, 1_923, 2_091, 2_918, 3_412],
        "Diluted_EPS_USD": [3.54, 4.21, 4.63, 6.54, 7.84],
        "Free_Cash_Flow_USD_M": [1_890, 2_234, 2_459, 3_245, 3_891],
        "Headcount_EoY": [18_200, 19_400, 23_100, 27_800, 29_400],
    }).to_csv(OUTPUT / "annual_financials.csv", index=False)
    print(f"Created: annual_financials.csv")

    # 5. Quarterly segments
    quarters = ["Q1-23", "Q2-23", "Q3-23", "Q4-23"] * 3
    segments = ["Cloud Services"] * 4 + ["Enterprise Software"] * 4 + ["Professional Services"] * 4
    pd.DataFrame({
        "Quarter": quarters,
        "Segment": segments,
        "Revenue_USD_M": [
            1_621, 1_789, 1_662, 2_052,
            1_987, 2_134, 2_147, 2_144,
            704, 764, 810, 928,
        ],
        "YoY_Growth_Pct": [
            28.4, 30.1, 31.2, 34.9,
            1.2, 2.8, 3.1, 2.8,
            -14.2, -12.8, -10.1, -10.5,
        ],
        "Gross_Margin_Pct": [
            68.2, 69.1, 68.9, 71.2,
            54.3, 54.8, 55.1, 56.0,
            22.1, 23.4, 24.2, 25.8,
        ],
    }).to_csv(OUTPUT / "quarterly_segments.csv", index=False)
    print(f"Created: quarterly_segments.csv")

    # 6. Monthly cash flow
    operating = [312, 287, 498, 341, 389, 512, 378, 412, 543, 489, 521, 630]
    investing = [-134, -87, -412, -98, -112, -143, -89, -134, -156, -98, -112, -150]
    financing = [-189, -143, -145, -167, -134, -187, -156, -198, -134, -189, -156, -314]
    pd.DataFrame({
        "Month": months,
        "Operating_Cash_Flow_USD_M": operating,
        "Investing_Cash_Flow_USD_M": investing,
        "Financing_Cash_Flow_USD_M": financing,
        "Net_Cash_Change_USD_M": [o + i + f for o, i, f in zip(operating, investing, financing)],
        "Cumulative_Cash_USD_M": [
            sum(o + i + f for o, i, f in zip(operating[:k+1], investing[:k+1], financing[:k+1])) + 5_631
            for k in range(12)
        ],
        "CapEx_USD_M": [67, 54, 98, 78, 81, 89, 74, 82, 91, 78, 76, 73],
    }).to_csv(OUTPUT / "monthly_cashflow_2023.csv", index=False)
    print(f"Created: monthly_cashflow_2023.csv")

    # 7. Investment portfolio
    pd.DataFrame({
        "Asset_Class": [
            "US Treasury Bills", "Corporate Bonds (AAA)", "Money Market Funds",
            "S&P 500 Index ETF", "International Equities", "Real Estate (REIT)",
            "Cash Equivalents",
        ],
        "Allocation_Pct": [22.0, 18.0, 15.0, 20.0, 12.0, 8.0, 5.0],
        "Market_Value_USD_M": [1_505, 1_232, 1_027, 1_369, 821, 548, 342],
        "Cost_Basis_USD_M": [1_500, 1_215, 1_027, 1_124, 756, 512, 342],
        "Unrealized_GL_USD_M": [5, 17, 0, 245, 65, 36, 0],
        "YTD_Return_Pct": [5.2, 4.8, 5.1, 26.3, 15.4, 8.7, 5.1],
        "Duration_Years": [0.5, 3.2, 0.1, None, None, None, 0.0],
        "Credit_Rating": ["AAA", "AAA", "AAA", None, None, None, "AAA"],
    }).to_csv(OUTPUT / "investment_portfolio.csv", index=False)
    print(f"Created: investment_portfolio.csv")

    # 8. Employee headcount by department and quarter
    depts = ["Engineering", "Sales", "Marketing", "Customer Success",
             "G&A", "R&D", "Legal", "IT Infrastructure"]
    pd.DataFrame({
        "Department": depts,
        "Q1_2023": [3_120, 1_412, 398, 645, 378, 956, 132, 289],
        "Q2_2023": [3_198, 1_398, 412, 651, 389, 978, 135, 293],
        "Q3_2023": [3_267, 1_392, 425, 654, 401, 1_002, 136, 295],
        "Q4_2023": [3_312, 1_389, 431, 658, 412, 1_021, 138, 298],
        "Attrition_Rate_Pct": [8.2, 12.4, 10.1, 9.8, 7.3, 6.9, 5.4, 8.7],
        "Open_Positions": [187, 45, 23, 34, 18, 89, 8, 12],
    }).to_csv(OUTPUT / "employee_headcount.csv", index=False)
    print(f"Created: employee_headcount.csv")


# ═══════════════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating sample financial data...\n")
    print("── PDFs ──")
    generate_annual_report()
    generate_q4_earnings()
    generate_risk_report()
    print("\n── CSVs ──")
    generate_csvs()
    print(f"\nAll files written to: {OUTPUT}")
