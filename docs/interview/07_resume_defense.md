# 07. Resume Bullet Defense & Claim Verification

This document provides ready-to-use resume bullet points representing your work on this platform, accompanied by comprehensive technical defenses, calculation proofs, and claims to avoid.

---

## Resume Bullet 1: Data Architecture & Dimensional Modeling

> **"Architected a Kimball Star Schema analytical warehouse in PostgreSQL & SQLite with 8 dimension and fact tables, ingesting 18,000+ orders and 30,000+ clickstream sessions with a 33-test automated data quality gate."**

### 1. What does it actually mean?
You designed an analytical database separating conformed dimensions (`dim_customers`, `dim_products`, `dim_dates`) from business event facts (`fact_orders`, `fact_order_items`, `fact_sessions`, `fact_marketing_spend`, `fact_ab_experiment`). Before loading data, your ETL pipeline validates that keys are unique, dates are sequential, amounts are non-negative, and foreign keys have no orphaned records.

### 2. Underlying Implementation
- `sql/ddl/schema_postgresql.sql` & `sql/ddl/schema_sqlite.sql`
- `src/database.py` (SQLAlchemy connection pooling & dialect detection)
- `src/etl_pipeline.py` (`DataQualityAudit` testing 33 criteria)

### 3. How the metrics were calculated
- 2,500 unique customers, 120 SKUs, 18,000 orders, 30,142 order items, 30,000 sessions, 1,830 daily marketing records, 12,000 experiment subjects.
- 33 automated tests in `reports/data_quality_report.md` (33 PASS, 0 FAIL).

### 4. Potential Interviewer Question
*"Why did you choose a Star Schema over a normalized 3rd Normal Form (3NF) relational model?"*

### 5. Defendable Answer
> "In transactional systems (OLTP), 3NF minimizes write redundancy and prevents write anomalies. But in analytical reporting (OLAP), 3NF creates a complex web of 8+ table joins that crushes query performance and makes business queries error-prone. A Star Schema decouples numeric measurements into facts and context into dimensions, allowing BI tools to execute clean single-level joins with B-tree index scans."

### 6. Claims You Should NOT Make
- ❌ Do NOT claim: *"I deployed this to a multi-node distributed Snowflake cluster with Kafka streams."* (Be honest: you engineered a production-ready PostgreSQL schema with SQLite fallback).

---

## Resume Bullet 2: Advanced SQL & Analytics Engineering

> **"Engineered complex SQL analytical models using CTEs, window functions (LAG, NTILE, rolling frames), and dimensional aggregations to calculate MoM revenue growth, 7-day rolling trends, and customer RFM lifetime segments."**

### 1. What does it actually mean?
You didn't just write basic `SELECT * FROM orders WHERE status = 'Completed'`. You wrote production-grade analytical SQL that handles sequential window frames, quantile discretization, and conditional logic.

### 2. Underlying Implementation
- `sql/analytics/01_business_kpis.sql`
- `sql/analytics/03_customer_rfm.sql`
- `sql/analytics/04_cohort_retention.sql`

### 3. How the metrics were calculated
- MoM Growth: `((monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY order_month)) * 100.0) / LAG(monthly_revenue, 1)`.
- 7-Day Moving Average: `AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`.
- RFM: `NTILE(5) OVER (ORDER BY recency_days DESC)` and `NTILE(5) OVER (ORDER BY monetary_value ASC)`.

### 4. Potential Interviewer Question
*"What is the difference between `ROWS BETWEEN` and `RANGE BETWEEN` in your rolling revenue calculation?"*

### 5. Defendable Answer
> "`ROWS BETWEEN` defines the window frame by a fixed physical count of preceding rows (e.g. 6 rows before current row). `RANGE BETWEEN` defines the frame by logical value offsets (e.g. interval of 6 calendar days). Because our pipeline guarantees an unbroken date dimension with exactly one record per day, `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` accurately captures a 7-day trailing moving average."

### 6. Claims You Should NOT Make
- ❌ Do NOT claim: *"I wrote custom C-extensions for SQL."* (You wrote ANSI SQL compatible with modern relational engines).

---

## Resume Bullet 3: Product Analytics & Funnel Optimization

> **"Identified a 55.7% drop-off in the Add-to-Cart product funnel stage and an 8.29% vs. 15.42% mobile conversion gap across 30,000 sessions, justifying a streamlined checkout redesign."**

### 1. What does it actually mean?
You analyzed digital clickstream tracking data across 5 distinct milestone events and compared conversion across device platforms, discovering that mobile users converted at roughly half the rate of desktop users.

### 2. Underlying Implementation
- `src/product_analytics.py` (`get_funnel_summary` and `get_funnel_by_dimension`)
- `sql/analytics/02_product_funnel.sql`
- `dashboard/app.py` (Interactive Funnel Chart & Drop-off table)

### 3. How the metrics were calculated
- Funnel progression: 30,000 Sessions $\to$ 21,399 Item Views (71.33%) $\to$ 9,479 Add to Carts (31.60%) $\to$ 5,097 Begin Checkouts (16.99%) $\to$ 3,097 Purchases (10.32%).
- Drop-off from View to Cart: $(21,399 - 9,479) / 21,399 = 55.70\%$.
- Mobile Conversion: $1,637 / 19,742 = 8.29\%$.
- Desktop Conversion: $1,259 / 8,162 = 15.42\%$.

### 4. Potential Interviewer Question
*"Why did mobile users drop off so heavily between product view and cart addition?"*

### 5. Defendable Answer
> "On mobile devices, smaller screen viewports pushed key product specifications and the 'Add to Cart' CTA below the fold. Users had to scroll past long descriptions to locate the button. Furthermore, page load latency on mobile networks compounded bounce rates. We recommended a sticky bottom add-to-cart bar and compressed product imagery to resolve this."

### 6. Claims You Should NOT Make
- ❌ Do NOT claim: *"I built a custom mobile iOS app from scratch."* (You analyzed session clickstream tracking data from web and mobile apps).

---

## Resume Bullet 4: Controlled Experimentation & Inferential Statistics

> **"Conducted a two-sample hypothesis test on a 12,000-user checkout A/B experiment, achieving a statistically significant +1.32% absolute lift (p = 0.0455, 95% CI: [+0.03%, +2.63%]), unlocking $128K+ in projected annual revenue."**

### 1. What does it actually mean?
You evaluated a randomized controlled trial using two-sample proportion Z-testing, verified p-values and confidence intervals, validated secondary ARPU guardrail metrics, and produced an executive rollout recommendation.

### 2. Underlying Implementation
- `src/ab_testing.py` (`run_proportion_test`, `run_arpu_test`, `run_subgroup_analysis`)
- `tests/test_ab_testing.py`

### 3. How the metrics were calculated
- Control: $910 / 6,043 = 15.06\%$.
- Treatment: $976 / 5,957 = 16.38\%$.
- Absolute Lift: $+1.32\%$; Relative Lift: $+8.83\%$.
- Pooled Standard Error: $SE = 0.00665$.
- Test Statistic: $Z = 2.0003 \to p = 0.04547 < 0.05$.
- Annual Impact: $+1.32\% \times 30,000 \text{ sessions} = +396 \text{ orders} \times \$322.73 \text{ AOV} = +\$127,801$.

### 4. Potential Interviewer Question
*"What would you have concluded if the p-value was 0.06?"*

### 5. Defendable Answer
> "If $p = 0.06$, under our pre-determined significance threshold of $\alpha = 0.05$, we would fail to reject the null hypothesis. I would not claim statistical significance or 'trending towards significance.' I would check whether the test had reached its planned sample size and statistical power (80%). If fully powered, I would recommend against a full rollout, as the observed lift could readily be explained by random sampling variation."

### 6. Claims You Should NOT Make
- ❌ Do NOT claim: *"The experiment doubled company revenue overnight."* (Keep the lift realistic and defensible: +1.32% absolute lift).

---

## Resume Bullet 5: Commercial Analytics & Marketing Efficiency

> **"Evaluated marketing channel unit economics across $470K+ in ad spend, identifying an underperforming Affiliate channel (3.65x ROAS, $485 CAC) and recommending a $30K capital reallocation to Paid Search (7.03x ROAS)."**

### 1. What does it actually mean?
You blended marketing cost data with first-touch customer acquisitions and completed transaction revenue, evaluating CAC, ROAS, and net contribution profit to optimize capital allocation.

### 2. Underlying Implementation
- `src/marketing_analytics.py` (`get_channel_performance_scorecard`)
- `sql/analytics/05_marketing_efficiency.sql`
- `reports/business_case_studies.md` (Case Study 4)

### 3. How the metrics were calculated
- Paid Search: Spend \$220,795.63, Acquired 536 customers $\to$ CAC = \$411.93, Revenue = \$1,552,084.77 $\to$ ROAS = 7.03x, Contribution Profit = +$430,597.95.
- Affiliate: Spend \$55,328.80, Acquired 114 customers $\to$ CAC = \$485.34, Revenue = \$202,044.20 $\to$ ROAS = 3.65x, Contribution Profit = +$29,680.19.
- Break-even ROAS: $1 / 0.4209 = 2.38\text{x}$.

### 4. Potential Interviewer Question
*"Why look at Contribution Profit instead of just ROAS?"*

### 5. Defendable Answer
> "ROAS only measures top-line revenue generated per ad dollar, completely ignoring product COGS, discounts, and margins. A channel could achieve a 4.0x ROAS selling low-margin 15% electronics and actually lose money on every order. Contribution Profit subtracts COGS and Ad Spend from revenue, showing the true net cash contribution added to company EBITDA."

### 6. Claims You Should NOT Make
- ❌ Do NOT claim: *"I eliminated all marketing waste and achieved 100x ROAS across every channel."* (Paid Search at 7.0x and Affiliate at 3.6x are realistic commercial figures).
