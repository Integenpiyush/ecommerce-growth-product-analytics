"""
Generate Publication-Quality PDF for Interview Preparation Strategies
=====================================================================
Generates: reports/Project_Interview_Defense_Strategy.pdf
Covers:
  - 30-40 sec Elevator Pitch
  - 2-3 min Standard Interview Walkthrough
  - 10-15 min In-Depth Technical Defense
  - Synergy with MedTourEasy Experience
  - Quick-Reference Metric & Defense Cheat Sheet
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print running headers and 'Page X of Y' footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))

        # Running header on pages 2+
        if self._pageNumber > 1:
            self.drawString(36, letter[1] - 28, "E-COMMERCE GROWTH & PRODUCT ANALYTICS PLATFORM — INTERVIEW DEFENSE GUIDE")
            self.drawRightString(letter[0] - 36, letter[1] - 28, "CANDIDATE INTERVIEW PREPARATION")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(36, letter[1] - 32, letter[0] - 36, letter[1] - 32)

        # Running footer on all pages
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 36, 24, page_str)
        self.drawString(36, 24, "CONFIDENTIAL • PREPARED FOR SENIOR ANALYTICS & PRODUCT INTERVIEWS")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(36, 32, letter[0] - 36, 32)

        self.restoreState()


def build_pdf(filename="reports/Project_Interview_Defense_Strategy.pdf"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    # Palette
    c_primary = colors.HexColor("#1A365D")    # Navy
    c_secondary = colors.HexColor("#2B6CB0")  # Slate Blue
    c_accent = colors.HexColor("#22543D")     # Forest Green
    c_dark = colors.HexColor("#2D3748")       # Body text dark
    c_bg_box = colors.HexColor("#F7FAFC")     # Soft light background
    c_border_box = colors.HexColor("#CBD5E0") # Box border

    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=c_secondary,
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        fontName="Helvetica",
        fontSize=8.8,
        leading=12.2,
        textColor=c_dark,
        spaceAfter=5
    )
    script_style = ParagraphStyle(
        "Script_Custom",
        fontName="Helvetica-Oblique",
        fontSize=8.8,
        leading=12.5,
        textColor=colors.HexColor("#1A202C")
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.8,
        textColor=c_dark,
        leftIndent=12,
        spaceAfter=3
    )
    label_style = ParagraphStyle(
        "Label_Custom",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=c_primary
    )
    metric_label = ParagraphStyle(
        "MetricLabel",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=c_secondary
    )
    metric_val = ParagraphStyle(
        "MetricVal",
        fontName="Helvetica",
        fontSize=7.8,
        leading=10,
        textColor=c_dark
    )

    story = []

    # -------------------------------------------------------------------------
    # COVER / HEADER BLOCK
    # -------------------------------------------------------------------------
    story.append(Paragraph("E-COMMERCE GROWTH & PRODUCT ANALYTICS PLATFORM", title_style))
    story.append(Paragraph(
        "Master Project Interview Preparation Guide: 3 Spoken Strategies (30-40s, 2-3m, 10-15m) + Internship Synergy & Technical Defense",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=8))

    # Profile & Project Summary Grid
    header_data = [
        [
            Paragraph("<b>Candidate Profile:</b> Analytics & Data Science Professional", body_style),
            Paragraph("<b>Target Roles:</b> Senior Data Analyst | Product Analyst | Analytics Engineer", body_style)
        ],
        [
            Paragraph("<b>Prior Experience:</b> Data Science & Analytics Intern @ MedTourEasy", body_style),
            Paragraph("<b>Live Demo:</b> ecommerce-growth-product-analytics.streamlit.app", body_style)
        ],
        [
            Paragraph("<b>Flagship Project Scope:</b> 18,000 Orders | 30,000 Sessions | 12,000 A/B Users | $4.83M Net Revenue", body_style),
            Paragraph("<b>Tech Stack:</b> Python, PostgreSQL, SQLite, SQL (CTEs, Windows), Streamlit, SciPy, Pytest", body_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[270, 270])
    t_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EDF2F7")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    story.append(t_header)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # STRATEGY 1: 30-40 SECONDS ELEVATOR PITCH
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. STRATEGY 1: THE 30–40 SECOND ELEVATOR PITCH (THE HOOK)", h1_style))
    story.append(Paragraph(
        "<b>When to use:</b> 'Tell me about yourself', recruiter screening calls, 30-second portfolio introduction, or quick interview openers. "
        "<i>(Word count: ~95 words | Target speaking pace: ~35 seconds).</i>",
        body_style
    ))

    script_1_text = (
        "\"I built an end-to-end <b>E-commerce Growth & Product Analytics Platform</b> analyzing $4.83M in revenue across "
        "18,000 orders and 30,000 clickstream sessions. Architected on a Kimball Star Schema with a 33-check automated data quality gate, "
        "the platform uncovered critical commercial bottlenecks: an <b>8.29% vs. 15.42% mobile conversion gap</b> driven by checkout friction, "
        "and a $999K operational refund drag. To resolve this, I evaluated a randomized <b>1-step checkout A/B experiment across 12,000 users</b>, "
        "proving a statistically significant <b>+1.32% absolute lift (p = 0.0455)</b> that unlocked over <b>$128,000 in projected annual revenue</b>, "
        "all visualized in an interactive 5-page Streamlit dashboard.\""
    )
    box_1 = Table([[Paragraph(script_1_text, script_style)]], colWidths=[540])
    box_1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3182CE")),
        ("PADDING", (0, 0), (-1, -1), 7)
    ]))
    story.append(box_1)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Breakdown of Why This Script Works:</b>", label_style))
    story.append(Paragraph("• <b>Hook & Scale (0–10s):</b> Establishes domain ($4.83M e-commerce) and scale (18K orders, 30K clickstream sessions).", bullet_style))
    story.append(Paragraph("• <b>Technical Credibility (10–20s):</b> Mentions Kimball Star Schema, automated quality engineering, and mobile funnel diagnostics.", bullet_style))
    story.append(Paragraph("• <b>Statistical Rigor & ROI (20–35s):</b> Cites exact hypothesis test numbers (+$1.32% lift, p = 0.0455) and ties directly to bottom-line financial impact ($128K+).", bullet_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # STRATEGY 2: 2-3 MINUTES STANDARD INTERVIEW WALKTHROUGH
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. STRATEGY 2: THE 2–3 MINUTE STRUCTURED WALKTHROUGH (STAR / CAR)", h1_style))
    story.append(Paragraph(
        "<b>When to use:</b> 'Walk me through a project you're most proud of', 'Tell me about a challenging analytical problem you solved', "
        "Technical Round 1, or Hiring Manager interviews. <i>(Word count: ~410 words | Target speaking pace: ~2.5 minutes).</i>",
        body_style
    ))

    script_2_p1 = (
        "<b>[Context & Problem — 35s]:</b><br/>"
        "\"In my recent flagship project, I engineered an end-to-end <b>E-commerce Growth & Product Analytics Platform</b> to solve three core commercial challenges: "
        "diagnosing why mid-year revenue decelerated by 6.2%, mapping severe clickstream funnel drop-offs, and optimizing marketing capital allocation across $470K in ad spend. "
        "The business generated $4.83M in net revenue across 14,978 completed orders, but faced a massive $999K operational refund drag from cancellations (6.74%) and returns (10.05%).\""
    )
    script_2_p2 = (
        "<b>[Architecture & Data Engineering — 45s]:</b><br/>"
        "\"To create a single source of truth, I architected a <b>Kimball Star Schema data warehouse</b> separating conformed dimensions (customers, products, calendar dates) "
        "from transaction, session, and marketing fact tables. I implemented a production ETL pipeline in Python and SQLAlchemy featuring a <b>33-check automated data quality gate</b> "
        "that enforces primary key uniqueness, non-negative monetary bounds, chronological validity, and referential integrity before database ingestion. "
        "I then wrote modular SQL models using advanced CTEs, <code>LAG()</code> window functions for MoM growth, rolling 7-day revenue averages, and <code>NTILE(5)</code> quintiles for customer RFM segmentation.\""
    )
    script_2_p3 = (
        "<b>[Product Analytics & A/B Experimentation — 50s]:</b><br/>"
        "\"By analyzing 30,000 clickstream sessions across 5 funnel milestones, I uncovered that the primary friction point was <b>View-to-Cart (55.7% drop-off)</b>, "
        "and that <b>Mobile conversion was lagging at 8.29% compared to 15.42% on Desktop</b>. Mobile users represented 66% of site traffic but dropped off heavily at checkout due to touchscreen form fatigue.<br/>"
        "To test a solution, I evaluated a randomized controlled trial testing a <b>1-step checkout flow against the existing 2-step control across 12,000 users</b>. "
        "Using a two-sample pooled proportion Z-test at alpha = 0.05, Treatment achieved an <b>absolute conversion lift of +1.32% (16.38% vs. 15.06%, p = 0.04547, Z = 2.0003)</b>. "
        "The 95% confidence interval of [+0.03%, +2.63%] strictly excluded zero. Crucially, I monitored <b>Average Revenue Per User (ARPU) via Welch's t-test</b> as a guardrail metric, "
        "confirming that ARPU grew by +$1.04 per visitor without degrading average basket size.\""
    )
    script_2_p4 = (
        "<b>[Business Impact & Production Delivery — 40s]:</b><br/>"
        "\"Based on these empirical findings, I delivered three key business actions: first, recommended full rollout of the 1-step checkout, capturing <b>$128,000+ in annual incremental revenue</b>; "
        "second, identified that <b>Affiliate marketing had an inflated $485 CAC and 3.65x ROAS</b> (barely clearing our 42% product margin hurdle), recommending reallocating $30,000 to <b>Paid Search (7.03x ROAS, +$430K contribution profit)</b>; "
        "and third, deployed an interactive <b>5-page Streamlit dashboard with Plotly visuals and automated Pytest CI/CD testing</b> so executive stakeholders could dynamically filter metrics by date, device, and channel.\""
    )

    t_script_2 = Table([
        [Paragraph(script_2_p1, body_style)],
        [Paragraph(script_2_p2, body_style)],
        [Paragraph(script_2_p3, body_style)],
        [Paragraph(script_2_p4, body_style)]
    ], colWidths=[540])
    t_script_2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#E2E8F0"))
    ]))
    story.append(t_script_2)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # STRATEGY 3: 10-15 MINUTES IN-DEPTH TECHNICAL & ARCHITECTURAL DEFENSE
    # -------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("3. STRATEGY 3: THE 10–15 MINUTE IN-DEPTH TECHNICAL & SYSTEM DEFENSE", h1_style))
    story.append(Paragraph(
        "<b>When to use:</b> Final round panel interviews, technical deep-dive case presentations, lead data scientist grilling, "
        "or architecture defense sessions. Structured into 6 progressive phases with exact mathematical proofs, schemas, and trade-offs.",
        body_style
    ))

    # Phase 1
    story.append(Paragraph("Phase 1: Problem Definition & Financial Decomposition (2 Minutes)", h2_style))
    story.append(Paragraph(
        "Start by walking the interviewers through the mathematical decomposition of top-line revenue into its operational levers:",
        body_style
    ))
    formula_1 = (
        "<b>Core Revenue Decomposition Formula:</b><br/>"
        "$$\\text{Net Revenue} = \\text{Traffic Sessions} \\times \\text{Conversion Rate} \\times \\text{AOV} \\times (1 - \\text{Cancellation Rate}) \\times (1 - \\text{Return Rate})$$<br/>"
        "• <b>Gross GMV:</b> $5,069,551.90 | <b>Promotional Discounts:</b> $235,760.27 (4.65% discount depth)<br/>"
        "• <b>Net Invoiced Revenue:</b> $4,833,791.63 | <b>COGS:</b> $2,799,216.92 | <b>Gross Profit:</b> $2,034,574.71 (42.09% Gross Margin)<br/>"
        "• <b>Operational Leakage Drag:</b> 1,213 cancellations (6.74%, $389K lost) + 1,809 returns (10.05%, $610K refunded) = <b>$999,800.95 in total refund drag</b>.<br/>"
        "• <i>Defense Argument:</i> Mid-year revenue deceleration was NOT a top-of-funnel demand failure (traffic and $322 AOV were steady), "
        "but an operational fulfillment failure: 58% of apparel returns were driven by 'Wrong Size / Fit' and shipping transit times exceeding 5 days."
    )
    t_f1 = Table([[Paragraph(formula_1, body_style)]], colWidths=[540])
    t_f1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEFCBF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D69E2E")),
        ("PADDING", (0, 0), (-1, -1), 6)
    ]))
    story.append(t_f1)
    story.append(Spacer(1, 8))

    # Phase 2
    story.append(Paragraph("Phase 2: Relational Data Modeling & ETL Quality Gate (3 Minutes)", h2_style))
    story.append(Paragraph(
        "Explain how the data warehouse was architected to eliminate analytical bottlenecks and prevent reporting errors:",
        body_style
    ))
    schema_points = [
        "<b>Kimball Star Schema Justification:</b> Decouples business measurements (fact tables) from context (conformed dimension tables). Unlike 3NF normalized structures that require 8+ table joins, the Star Schema allows single-level joins with B-tree index scans on foreign keys.",
        "<b>Table Grains:</b> <code>dim_customers</code> (1 row per user), <code>dim_products</code> (1 row per SKU), <code>dim_dates</code> (1 row per calendar day), <code>fact_orders</code> (1 row per order transaction), <code>fact_order_items</code> (1 row per item SKU per order), <code>fact_sessions</code> (1 row per visit), <code>fact_marketing_spend</code> (1 row per channel per day).",
        "<b>Preventing the 'Fan-Out' Trap:</b> Joining <code>fact_orders</code> directly to <code>fact_order_items</code> multiplies order-level metrics (shipping, discounts, net amount) by the item count. Defended by aggregating line items to order grain in a CTE before joining, or querying <code>fact_orders</code> exclusively for financial KPIs.",
        "<b>33-Check Automated Quality Gate:</b> Programmatic validation in <code>src/etl_pipeline.py</code> halting execution on duplicate PKs, null values in foreign keys, negative amounts, math discrepancies (|Gross - Discount - Net| > 0.02), or orphan records."
    ]
    for sp in schema_points:
        story.append(Paragraph(f"• {sp}", bullet_style))
    story.append(Spacer(1, 8))

    # Phase 3
    story.append(Paragraph("Phase 3: Advanced SQL Analytics & Customer Lifetime Modeling (2.5 Minutes)", h2_style))
    story.append(Paragraph(
        "Detail your technical SQL query design, window functions, and customer segmentation logic:",
        body_style
    ))
    sql_points = [
        "<b>MoM Revenue Growth:</b> Used <code>LAG(monthly_revenue, 1) OVER (ORDER BY order_month)</code> to compare sequential periods without expensive self-joins, wrapped in <code>NULLIF()</code> to prevent division-by-zero on initial cohorts.",
        "<b>Rolling Moving Averages:</b> Used <code>AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)</code>. Defended why an uninterrupted calendar dimension (<code>dim_dates</code>) is essential so weekends with zero sales do not skip window rows.",
        "<b>RFM Segmentation:</b> Computed Recency (days to 2024-12-31), Frequency (completed orders), and Monetary spend. Discretized into quintiles via <code>NTILE(5)</code> in SQL and <code>pd.qcut()</code> in Python. Discovered that <b>Champions (19.3% of customers) generate 67.75% of total revenue ($3.27M)</b>, proving massive revenue concentration.",
        "<b>Cohort Retention Matrix:</b> Built a 3-step CTE computing first purchase month (<code>MIN(order_month)</code>), month distance index <code>((year_diff * 12) + month_diff)</code>, and distinct active user retention percentages. Retention dropped to 48.2% in Month 1, stabilizing at 40%–50% in months 2–6."
    ]
    for sp in sql_points:
        story.append(Paragraph(f"• {sp}", bullet_style))
    story.append(Spacer(1, 8))

    # Phase 4
    story.append(Paragraph("Phase 4: Product Clickstream Funnel Diagnostics (2.5 Minutes)", h2_style))
    story.append(Paragraph(
        "Walk the panel through how clickstream session events were analyzed to isolate product friction:",
        body_style
    ))
    funnel_box_text = (
        "<b>5-Stage Clickstream Progression (30,000 Total Sessions):</b><br/>"
        "1. <b>Session Start:</b> 30,000 users (100.0%)<br/>"
        "2. <b>View Item:</b> 21,399 users (71.3% CR, 28.7% drop-off)<br/>"
        "3. <b>Add to Cart:</b> 9,479 users (44.3% step CR, <b>55.70% drop-off — PRIMARY BOTTLENECK</b>)<br/>"
        "4. <b>Begin Checkout:</b> 5,097 users (53.8% step CR, 46.2% drop-off)<br/>"
        "5. <b>Purchase Completed:</b> 3,097 users (60.8% step CR, 39.2% drop-off) $\\to$ <b>Overall End-to-End CR: 10.32%</b><br/>"
        "• <b>Device Disparity:</b> Desktop converted at <b>15.42%</b> while Mobile converted at only <b>8.29%</b> (Desktop 1.86x higher). "
        "Mobile represented 65.8% of visits (19,742 sessions) but generated only 53.2% of orders due to touchscreen checkout friction."
    )
    t_f4 = Table([[Paragraph(funnel_box_text, body_style)]], colWidths=[540])
    t_f4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0FFF4")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#38A169")),
        ("PADDING", (0, 0), (-1, -1), 6)
    ]))
    story.append(t_f4)
    story.append(Spacer(1, 8))

    # Phase 5
    story.append(Paragraph("Phase 5: Controlled Experimentation & Statistical Rigor (3 Minutes)", h2_style))
    story.append(Paragraph(
        "Defend the statistical mechanics of the A/B test with full mathematical precision:",
        body_style
    ))
    stat_proof = (
        "<b>A/B Experiment: 'checkout_one_step_v2' (N = 12,000 Randomized Users):</b><br/>"
        "• <b>Hypotheses:</b> $H_0: p_{\\text{treatment}} - p_{\\text{control}} = 0$ vs. $H_1: p_{\\text{treatment}} - p_{\\text{control}} \\ne 0$ (Two-sided test, $\\alpha = 0.05$).<br/>"
        "• <b>Control (2-Step):</b> $N_1 = 6,043$, Conversions $X_1 = 910$, $\\hat{p}_1 = 15.06\\%$.<br/>"
        "• <b>Treatment (1-Step):</b> $N_2 = 5,957$, Conversions $X_2 = 976$, $\\hat{p}_2 = 16.38\\%$.<br/>"
        "• <b>Observed Lift:</b> Absolute Lift $\\Delta = +1.32\\%$ (+0.0132); Relative Lift = $+8.83\\%$.<br/>"
        "• <b>Pooled Proportion:</b> $\\hat{p}_{pool} = (910 + 976) / 12,000 = 0.15717$.<br/>"
        "• <b>Pooled Standard Error:</b> $SE = \\sqrt{0.15717(1 - 0.15717)(1/6,043 + 1/5,957)} = 0.00665$.<br/>"
        "• <b>Z-Statistic & P-Value:</b> $Z = 0.01325 / 0.00665 = \\mathbf{2.0003} \\implies \\mathbf{p = 0.04547} < 0.05$ (Statistically Significant).<br/>"
        "• <b>95% Confidence Interval for Absolute Lift:</b> $\\Delta \\pm 1.96 \\times SE_{unpooled} = \\mathbf{[+0.03\\%, +2.63\\%]}$ (Relative: $[+0.21\\%, +17.48\\%]$). "
        "Strictly excludes zero.<br/>"
        "• <b>Guardrail Metric (Welch's t-Test for ARPU):</b> Control ARPU = $12.66; Treatment ARPU = $13.70 (+$1.04 lift, $t=1.602, p=0.109$). "
        "While ARPU has higher variance and did not reach $\\alpha=0.05$ significance, it trended positively, confirming no basket degradation.<br/>"
        "• <b>Subgroup Heterogeneity:</b> Mobile drove the win with a <b>+18.4% relative lift (p = 0.012)</b>, validating the UX friction hypothesis."
    )
    t_f5 = Table([[Paragraph(stat_proof, body_style)]], colWidths=[540])
    t_f5.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF5F5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E53E3E")),
        ("PADDING", (0, 0), (-1, -1), 6)
    ]))
    story.append(t_f5)
    story.append(Spacer(1, 8))

    # Phase 6
    story.append(Paragraph("Phase 6: Commercial Strategy, Limitations & Production Scaling (2 Minutes)", h2_style))
    story.append(Paragraph(
        "Conclude with commercial business recommendations and realistic engineering scaling trade-offs:",
        body_style
    ))
    scale_points = [
        "<b>Marketing Capital Optimization:</b> Evaluated $472K spend. Paid Search produced <b>7.03x ROAS ($411 CAC, +$430K contribution profit)</b>, while Affiliate generated <b>3.65x ROAS ($485 CAC, +$29.6K profit)</b>. Defended break-even ROAS formula: $1 / \\text{Gross Margin} = 1 / 0.4209 = 2.38\\text{x}$, which rises to ~3.2x after accounting for 10% returns and payment processing. Recommended reallocating $30,000 from Affiliate to Paid Search (+ $100.5K GMV).",
        "<b>Merchandising Mix Dynamics:</b> Electronics generated highest revenue ($1.56M) but compressed margins (31.55%, $491K profit). Home & Living generated more absolute profit ($517K, 46.38% margin) on lower revenue ($1.11M). Recommended bundling high-margin accessories and raising free shipping threshold on electronics from $75 to $99.",
        "<b>Scaling Bottlenecks (18K to 18M Orders):</b> Single-node Pandas and SQLite would fail due to OOM memory errors and write locks. Production redesign: ingest clickstream events via <b>Apache Kafka</b>, store in a distributed columnar warehouse (<b>Snowflake / BigQuery</b>), transform metrics incrementally using <b>dbt models</b>, and pre-aggregate OLAP cubes for sub-second BI response."
    ]
    for sp in scale_points:
        story.append(Paragraph(f"• {sp}", bullet_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # RESUME SYNERGY SECTION: BRIDGING MEDTOUREASY WITH THIS PROJECT
    # -------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("4. RESUME SYNERGY: BRIDGING MEDTOUREASY WITH THIS E-COMMERCE PLATFORM", h1_style))
    story.append(Paragraph(
        "How to seamlessly integrate your prior internship at <b>MedTourEasy</b> with this <b>E-commerce Growth Platform</b> "
        "to tell a cohesive, credible story of progressive senior analytical capability:",
        body_style
    ))

    synergy_table_data = [
        [
            Paragraph("<b>Core Analytical Competency</b>", label_style),
            Paragraph("<b>Internship: MedTourEasy (Healthcare Analytics)</b>", label_style),
            Paragraph("<b>Flagship Project: E-commerce Growth Platform</b>", label_style)
        ],
        [
            Paragraph("<b>Funnel & Drop-Off Analytics</b>", body_style),
            Paragraph("Engineered Python/SQL pipeline across 1,500 patient journeys; identified SLA conversion bottlenecks.", body_style),
            Paragraph("Constructed 5-stage clickstream funnel across 30,000 sessions; isolated 55.7% drop-off at cart & 8.3% vs 15.4% mobile gap.", body_style)
        ],
        [
            Paragraph("<b>Statistical Testing & Hypothesis Rigor</b>", body_style),
            Paragraph("Quantified 16.7 pp SLA conversion gap (62.7% vs. 79.5%) using Chi-square testing (p < 0.001).", body_style),
            Paragraph("Executed Two-Sample Pooled Z-Test (Z = 2.0003, p = 0.0455) & Welch's t-test on ARPU across 12,000 A/B experiment users.", body_style)
        ],
        [
            Paragraph("<b>Customer / User Segmentation</b>", body_style),
            Paragraph("Segmented 1,500 patients into 3 personas using K-Means on intent, engagement, response time, and value.", body_style),
            Paragraph("Discretized 2,095 buyers into 8 RFM lifecycle tiers via <code>NTILE(5)</code> quintiles; revealed Champions drive 67.8% of revenue.", body_style)
        ],
        [
            Paragraph("<b>Data Engineering & Architecture</b>", body_style),
            Paragraph("Integrated 5 raw datasets in Python/SQL with leakage-aware feature engineering (0.8695 ROC-AUC).", body_style),
            Paragraph("Architected Kimball Star Schema warehouse (8 tables) with 33-check automated quality gate & Pytest CI/CD.", body_style)
        ]
    ]
    t_syn = Table(synergy_table_data, colWidths=[110, 215, 215])
    t_syn.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]))
    story.append(t_syn)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>The Unified Career Narrative to Speak in Interviews:</b>", label_style))
    narrative_text = (
        "\"Across my analytics career, I focus on transforming messy relational event data into statistically validated commercial growth. "
        "At <b>MedTourEasy</b>, I focused on patient funnel friction, using Chi-square statistical testing to prove that a 16.7 percentage point "
        "SLA response gap was driving conversion attrition, and used K-Means to segment high-intent patient personas. "
        "Building upon that foundation, in my <b>E-commerce Growth & Product Analytics Platform</b>, I scaled these competencies to an enterprise "
        "retail ecosystem: architecting a Kimball Star Schema data warehouse with automated quality gates, applying advanced SQL window functions "
        "and RFM lifetime segmentation, and running controlled A/B experimentation with two-sample Z-tests and Welch's t-tests that drove $128K+ in incremental annual revenue.\""
    )
    box_narrative = Table([[Paragraph(narrative_text, script_style)]], colWidths=[540])
    box_narrative.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#4A5568")),
        ("PADDING", (0, 0), (-1, -1), 7)
    ]))
    story.append(box_narrative)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # MASTER METRICS & DEFENSE CHEAT SHEET
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. MASTER PROJECT METRICS & DEFENSE CHEAT SHEET", h1_style))
    story.append(Paragraph(
        "Keep these exact verified numbers memorized for rapid-fire technical cross-examination:",
        body_style
    ))

    cheat_sheet_data = [
        [
            Paragraph("<b>Metric Name</b>", metric_label),
            Paragraph("<b>Verified Value</b>", metric_label),
            Paragraph("<b>Underlying Formula / SQL Implementation</b>", metric_label),
            Paragraph("<b>Interview Defense Context</b>", metric_label)
        ],
        [
            Paragraph("Net Revenue", metric_label),
            Paragraph("$4,833,791.63", metric_val),
            Paragraph("<code>SUM(CASE WHEN status='Completed' THEN net_amount END)</code>", metric_val),
            Paragraph("Net of $235.8K in promotional discounts across 14,978 completed orders.", metric_val)
        ],
        [
            Paragraph("Gross Profit / Margin", metric_label),
            Paragraph("$2,034,574.71 (42.09%)", metric_val),
            Paragraph("<code>(net_amount - total_cogs) / net_amount * 100</code>", metric_val),
            Paragraph("Healthy retail margin; COGS is 57.91% ($2.80M).", metric_val)
        ],
        [
            Paragraph("Average Order Value", metric_label),
            Paragraph("$322.73", metric_val),
            Paragraph("<code>net_revenue / completed_orders</code>", metric_val),
            Paragraph("Basket size stayed steady across quarters; revenue drop wasn't AOV decay.", metric_val)
        ],
        [
            Paragraph("Repeat Purchase Rate", metric_label),
            Paragraph("76.55%", metric_val),
            Paragraph("<code>COUNT(buyers with >=2 orders) / active_buyers</code>", metric_val),
            Paragraph("1,604 of 2,095 ordering customers repeat-purchased; strong product stickiness.", metric_val)
        ],
        [
            Paragraph("Operational Leakage", metric_label),
            Paragraph("$999,800.95 (16.79%)", metric_val),
            Paragraph("Cancelled ($389.5K) + Returned ($610.4K)", metric_val),
            Paragraph("1,213 cancels (6.74%) + 1,809 returns (10.05%); sizing & delivery transit delays.", metric_val)
        ],
        [
            Paragraph("End-to-End Funnel CR", metric_label),
            Paragraph("10.32%", metric_val),
            Paragraph("<code>3,097 purchases / 30,000 sessions</code>", metric_val),
            Paragraph("Desktop: 15.42% vs Mobile: 8.29% (Desktop converts 1.86x higher).", metric_val)
        ],
        [
            Paragraph("A/B Conversion Lift", metric_label),
            Paragraph("+1.32% abs (+8.83% rel)", metric_val),
            Paragraph("Treatment: 16.38% vs Control: 15.06%", metric_val),
            Paragraph("Two-sample pooled Z-test: Z = 2.0003, p = 0.04547 < 0.05 (Significant).", metric_val)
        ],
        [
            Paragraph("A/B Confidence Interval", metric_label),
            Paragraph("[+0.03%, +2.63%]", metric_val),
            Paragraph("<code>delta +- 1.96 * SE_unpooled</code>", metric_val),
            Paragraph("95% CI strictly excludes zero; confirms positive true effect size.", metric_val)
        ],
        [
            Paragraph("A/B ARPU Guardrail", metric_label),
            Paragraph("+$1.04 (+8.20%)", metric_val),
            Paragraph("Treatment: $13.70 vs Control: $12.66", metric_val),
            Paragraph("Welch's t-test: t = 1.602, p = 0.109; proved checkout didn't cannibalize basket.", metric_val)
        ],
        [
            Paragraph("RFM Champions Share", metric_label),
            Paragraph("67.75% of revenue", metric_val),
            Paragraph("<code>NTILE(5)</code> score: R>=4, F>=4, M>=4", metric_val),
            Paragraph("404 users (19.3% of buyers) generate $3.27M; requires VIP retention safeguards.", metric_val)
        ],
        [
            Paragraph("Paid Search Efficiency", metric_label),
            Paragraph("7.03x ROAS ($411 CAC)", metric_val),
            Paragraph("Spend: $220.8K $\\to$ Revenue: $1.55M", metric_val),
            Paragraph("+$430.6K net contribution profit; primary scaling acquisition channel.", metric_val)
        ],
        [
            Paragraph("Affiliate Inefficiency", metric_label),
            Paragraph("3.65x ROAS ($485 CAC)", metric_val),
            Paragraph("Spend: $55.3K $\\to$ Revenue: $202.0K", metric_val),
            Paragraph("Barely cleared ~3.2x operational hurdle; reallocated $30K to Paid Search.", metric_val)
        ]
    ]
    t_cheat = Table(cheat_sheet_data, colWidths=[95, 105, 170, 170])
    t_cheat.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 3.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    story.append(t_cheat)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {filename}")


if __name__ == "__main__":
    build_pdf()
