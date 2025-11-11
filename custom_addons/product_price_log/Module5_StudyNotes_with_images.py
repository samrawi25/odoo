from fpdf import FPDF
import os

# -----------------------------
# PDF Setup
# -----------------------------
pdf = FPDF('P', 'mm', 'A4')
pdf.set_auto_page_break(auto=True, margin=15)

# Add High Tower font
FONT_PATH_REGULAR = "C:/Windows/Fonts/HTOWERT.TTF"  # High Tower regular
FONT_PATH_BOLD = "C:/Windows/Fonts/HTOWERT.TTF"     # High Tower bold uses same file
if not os.path.exists(FONT_PATH_REGULAR):
    raise FileNotFoundError(f"Font file not found: {FONT_PATH_REGULAR}")
pdf.add_font('HighTower', '', FONT_PATH_REGULAR)
pdf.add_font('HighTower', 'B', FONT_PATH_BOLD)

# -----------------------------
# Title Page
# -----------------------------
pdf.add_page()
pdf.set_font("HighTower", 'B', 18)
pdf.cell(0, 15, "Module 5: Liquidity and Regulation", ln=True, align="C")
pdf.set_font("HighTower", '', 12)
pdf.ln(10)
pdf.multi_cell(0, 6, "Comprehensive Study Notes\n\nLessons 1–4\n\nPrepared for MSc Financial Engineering Students", align="C")

# -----------------------------
# Lessons and Diagram Placeholders
# -----------------------------
lessons = [
    ("Lesson 1: Securitization", [
        "- Key concepts: securitization, MBS, CDO, SPE/SPV",
        "- Mortgage origination: fully amortizing mortgages, credit risk, types (prime, subprime, ARM, jumbo)",
        "- Credit analysis: 5 Cs (Capacity, Capital, Character, Collateral, Conditions)",
        "- Securitization process: retail bank -> investment bank -> SPE -> investors",
        "- Tranches & waterfall: senior, mezzanine, equity, credit enhancement, prepayment/time tranching",
        "- Case study: Jacob’s mortgage, risk analysis using 5 Cs",
        "[Image: diagram1.png]",
        "[Image: diagram2.png]",
        "[Table: table1.png]"
    ]),
    ("Lesson 2: Valuation Challenges", [
        "- Market frictions: liquidity risk, transaction costs, funding constraints",
        "- Model risk: incorrect assumptions, parameter errors, ignoring tail risks",
        "- Real-world implications: financial crisis lessons, underestimating credit risk, illiquidity",
        "- Regulatory context: Dodd-Frank Act, rating agency reliance",
        "- Practical examples: MBS analysis, cash flows, risk-return selection, tranche prioritization",
        "- Key formulas: LTV, DTI, tranche loss allocation, prepayment impact",
        "- Visuals: MBS flow diagram, tranche waterfall, risk mitigation example",
        "[Image: diagram3.png]",
        "[Image: diagram4.png]",
        "[Table: table2.png]",
        "[Image: diagram5.png]"
    ]),
    ("Lesson 3: Liquidity and the Credit Market", [
        "- Credit Market Overview: bonds, corporate bonds, high-yield bonds, market size, liquidity",
        "- Credit Spreads & CDS: CS = yield - risk-free rate, PD = CS / (1 - RR), recovery rate, CDS mechanics, moral hazard examples",
        "- Ratings & Credit Spread: PD ↔ rating ↔ credit spread, lag of rating agencies, CDS spread as forward-looking signal",
        "- Liquidity Risk: bid-ask spread, volume, fungibility, liquidation horizon",
        "[Image: diagram6.png]",
        "[Image: diagram7.png]",
        "[Table: table3.png]",
        "[Image: diagram8.png]",
        "[Image: diagram9.png]"
    ]),
    ("Lesson 4: Leverage and Crisis", [
        "- Correlation & Market Dynamics: stock vs real estate, wealth effect, credit-price effect",
        "- Leverage Risk: margin trading, mortgages, corporate leverage, ETFs, swaps, DTI, LTV ratios",
        "- Regulation & Crisis: GFC lessons, moral hazard, centralized vs decentralized regulation, policy response",
        "- Conclusion: synthesis of correlation, leverage, liquidity, credit risk, regulation",
        "[Image: diagram10.png]",
        "[Image: diagram11.png]",
        "[Table: table4.png]",
        "[Image: diagram12.png]",
        "[Image: diagram13.png]"
    ])
]

# -----------------------------
# Add Lessons to PDF
# -----------------------------
for title, points in lessons:
    pdf.add_page()
    pdf.set_font("HighTower", 'B', 14)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_font("HighTower", '', 11)
    for point in points:
        # Check if point is an image or table placeholder
        if point.startswith("[Image:") or point.startswith("[Table:"):
            file_name = point.split(":")[1].strip().replace("]", "")
            try:
                pdf.ln(2)
                pdf.image(os.path.join("images", file_name), w=180)
                pdf.ln(5)
            except:
                pdf.multi_cell(0, 6, f"{point} (placeholder - file not found)")
        else:
            pdf.multi_cell(0, 6, point)
            pdf.ln(1)

# -----------------------------
# Save PDF
# -----------------------------
pdf_output_path = "Module5_HighTower_Study_Notes_17pages.pdf"
pdf.output(pdf_output_path)
print(f"✅ PDF generated successfully: {pdf_output_path}")
