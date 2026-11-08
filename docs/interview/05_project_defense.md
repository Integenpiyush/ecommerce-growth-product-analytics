# 05. Master Project Defense & Decision Justifications

This document is your tactical playbook for defending every architectural, statistical, and business decision made in this project during senior interviews.

---

## 1. Why this project?
**Interviewer Prompt**: *"Why did you choose to build an e-commerce growth and product analytics platform rather than a simple machine learning or forecasting model?"*

### Strong Defensible Answer
> "Most entry-level portfolio projects build isolated ML models (like churn prediction on Kaggle's Telco dataset) without establishing the foundational analytical infrastructure that businesses actually depend on daily. 
> 
> In real enterprise companies, 80% of executive decisions are driven by descriptive, diagnostic, and experimental analytics: *Why did revenue drop? Where are customers leaking from the checkout funnel? Which marketing channels yield profitable CAC? Did our feature experiment achieve statistically significant lift?*
> 
> I built this platform to demonstrate the full breadth of senior competencies across Data Analytics, Product Analytics, Business Analytics, and Analytics Engineering: from designing a Kimball dimensional data warehouse and writing advanced SQL CTEs/window functions, to conducting rigorous two-sample hypothesis testing and delivering an interactive executive Streamlit dashboard."

---

## 2. Why synthetic data? Why not a public Kaggle dataset?
**Interviewer Prompt**: *"Isn't synthetic data less realistic than real-world data from Kaggle or public repositories?"*

### Strong Defensible Answer
> "Public datasets are notoriously fragmented and siloed. For example, the Olist Brazilian E-commerce dataset has orders and reviews, but completely lacks website clickstream sessions, marketing channel ad spend, and randomized A/B experimentation logs. Conversely, Google Analytics 4 public data has clickstream sessions, but lacks backend order margin, return/refund line items, and channel cost data.
> 
> To answer cross-functional business questions—such as calculating blended CAC against first-order acquisitions, tracking device-level funnel drop-offs, and running hypothesis tests on checkout flows—I needed a cohesive, end-to-end relational ecosystem.
> 
> I built a seed-controlled (Seed: 42), mathematically grounded generator that embeds realistic business phenomena: a Pareto distribution where the top 20% of customers generate ~68% of revenue, seasonal Q4 spikes, device conversion disparities (Desktop converting 1.8x higher than Mobile), and a 10.05% return rate concentrated in Apparel sizing issues. Everything is reproducible, transparent, and documented."

---

## 3. Why PostgreSQL & SQLite dual database design?
**Interviewer Prompt**: *"Why did you provide DDL for both PostgreSQL and SQLite?"*

### Strong Defensible Answer
> "This reflects production thinking and portfolio pragmatism. 
> 
> In enterprise environments, PostgreSQL is the standard open-source analytical and transactional workhorse with robust support for concurrent connections, constraints, and B-tree indexing. That is why I wrote full production DDL with primary/foreign keys, check constraints, and composite indices in `schema_postgresql.sql`.
> 
> However, for sharing a portfolio project with interviewers, hiring managers, and deploying to Streamlit Community Cloud, requiring an active cloud PostgreSQL instance introduces external credential dependencies and connection outages. By using SQLAlchemy's dialect abstraction in `database.py`, the system seamlessly falls back to a self-contained SQLite warehouse (`ecommerce.db`). It gives the best of both worlds: zero-friction local execution with enterprise-ready schema design."

---

## 4. Why SQL for some analytics and Pandas for others?
**Interviewer Prompt**: *"How do you decide whether a calculation belongs in SQL or in Python/Pandas?"*

### Strong Defensible Answer
> "I follow the industry standard principle of **'Filter and Aggregate Close to the Storage Engine'**:
> 1. **SQL for Heavy Aggregations & Joins**: Order summaries, monthly revenue growth via `LAG()`, rolling 7-day moving averages, and funnel stage counts run in SQL. Databases are optimized for relational algebra, index scans, and predicate pushdown. Querying only aggregated rows reduces network data transfer from hundreds of megabytes to a few kilobytes.
> 2. **Pandas for Multi-Dimensional Matrices & Stats**: Cohort retention pivot matrices, quantile discretizations (`pd.qcut` for RFM scoring), and inferential statistical testing (`scipy.stats` for p-values, z-scores, and Welch's t-tests) are best executed in Python. Doing complex matrix transformations or statistical hypothesis tests in pure SQL requires convoluted procedural PL/pgSQL scripts."

---

## 5. How did you validate data and prevent double-counting?
**Interviewer Prompt**: *"How can you be certain your revenue metrics don't suffer from duplication or fan-out?"*

### Strong Defensible Answer
> "We implemented two layers of defense:
> 1. **Automated Data Quality Gate**: Before ingestion, `DataQualityAudit` runs 33 programmatic tests checking primary key uniqueness, foreign key orphans, null constraints, and mathematical consistency ($\text{Gross} - \text{Discount} = \text{Net}$). If any test fails, the pipeline halts.
> 2. **Enforcing Table Grain**: The most common trap in retail analytics is joining `fact_orders` (order-level grain) with `fact_order_items` (line-item grain) and summing `orders.net_amount`, which multiplies order totals by the number of items in the cart. I strictly enforce grain isolation: platform financial KPIs query `fact_orders` directly, while basket and merchandise analyses aggregate `fact_order_items` to the order grain before joining."

---

## 6. How did you conduct the A/B test, and why is it statistically sound?
**Interviewer Prompt**: *"How did you evaluate the checkout experiment, and what was your final recommendation?"*

### Strong Defensible Answer
> "We tested a streamlined 1-step checkout flow against the 2-step control across 12,000 randomized users.
> - **Primary Metric**: Conversion Rate (orders placed / assigned users).
> - **Statistical Test**: Two-sample pooled Z-test for proportions ($\alpha = 0.05$, two-sided).
> - **Results**: Control converted at 15.06% ($N=6,043$); Treatment converted at 16.38% ($N=5,957$). This yielded an absolute lift of +1.32% (+8.83% relative lift).
> - **P-Value & Confidence Interval**: $Z = 2.0003$, yielding $p = 0.04547 < 0.05$. The 95% Confidence Interval for relative lift is $[+0.21\%, +17.48\%]$, which strictly excludes zero.
> - **Guardrail Metric**: We checked ARPU via Welch's t-test ($t = 1.602, p = 0.109$). While not statistically significant at $\alpha = 0.05$ due to basket variance, ARPU increased by +$1.04 per user, proving the checkout redesign did not degrade basket size.
> - **Recommendation**: Full rollout to 100% of traffic, with targeted monitoring for post-purchase return rates over the subsequent 60 days."

---

## 7. What are the limitations and what would you improve in production?
**Interviewer Prompt**: *"If you had another month to build this with an engineering team, what would you change?"*

### Strong Defensible Answer
> "I would elevate three specific areas:
> 1. **dbt (data build tool) Integration**: Migrate our SQL transformation layer to dbt models with automated schema testing, documentation, and lineage graphs.
> 2. **Multi-Touch Marketing Attribution**: Replace first-touch attribution with a data-driven algorithmic model (Markov chains or Shapley values) to credit middle-funnel touchpoints (Paid Social views preceding Search conversions).
> 3. **Real-time Event Streaming**: Ingest clickstream events via Kafka / Apache Flink into a real-time warehouse (ClickHouse or Snowflake) rather than batch daily ETL."
