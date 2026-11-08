# 06. Progressive Mock Interview Simulation System

This system provides a structured 6-level interview simulation. To get the maximum benefit:
1. **Read one question at a time.**
2. **Speak or write your answer out loud before scrolling to the evaluation rubric.**
3. **Score yourself against the 5-point evaluation criteria (Correctness, Clarity, Depth, Business Thinking, Communication).**
4. **Study the improved answer and common mistakes.**

```
+-------------------------------------------------------+
| LEVEL 1: High-Level Elevator Pitch & Overview         |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
| LEVEL 2: SQL & Python Technical Grilling              |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
| LEVEL 3: Product Analytics & Funnel Diagnostics       |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
| LEVEL 4: Executive Business Cases & Resource Allocation|
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
| LEVEL 5: Statistics, Power & Experimentation Rigor    |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
| LEVEL 6: System Architecture & Defensive Stress-Test  |
+-------------------------------------------------------+
```

---

## Level 1: Project Overview & Elevator Pitch

### The Question
> *"Can you give me a 90-second overview of this project, why you built it, and what key business insights it uncovered?"*

#### Self-Evaluation Rubric (Score each from 1 to 5):
- [ ] **Correctness**: Did you state accurate project metrics ($4.83M revenue, 18,000 orders, 10.05% return rate, +1.32% A/B test lift)?
- [ ] **Clarity**: Did you structure your answer chronologically (Context $\to$ Action $\to$ Results)?
- [ ] **Depth**: Did you mention the tech stack (Postgres/SQLite, Python, Streamlit, SciPy)?
- [ ] **Business Thinking**: Did you highlight executive impact rather than just technical tools?
- [ ] **Communication**: Did you stay within 90 seconds without filler words?

<details>
<summary>🔍 Click to Reveal Benchmark Evaluation & Ideal Answer</summary>

#### Common Mistakes
- Spending 80 seconds listing Python packages without mentioning what business problems were solved.
- Forgetting to mention the specific business findings (e.g. mobile funnel drop-off or marketing reallocation).

#### Ideal Answer
> "I built an end-to-end E-commerce Growth & Product Analytics Platform designed to answer critical commercial questions: why revenue accelerates or decelerates, where users drop off in the product funnel, and how to allocate marketing capital efficiently.
> 
> The architecture ingests a reproducible 2,500-customer, 18,000-order dataset into a Kimball Star Schema analytical database. I implemented an automated ETL pipeline with a 33-test data quality audit gate, followed by modular SQL and Python analytics engines covering financial KPIs, RFM customer segmentation, cohort retention, and a 5-page interactive Streamlit dashboard.
> 
> The analysis revealed three pivotal findings:
> 1. While Mobile generated 66% of traffic, it converted at only 8.3% compared to Desktop's 15.4%, primarily due to checkout form friction.
> 2. Operational leakage was substantial: 10.05% of orders were returned, heavily driven by apparel sizing mismatches, creating a $610K refund drag.
> 3. We executed a randomized controlled A/B test on a 1-step checkout flow across 12,000 users, proving a statistically significant +1.32% absolute lift in conversion rate (p = 0.0455), unlocking an estimated $128,000 in incremental annual top-line revenue."
</details>

---

## Level 2: Technical SQL & Python Grilling

### The Question
> *"Walk me through the exact SQL logic you used to build the Monthly Cohort Retention Matrix. How did you index the months, and how did you prevent customer order duplication?"*

#### Self-Evaluation Rubric:
- [ ] **Correctness**: Explained finding first order month per customer via `MIN()`.
- [ ] **Clarity**: Detailed the month distance formula: `((year_diff * 12) + month_diff)`.
- [ ] **Depth**: Mentioned distinct customer counting (`COUNT(DISTINCT customer_id)`).
- [ ] **Business Thinking**: Explained dividing by Month 0 base size to yield retention percentages.
- [ ] **Communication**: Articulated CTE structure cleanly.

<details>
<summary>🔍 Click to Reveal Benchmark Evaluation & Ideal Answer</summary>

#### Common Mistakes
- Claiming that subtracting order dates directly (`order_date - first_date`) gives monthly cohorts (it gives days, not month buckets).
- Counting total orders instead of distinct active customers, which inflates retention if one user makes 5 orders in month 2.

#### Ideal Answer
> "I structured the cohort retention logic into 3 Common Table Expressions (CTEs):
> 
> In CTE 1 (`customer_cohort`), I found each customer's acquisition cohort by taking the minimum completed order month: `MIN(SUBSTR(order_date, 1, 7)) AS cohort_month`.
> 
> In CTE 2 (`order_activity`), I joined all completed orders back to the customer cohort table. To calculate the month distance index regardless of calendar year boundaries, I used the integer formula:
> `((CAST(SUBSTR(order_date, 1, 4) AS INT) - CAST(SUBSTR(cohort_month, 1, 4) AS INT)) * 12 + (CAST(SUBSTR(order_date, 6, 2) AS INT) - CAST(SUBSTR(cohort_month, 6, 2) AS INT))) AS month_number`. This correctly marks the acquisition month as 0, the next month as 1, and so on.
> 
> In CTE 3, I grouped by `cohort_month` and `month_number`, aggregating `COUNT(DISTINCT customer_id)`. Crucially, using `COUNT(DISTINCT)` prevents double-counting customers who place multiple orders in the same month.
> 
> Finally, I pivoted the result and divided active users by the cohort's Month 0 base size to obtain retention percentages."
</details>

---

## Level 3: Product Analytics & Funnel Diagnostics

### The Question
> *"You observed that Mobile conversion (8.29%) is nearly half of Desktop conversion (15.42%). How did you diagnose where the drop-off occurs, and how do you know this isn't just cross-device browsing?"*

#### Self-Evaluation Rubric:
- [ ] **Correctness**: Identified the exact funnel stages: View $\to$ Cart and Cart $\to$ Checkout.
- [ ] **Clarity**: Distinguished between session-level drop-off and cross-device journeys.
- [ ] **Depth**: Discussed UX differences (screen real estate, form friction, mobile keyboard).
- [ ] **Business Thinking**: Recommended specific mobile optimizations (sticky CTA, Apple/Google Pay).
- [ ] **Communication**: Structured diagnosis logically from top-to-bottom of funnel.

<details>
<summary>🔍 Click to Reveal Benchmark Evaluation & Ideal Answer</summary>

#### Ideal Answer
> "To isolate the breakdown, I calculated stage-to-stage drop-off rates across all 5 milestones.
> 
> The data revealed two acute drop-off points:
> 1. **PDP to Cart**: Mobile users dropped off at 58.2% compared to 51.4% on Desktop. On mobile viewports, reviews, specs, and add-to-cart buttons were pushed below the fold, creating browsing friction.
> 2. **Checkout Completion**: Desktop checkout-to-purchase conversion was 66.8%, whereas Mobile was 57.4%. Entering shipping addresses and credit card numbers on a small mobile touchscreen causes user abandonment.
> 
> Regarding cross-device browsing: while some users do browse on mobile and buy on desktop, our session data showed that mobile session duration for non-converters averaged under 90 seconds with only 2 pageviews, indicating high bounce rather than deep research.
> 
> We addressed this by designing the 1-step checkout experiment with autofill and sticky CTAs, which subsequently proved an +18.4% relative lift on Mobile."
</details>

---

## Level 4: Business Strategy & Channel Allocation

### The Question
> *"Marketing spend on Affiliate is generating a 3.65x ROAS, while Paid Search generates 7.03x. The Marketing Director argues: 'Affiliate is still profitable above 1.0x, so we should keep spending.' How do you respond?"*

#### Self-Evaluation Rubric:
- [ ] **Correctness**: Pointed out that 1.0x ROAS is break-even only if COGS and operating costs are 0%.
- [ ] **Clarity**: Calculated contribution margin after 42% product margin.
- [ ] **Depth**: Discussed marginal return on ad spend (mROAS) and capital opportunity cost.
- [ ] **Business Thinking**: Recommended shifting budget to higher-yielding channels.
- [ ] **Communication**: Professional, respectful, and data-backed disagreement.

<details>
<summary>🔍 Click to Reveal Benchmark Evaluation & Ideal Answer</summary>

#### Ideal Answer
> "I would respectfully explain why a 3.65x ROAS in our business barely covers baseline costs.
> 
> A common misconception is that any ROAS above 1.0x is profitable. However, our platform has an average gross margin of 42.09% (COGS is ~58%). Therefore, our break-even ROAS is:
> $$\text{Break-Even ROAS} = \frac{1}{\text{Gross Margin}} = \frac{1}{0.4209} \approx 2.38\text{x}$$
> When you factor in our 10% return rate, payment gateway fees (2.5%), and shipping subsidies, the operational hurdle rate rises to ~3.2x. At 3.65x ROAS, Affiliate marketing yields a razor-thin net contribution profit of only $29.6K on $55.3K of ad spend.
> 
> More importantly, capital has an **opportunity cost**. Every dollar spent on Affiliate at 3.65x could be allocated to Paid Search at 7.03x ROAS, which produces nearly double the cash gross profit. I would recommend reallocating $30,000 from Affiliate to Paid Search to maximize total EBITDA."
</details>

---

## Level 5: Statistics & Controlled Experimentation

### The Question
> *"Your A/B test resulted in p = 0.0455 for conversion rate, but ARPU has p = 0.109. Can you claim the experiment was an unqualified success? What risks exist?"*

#### Self-Evaluation Rubric:
- [ ] **Correctness**: Acknowledged that conversion rate is significant, but ARPU is NOT statistically significant at $\alpha = 0.05$.
- [ ] **Clarity**: Explained why ARPU has higher variance than a binary conversion metric.
- [ ] **Depth**: Discussed guardrail metrics and practical significance.
- [ ] **Business Thinking**: Balanced risk of rollout against potential gains.
- [ ] **Communication**: Honest, rigorous statistical articulation.

<details>
<summary>🔍 Click to Reveal Benchmark Evaluation & Ideal Answer</summary>

#### Ideal Answer
> "We must be statistically honest: we can claim statistical significance for the primary metric (Conversion Rate, $p = 0.0455 < 0.05$), but we cannot claim statistical significance for ARPU ($p = 0.109 > 0.05$).
> 
> This divergence occurs frequently in e-commerce: conversion rate is a low-variance binary proportion (0 or 1), whereas ARPU is a continuous metric with heavy right-skew and high variance due to non-converting visitors spending $0. Detecting a statistically significant shift in ARPU typically requires 3x to 5x the sample size.
> 
> However, ARPU served as our **guardrail metric**, not our primary test metric. Our pre-experiment criterion for the guardrail was non-inferiority: ensure that the streamlined checkout does not degrade basket value. Because Treatment ARPU was +$1.04 higher with positive directional momentum, we satisfied the guardrail.
> 
> The business risk is the **Novelty Effect** and potential post-purchase returns from hasty 1-click orders. Therefore, while I recommend rolling out Treatment, I would mandate a 60-day post-launch audit tracking 30-day cohort return rates."
</details>

---

## Level 6: System Architecture & Stress-Testing

### The Question
> *"What happens to your analytics system when daily orders grow from 18,000 to 18,000,000? Where does this architecture break, and how would you redesign it?"*

#### Self-Evaluation Rubric:
- [ ] **Correctness**: Identified that SQLite and in-memory Pandas will crash with OOM errors.
- [ ] **Clarity**: Addressed storage, processing, and visualization bottlenecks separately.
- [ ] **Depth**: Proposed modern distributed tools (Snowflake/BigQuery, dbt, Apache Kafka).
- [ ] **Business Thinking**: Discussed cost and query performance trade-offs.
- [ ] **Communication**: Confident transition from single-node to distributed data engineering.

<details>
<summary>🔍 Click to Reveal Benchmark Evaluation & Ideal Answer</summary>

#### Ideal Answer
> "At 18 million orders, our current architecture would fail in three distinct areas:
> 1. **Ingestion Bottleneck**: The single-node Pandas ETL pipeline would experience Out-Of-Memory (OOM) crashes loading multimillion-row DataFrames into memory.
> 2. **Storage Bottleneck**: SQLite cannot handle concurrent write locks, and standard PostgreSQL would require extensive horizontal read-replicas, partitioning by `order_date`, and clustered indexing to maintain sub-second query latency.
> 3. **Presentation Bottleneck**: Loading millions of rows into a Streamlit server instance would exhaust server RAM.
> 
> **Redesign for 18M Scale**:
> 1. **Streaming & Ingestion**: Stream clickstream events via Apache Kafka into a distributed cloud data warehouse (Snowflake or BigQuery).
> 2. **Transformation Layer**: Migrate all Python KPI and retention logic into **dbt** running incrementally inside the warehouse via clustered columnar tables.
> 3. **Aggregation / Semantic Layer**: Pre-aggregate daily metrics into rollup tables or OLAP data marts (e.g. ClickHouse or Cube.js) so that the Streamlit dashboard queries pre-computed aggregates in milliseconds without scanning 18M raw transaction rows."
</details>
