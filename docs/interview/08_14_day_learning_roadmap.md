# 08. 14-Day Master Interview Preparation Roadmap

This structured 14-day roadmap is designed to take you from beginner to an articulate, confident senior analyst ready to defend every layer of this platform.

```
+--------------------------------------------------------------------------------+
| WEEK 1: Foundations, SQL Mastery, Product Clickstreams & Dimensional Modeling  |
| Day 1: Project Architecture & Star Schema Design                              |
| Day 2: ETL Pipelines & Automated Data Quality Engineering                      |
| Day 3: Advanced SQL: Window Functions (LAG, NTILE, Moving Averages)           |
| Day 4: Core Financial KPIs: Revenue Decomposition & Operational Leakage        |
| Day 5: Product Funnel Analytics: Drop-offs & Device Heterogeneity              |
| Day 6: Customer Segmentation: RFM Quintiles & Cluster Economics                |
| Day 7: Customer Retention: Monthly Cohort Matrices & Cumulative LTV            |
+--------------------------------------------------------------------------------+
                                        |
+--------------------------------------------------------------------------------+
| WEEK 2: Marketing Unit Economics, Rigorous Experimentation & Mock Grilling     |
| Day 8: Marketing Economics: CAC, ROAS & Capital Reallocation                   |
| Day 9: Merchandising & Category Profitability Dynamics                         |
| Day 10: Experimentation Statistics: Two-Sample Z-Tests & Hypothesis Framing    |
| Day 11: Statistical Guardrails: Welch's t-Test, MDE & Confidence Intervals     |
| Day 12: Interactive Dashboard Design & Streamlit Implementation                |
| Day 13: 100-Question Grilling & Level 1-4 Mock Simulation                      |
| Day 14: Final System Defense (Level 5-6) & Resume Polishing                    |
+--------------------------------------------------------------------------------+
```

---

## Week 1: Foundations, SQL Mastery & Customer Dynamics

### Day 1: System Architecture & Dimensional Modeling
- **Topics**: Kimball Star Schema, Fact vs. Dimension tables, Grain definition, OLTP vs. OLAP trade-offs.
- **Files to Study**: `docs/interview/01_project_architecture_explained.md`, `docs/database_schema.md`, `sql/ddl/schema_postgresql.sql`.
- **SQL Practice**: Query `dim_customers` and `fact_orders` to check grains and foreign keys.
- **Business Question**: Why is keeping table grains strictly defined essential for accurate financial reporting?
- **Interview Question**: How does a Star Schema improve query performance compared to 3NF?
- **Practical Exercise**: Draw the entity relationship diagram (ERD) from memory on paper.
- **Revision Task**: Summarize why the dual-database setup (Postgres + SQLite) was chosen.

---

### Day 2: ETL Pipeline & Data Quality Engineering
- **Topics**: Automated quality gates, primary key uniqueness, foreign key orphans, data cleansing.
- **Files to Study**: `src/etl_pipeline.py`, `reports/data_quality_report.md`, `tests/test_data_validation.py`.
- **SQL Practice**: Write a SQL query that detects orphan orders without matching customers using `LEFT JOIN ... WHERE customer_id IS NULL`.
- **Business Question**: What is the commercial risk of ingesting corrupted data into executive dashboards?
- **Interview Question**: How did your pipeline prevent invalid revenue calculations?
- **Practical Exercise**: Intentionally inject a duplicate customer ID into `customers.csv` and verify the pipeline catches it.
- **Revision Task**: Recite the 5 core checks in your data validation audit.

---

### Day 3: Advanced SQL Mastery (Window Functions & CTEs)
- **Topics**: `LAG()`, `LEAD()`, `NTILE()`, `ROW_NUMBER()`, `ROWS BETWEEN` frames.
- **Files to Study**: `sql/analytics/01_business_kpis.sql`, `docs/interview/02_file_by_file_code_explanation.md`.
- **SQL Practice**: Write a query calculating 7-day rolling revenue using `AVG() OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`.
- **Business Question**: Why are rolling averages better than raw daily revenue for executive trend reviews?
- **Interview Question**: What is the difference between `ROW_NUMBER()`, `RANK()`, and `DENSE_RANK()`?
- **Practical Exercise**: Run `01_business_kpis.sql` in SQLite and inspect the output.
- **Revision Task**: Explain why `NULLIF()` must wrap division denominators in analytical queries.

---

### Day 4: Core Financial KPIs & Revenue Decomposition
- **Topics**: Gross Revenue, Discounts, Net Revenue, COGS, Gross Profit Margin, Operational Leakage (Cancellations, Returns).
- **Files to Study**: `src/kpi_engine.py`, `reports/business_case_studies.md` (Case Study 1).
- **SQL Practice**: Write a query breaking down total placed orders into Completed, Cancelled, and Returned counts and percentages.
- **Business Question**: If revenue dropped 6% this month, how do you determine if it was caused by traffic, conversion, or returns?
- **Interview Question**: What was the operational return rate on your platform, and why was it so high?
- **Practical Exercise**: Recompute total net revenue and profit margin using `kpi_engine.py`.
- **Revision Task**: Memorize platform numbers: $4.83M Net Revenue, $2.03M Gross Profit, 42.09% Margin, $322.73 AOV.

---

### Day 5: Product Funnel Analytics & Device Heterogeneity
- **Topics**: Macro vs. micro conversion rates, step-to-step drop-offs, device UX friction (Desktop vs. Mobile).
- **Files to Study**: `src/product_analytics.py`, `sql/analytics/02_product_funnel.sql`, `reports/business_case_studies.md` (Case Study 2).
- **SQL Practice**: Write a query computing conversion rates from View $\to$ Cart, Cart $\to$ Checkout, and Checkout $\to$ Purchase.
- **Business Question**: Why does Mobile convert at 8.29% while Desktop converts at 15.42%?
- **Interview Question**: Where is the primary drop-off point in the e-commerce funnel?
- **Practical Exercise**: Modify `get_funnel_summary()` to return lost user counts per stage.
- **Revision Task**: Explain the difference between session drop-off and cross-device browsing.

---

### Day 6: Customer Segmentation & RFM Quintiles
- **Topics**: Recency, Frequency, Monetary value, `pd.qcut` vs. `NTILE(5)`, behavioral segment clustering.
- **Files to Study**: `src/customer_analytics.py`, `sql/analytics/03_customer_rfm.sql`.
- **SQL Practice**: Write a query finding all customers in the "Champions" segment.
- **Business Question**: Why do "Champions" account for 67.75% of revenue despite being only ~19% of customers?
- **Interview Question**: How did you handle tied customer order frequencies when assigning quintile scores?
- **Practical Exercise**: Run `CustomerAnalyticsEngine().compute_rfm_segments()` in Python.
- **Revision Task**: Name the 8 customer lifecycle segments and their business definitions.

---

### Day 7: Customer Retention, Cohort Heatmaps & LTV
- **Topics**: Acquisition cohorts, month index offsets, cohort retention matrices, cumulative lifetime value curves.
- **Files to Study**: `src/customer_analytics.py`, `sql/analytics/04_cohort_retention.sql`, `reports/business_case_studies.md` (Case Study 3).
- **SQL Practice**: Write the 3-step CTE query that constructs a monthly cohort retention table.
- **Business Question**: What does a Month 1 retention rate of 48% tell you about product-market fit?
- **Interview Question**: How does cumulative LTV progression inform how much you can afford to spend on CAC?
- **Practical Exercise**: Generate the cohort retention heatmap in Python using Plotly.
- **Revision Task**: Explain the difference between user churn and transactional repeat decay.

---

## Week 2: Marketing Unit Economics, Experimentation & Final Defense

### Day 8: Marketing Economics (CAC, ROAS & Budget Allocation)
- **Topics**: First-touch attribution, Paid CAC vs. Blended CAC, ROAS, Net Contribution Profit.
- **Files to Study**: `src/marketing_analytics.py`, `sql/analytics/05_marketing_efficiency.sql`, `reports/business_case_studies.md` (Case Study 4).
- **SQL Practice**: Calculate ROAS and CAC for each marketing channel.
- **Business Question**: Why is a 3.65x ROAS on Affiliate underperforming if it's technically above 1.0x?
- **Interview Question**: What is your break-even ROAS formula based on platform product margins?
- **Practical Exercise**: Calculate the dollar profit gain of shifting $30K from Affiliate to Paid Search.
- **Revision Task**: Memorize channel metrics: Paid Search CAC \$411.93 / ROAS 7.03x; Affiliate CAC \$485.34 / ROAS 3.65x.

---

### Day 9: Merchandising & Category Margin Dynamics
- **Topics**: Category mix, basket affinity, cross-selling high-margin accessories, freight subsidies.
- **Files to Study**: `src/kpi_engine.py` (`compute_category_breakdown`), `reports/business_case_studies.md` (Case Study 5).
- **SQL Practice**: Group order items by category and compute units sold, total revenue, and gross margin percentage.
- **Business Question**: Why does Electronics generate the most revenue ($1.56M) but Home & Living generates more absolute gross profit ($517K)?
- **Interview Question**: How would you optimize product merchandising to boost overall platform margin without raising prices?
- **Practical Exercise**: Identify the top 5 individual SKUs by total profit.
- **Revision Task**: Explain how free shipping thresholds ($75 vs. $99) protect category margins.

---

### Day 10: Controlled Experimentation & Proportion Z-Testing
- **Topics**: Null vs. Alternative hypothesis, randomized assignment, two-sample pooled Z-test, p-value derivation.
- **Files to Study**: `src/ab_testing.py`, `tests/test_ab_testing.py`, `reports/business_case_studies.md` (Case Study 6).
- **SQL Practice**: Query `fact_ab_experiment` to find conversion rates for Control vs. Treatment.
- **Business Question**: Did the 1-step checkout flow win the experiment, and what was the p-value?
- **Interview Question**: Walk me through the pooled standard error formula in a two-sample Z-test.
- **Practical Exercise**: Run `ExperimentAnalyzer().run_proportion_test()` and inspect the confidence interval.
- **Revision Task**: Explain why a two-sided test is preferred over a one-sided test in product experimentation.

---

### Day 11: Statistical Guardrails & Practical Significance
- **Topics**: Welch's two-sample t-test, ARPU variance, Minimum Detectable Effect (MDE), statistical power ($1-\beta$).
- **Files to Study**: `src/ab_testing.py` (`run_arpu_test` and `run_subgroup_analysis`).
- **SQL Practice**: Check revenue per visitor across control and treatment variants.
- **Business Question**: Why was conversion rate significant ($p = 0.0455$) but ARPU was not ($p = 0.109$)?
- **Interview Question**: What is the difference between statistical significance and practical (business) significance?
- **Practical Exercise**: Run the subgroup analysis to verify the mobile-specific lift (+18.4%).
- **Revision Task**: Formulate your final executive rollout recommendation and risk caveats.

---

### Day 12: Streamlit Interactive Dashboard Engineering
- **Topics**: Multi-page dashboard layout, session state, Plotly charting, caching with `@st.cache_resource`.
- **Files to Study**: `dashboard/app.py`, `.streamlit/config.toml`.
- **Command Practice**: Launch the dashboard locally: `streamlit run dashboard/app.py`.
- **Business Question**: How does interactive filtering empower non-technical business stakeholders?
- **Interview Question**: Why did you build the dashboard in Streamlit instead of Tableau or PowerBI?
- **Practical Exercise**: Test filtering by "Mobile" only and inspect how KPI cards update reactively.
- **Revision Task**: Review Streamlit Community Cloud deployment steps and requirements.

---

### Day 13: Technical Interview Grilling (Levels 1–4)
- **Topics**: Rapid-fire technical grilling across SQL, Python, Product, and Business analytics.
- **Files to Study**: `docs/interview/04_project_interview_questions_100.md`, `docs/interview/06_mock_interview_system.md`.
- **Practical Exercise**: Have a friend or timer ask you 15 random questions from the 100-question guide. Speak answers out loud.
- **Scoring**: Evaluate each response against the 5-point rubric (Correctness, Clarity, Depth, Business Thinking, Communication).
- **Revision Task**: Re-read the improved answers for any question where you scored below 4.

---

### Day 14: Final Defense, Resume Alignment & Mock Interview (Levels 5–6)
- **Topics**: Defending limitations, architectural scalability (18K $\to$ 18M orders), resume bullet defense.
- **Files to Study**: `docs/interview/05_project_defense.md`, `docs/interview/07_resume_defense.md`.
- **Practical Exercise**: Deliver the complete 90-second elevator pitch and defend the 5 resume bullets without looking at notes.
- **Final Verification**: Run `pytest tests/ -v` to confirm all 15 tests pass.
- **Outcome**: You are 100% prepared to interview as a Senior Data Analyst, Product Analyst, or Analytics Engineer!
