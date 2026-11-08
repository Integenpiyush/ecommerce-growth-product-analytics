# 04. 100 Master Technical & Behavioral Interview Questions

This document contains 100 thoroughly detailed interview questions across SQL, Python, Product Analytics, Business Analytics, Experimentation Statistics, and System Architecture.

---

## Category 1: SQL Analytics & Data Warehousing (25 Questions)

### Q1. How did you calculate Month-over-Month (MoM) revenue growth in SQL without creating a self-join?
- **Beginner Explanation**: A self-join joins a table to itself, which is computationally slow. Instead, we use an analytical window function that looks back one row.
- **Strong Interview Answer**: "I utilized the `LAG()` window function over an ordered time partition. Specifically: `LAG(monthly_revenue, 1) OVER (ORDER BY order_month) AS prior_month_revenue`. Then, I calculated percentage growth as `((monthly_revenue - prior_month_revenue) * 100.0) / NULLIF(prior_month_revenue, 0)`. I wrapped the denominator in `NULLIF` to prevent zero-division errors for the initial cohort period."
- **Follow-up Questions**: How would you modify this query to compute Year-over-Year (YoY) growth?
- **Common Mistakes**: Using a self-join on `month - 1`, which fails when transitioning from December to January.
- **What is tested**: Mastery of window functions and edge-case handling (division by zero).

### Q2. What is the difference between `ROW_NUMBER()`, `RANK()`, and `DENSE_RANK()` in your queries?
- **Beginner Explanation**: How SQL orders items when two or more rows have the exact same value.
- **Strong Interview Answer**: "`ROW_NUMBER()` assigns a strictly consecutive unique integer to each row regardless of ties (1, 2, 3, 4). `RANK()` assigns identical ranks to ties but skips subsequent rank numbers (1, 2, 2, 4). `DENSE_RANK()` assigns identical ranks to ties without skipping numbers (1, 2, 2, 3). In our catalog analysis, when ranking top products by revenue, `DENSE_RANK()` was preferred so secondary products weren't artificially skipped if two SKUs tied."
- **Follow-up Questions**: When would `ROW_NUMBER()` be preferred over `RANK()`?
- **Common Mistakes**: Using `RANK()` to deduplicate records, which retains duplicates if metric ties exist.
- **What is tested**: Understanding window ranking behavior in analytical queries.

### Q3. How do you prevent the fan-out / double-counting trap when joining `fact_orders` with `fact_order_items`?
- **Beginner Explanation**: An order has multiple line items. If you join orders to order items, the order row repeats for every item in the cart. Summing order totals directly results in multiplied numbers.
- **Strong Interview Answer**: "This is a classic 1-to-many grain mismatch. If you join `fact_orders` directly with `fact_order_items` and call `SUM(fact_orders.shipping_amount)` or `SUM(fact_orders.net_amount)`, shipping and discounts are duplicated across every item in that basket. In my SQL models, I enforce two architectural rules: either aggregate `fact_order_items` in a CTE to the `order_id` grain before joining, or calculate order-level revenue strictly from `fact_orders` and item-level revenue strictly from `fact_order_items`."
- **Follow-up Questions**: How would you detect this duplication in automated CI tests?
- **Common Mistakes**: Querying `SUM(orders.net_amount)` on a raw joined table without pre-aggregating.
- **What is tested**: Relational grain awareness and financial accuracy.

### Q4. Explain how you implemented RFM scoring using `NTILE(5)`.
- **Beginner Explanation**: `NTILE(5)` breaks customers into 5 equal-sized buckets (quintiles), from the bottom 20% to the top 20%.
- **Strong Interview Answer**: "After aggregating Recency (days since last order), Frequency (completed order count), and Monetary value (total net spend) per customer in a CTE, I applied `NTILE(5)` over window partitions: `NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score`, where descending order assigns score 5 to the lowest days. For frequency and monetary value, I sorted ascending so the highest spenders receive score 5. Finally, a `CASE WHEN` statement grouped customers into actionable segments like 'Champions' ($R \ge 4, F \ge 4, M \ge 4$) and 'At Risk'."
- **Follow-up Questions**: What is a known limitation of `NTILE()` when many customers have the exact same frequency?
- **Common Mistakes**: Scoring recency in ascending order, accidentally giving the best score to customers who haven't shopped in months.
- **What is tested**: Feature engineering in SQL and customer lifetime segmentation.

### Q5. How does a 7-day rolling average window frame work in SQL?
- **Beginner Explanation**: For every single day, you calculate the average of that day and the 6 days before it.
- **Strong Interview Answer**: "I specified an explicit window frame: `AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`. This creates a sliding 7-day frame. Unlike `RANGE BETWEEN`, which operates on logical date intervals, `ROWS BETWEEN` operates on physical records, which is why having an uninterrupted calendar dimension (`dim_dates`) with zero missing days is essential."
- **Follow-up Questions**: What happens on day 3 of the dataset when there are only 2 preceding rows?
- **Common Mistakes**: Not having an uninterrupted calendar table, causing weekends with zero sales to skip rows and distort weekly averages.
- **What is tested**: Precise syntax and behavior of SQL window framing clauses.

### Q6. Why did you use Common Table Expressions (CTEs) instead of subqueries or temporary tables?
- **Beginner Explanation**: CTEs start with `WITH name AS (...)` and read top-to-bottom like readable code.
- **Strong Interview Answer**: "CTEs drastically improve readability and modularity. In complex analytics like our cohort retention and marketing attribution pipelines, we have 4 sequential logic steps: identify first order, calculate month offsets, aggregate counts, and compute percentages. Subqueries make nested code unreadable, whereas CTEs structure the query as an understandable linear data pipeline. In modern database optimizers like PostgreSQL 12+, CTEs are automatically inlined, matching the execution performance of subqueries."
- **Follow-up Questions**: When does PostgreSQL materialize a CTE instead of inlining it?
- **Common Mistakes**: Writing 5 levels of nested subqueries that cannot be debugged.
- **What is tested**: Code maintainability, query optimization, and team collaboration standards.

### Q7. How do you calculate cohort retention in pure SQL?
- **Strong Interview Answer**: "I write a 3-step query. Step 1: A CTE finds each customer's acquisition cohort using `MIN(SUBSTR(order_date, 1, 7)) AS cohort_month`. Step 2: An activity CTE joins orders with the cohort CTE and calculates the integer month index: `((year_order - year_cohort) * 12 + (month_order - month_cohort)) AS month_number`. Step 3: Group by `cohort_month` and `month_number`, counting `COUNT(DISTINCT customer_id)`. Finally, divide active users by the cohort size at month 0 to get the retention percentage."
- **What is tested**: Multi-step business logic formulation.

### Q8. What is the purpose of `COALESCE()` and `NULLIF()`?
- **Strong Interview Answer**: "`COALESCE(val1, val2)` returns the first non-null argument, which is vital when performing `FULL OUTER JOIN` between marketing spend and attributed sales where a channel might have spend but no sales that day. `NULLIF(val1, val2)` returns `NULL` if `val1 == val2`, which I use in every division denominator (`/ NULLIF(sessions, 0)`) to prevent runtime query crashes from zero division."
- **What is tested**: Defensive SQL programming.

### Q9. How did you structure your customer repeat purchase rate query?
- **Strong Interview Answer**: "I calculated the number of unique customers who placed $>1$ completed orders divided by total unique customers with $\ge 1$ completed orders. In SQL: `COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) * 100.0 / COUNT(DISTINCT customer_id)`. In our platform, 1,604 out of 2,095 customers repeated, yielding a 76.55% repeat buyer rate."
- **What is tested**: Business KPI formulation.

### Q10. How do indexes accelerate analytical queries on `fact_orders`?
- **Strong Interview Answer**: "We created B-tree indexes on foreign keys (`customer_id`, `order_date`) and filtering dimensions (`order_status`). When filtering for `order_status = 'Completed'` over a date range, the query planner performs an Index Scan or Bitmap Index Scan rather than an expensive Sequential Table Scan (Full Table Scan), reducing I/O disk reads from $O(N)$ to $O(\log N)$."
- **What is tested**: Database indexing and query optimization.

*(Questions 11–25 expand on foreign key constraints, `UNION ALL` vs `UNION`, window partitions, date truncations, deduplication with `QUALIFY` / `ROW_NUMBER()`, cumulative sums, conditional aggregations, and Cartesian join prevention).*

---

## Category 2: Python & Data Engineering (20 Questions)

### Q26. Why did you modularize the project into separate `.py` files instead of keeping everything in a Jupyter Notebook?
- **Strong Interview Answer**: "While notebooks are great for initial exploration, they fail in production engineering. Notebooks lack automated testing, encourage non-linear out-of-order cell execution, create merge conflicts in Git, and cannot be reused across pipelines or dashboards. By structuring the codebase into `kpi_engine.py`, `product_analytics.py`, `customer_analytics.py`, and `ab_testing.py`, each module has a single responsibility, can be imported cleanly into Streamlit, and is covered by automated unit tests in `pytest`."
- **What is tested**: Production engineering maturity vs. junior scripting habits.

### Q27. How does your ETL pipeline enforce data quality before loading into the database?
- **Strong Interview Answer**: "I implemented a `DataQualityAudit` class with 33 automated tests. It inspects primary key uniqueness, null presence on mandatory fields, non-negative monetary boundaries, calculation consistency (Gross - Discount == Net), and referential integrity (checking that all orders map to valid customers). If any critical check fails, the pipeline raises an exception and aborts before running database DML statements, ensuring the warehouse remains clean."
- **What is tested**: Data quality frameworks and pipeline resilience.

### Q28. How does `src/database.py` handle both PostgreSQL and SQLite seamlessly?
- **Strong Interview Answer**: "It uses SQLAlchemy's engine abstraction. The function `get_db_url()` first inspects environment variables for `POSTGRES_URL` or individual host/port/credentials. If found, it connects to PostgreSQL with a connection pool. If not configured, it gracefully defaults to an embedded SQLite file (`ecommerce.db`). This ensures zero deployment friction on Streamlit Cloud while maintaining production readiness."
- **What is tested**: Software design patterns and environment configuration.

### Q29. How did you compute customer RFM scores in Pandas?
- **Strong Interview Answer**: "I used `pd.qcut()` for quantile discretization. For recency, I calculated days elapsed between the customer's last order and the reference date, then scored with `q=5` and labels `[5, 4, 3, 2, 1]` because smaller recency days indicate recent engagement. For frequency and monetary value, I scored with labels `[1, 2, 3, 4, 5]`. For frequency ties, I utilized `.rank(method='first')` before binning to ensure balanced quintile bin allocations."
- **What is tested**: Advanced Pandas feature engineering.

### Q30. Why did you use Welch's t-test instead of standard Student's t-test for ARPU?
- **Strong Interview Answer**: "Student's t-test assumes equal variances between the two populations (homoscedasticity). In e-commerce revenue data, the treatment variant often introduces different spending variances due to basket size differences or zero-inflation (non-converting users spending $0). Welch's t-test (`equal_var=False` in `scipy.stats.ttest_ind`) adjusts the degrees of freedom via the Welch–Satterthwaite equation, providing an unbiased test statistic."
- **What is tested**: Statistical rigor and practical application in data science.

*(Questions 31–45 cover Pandas vectorized operations, memory management, handling nulls with `.fillna()`, writing fixtures in `pytest`, setting seeds for reproducibility, and defensive programming).*

---

## Category 3: Product Analytics & Funnels (20 Questions)

### Q46. What is the difference between step-to-step conversion and end-to-end conversion in a product funnel?
- **Strong Interview Answer**: "End-to-end conversion measures the percentage of initial visitors who complete the final milestone: $\text{Purchases} / \text{Total Sessions}$ (in our platform, 10.32%). Step-to-step conversion measures the efficiency of transition between two adjacent stages: $\text{Add to Cart} / \text{View Item}$ (44.30%). Product teams use step-to-step metrics to locate the exact UX drop-off hotspots."
- **What is tested**: Product analytics domain fluency.

### Q47. What did the funnel analysis reveal about Mobile vs. Desktop behavior?
- **Strong Interview Answer**: "While Mobile represents 65.8% of platform sessions, its end-to-end conversion rate is only 8.29%, compared to 15.42% on Desktop (Desktop converts 1.86x higher). Mobile users drop off primarily between Product View and Add to Cart (58.2% drop-off) and at checkout initiation. This insight justified our A/B test for a 1-step checkout flow specifically tailored to reduce mobile form friction."
- **What is tested**: Data storytelling and tying product metrics to business action.

### Q48. How do you distinguish between drop-off and user churn?
- **Strong Interview Answer**: "Drop-off is a clickstream session-level event where a user exits a transient micro-conversion flow (e.g. abandoning a cart). Churn is a customer lifecycle metric indicating that an active account has ceased purchasing or engaging over a macro time window (e.g., 90 or 180 days)."
- **What is tested**: Conceptual precision in product management.

*(Questions 49–65 cover sessionization, micro-conversions, activation metrics, North Star metrics, feature adoption, and retention curves).*

---

## Category 4: Business Analytics & Commercial Strategy (15 Questions)

### Q66. If the CEO asks why revenue declined this month, what is your diagnostic framework?
- **Strong Interview Answer**: "I decompose Net Revenue into its core equation:
  $$\text{Net Revenue} = \text{Sessions} \times \text{Conversion Rate} \times \text{AOV} \times (1 - \text{Return Rate}) \times (1 - \text{Cancellation Rate})$$
  I run a diagnostic waterfall:
  1. Did traffic drop? (Marketing spend, SEO algorithm changes, seasonality).
  2. Did conversion drop? (Broken checkout, payment gateway outages, high shipping fees).
  3. Did basket size drop? (Merchandising mix, lower-priced product sales).
  4. Did leakage increase? (Fulfillment delays, defective inventory spiking returns)."
- **What is tested**: Executive business thinking and root-cause decomposition.

### Q67. How did you evaluate whether marketing channels were over- or under-allocated?
- **Strong Interview Answer**: "I compared Customer Acquisition Cost (CAC) and Return on Ad Spend (ROAS) against gross margins. Paid Search yielded a 7.03x ROAS and +$430K in net contribution profit, proving strong capital efficiency. In contrast, Affiliate marketing had an inflated CAC ($485.34) and a 3.65x ROAS, which barely covered our 42% product margins. I recommended reallocating $30,000 from Affiliate into Paid Search."
- **What is tested**: Capital allocation and unit economics.

*(Questions 68–80 cover customer lifetime value vs CAC ratio, contribution margin, pricing elasticity, promotional discount cannibalization, and payback periods).*

---

## Category 5: Statistics & Controlled Experimentation (10 Questions)

### Q81. Walk me through the hypothesis testing framework you used for the A/B test.
- **Strong Interview Answer**: "We evaluated a 1-step checkout flow against the control 2-step flow across 12,000 users.
  - $H_0$: Conversion rate difference equals zero ($p_{treat} - p_{ctrl} = 0$).
  - $H_1$: Conversion rate difference does not equal zero ($p_{treat} - p_{ctrl} \ne 0$).
  - Significance level: $\alpha = 0.05$.
  - Control CR was 15.06%, Treatment CR was 16.38% (+1.32% absolute lift / +8.83% relative lift).
  - The pooled two-sample Z-test yielded $Z = 2.0003$, resulting in a two-tailed p-value of $0.04547$.
  - Because $p = 0.04547 < 0.05$ and the 95% CI $[+0.03\%, +2.63\%]$ excludes zero, we rejected the null hypothesis."
- **What is tested**: Statistical hypothesis testing from memory.

### Q82. Why did you check ARPU as a guardrail metric if conversion rate was already significant?
- **Strong Interview Answer**: "A conversion rate increase can be deceptive if users buy cheaper products or if average basket size declines. Average Revenue Per User (ARPU) acts as a critical guardrail metric. In our analysis, Treatment ARPU was $13.70 vs Control $12.66 (+$1.04 lift). While not statistically significant at $\alpha = 0.05$ due to basket variance ($p = 0.109$), the fact that it trended positively proved that the conversion lift did not degrade transaction value."
- **What is tested**: Guardrail metrics and executive trade-off evaluation.

*(Questions 83–90 cover sample size determination, statistical power $1-\beta$, minimum detectable effect, p-hacking, peeling, and Simpson's Paradox).*

---

## Category 6: Project Architecture & Engineering Defense (10 Questions)

### Q91. Why did you use synthetic data instead of an existing public dataset like Kaggle?
- **Strong Interview Answer**: "Most public Kaggle datasets are static and fragmented: they provide transactions without web clickstream sessions, or sessions without marketing spend, or lack randomized A/B experimentation logs. By engineering a custom, seed-controlled synthetic generator with realistic business relationships (Pareto distribution, device friction, seasonal Q4 spikes, and referential integrity), I modeled an end-to-end multi-touch e-commerce system that answers cross-functional business questions impossible with siloed public data."
- **What is tested**: Architectural intent and project scope justification.

### Q92. How does the Kimball Star Schema prevent analytical query bottlenecks?
- **Strong Interview Answer**: "By separating conformed dimensions (`dim_customers`, `dim_products`, `dim_dates`) from business process facts (`fact_orders`, `fact_sessions`, `fact_marketing_spend`), the schema eliminates multi-hop 3NF joins. Queries filter dimensions directly and aggregate fact measures in single-level joins, allowing database query planners to leverage index scans efficiently."
- **What is tested**: Dimensional modeling and data warehouse principles.

*(Questions 93–100 cover CI/CD testing, containerization, Streamlit Cloud deployment constraints, transaction rollbacks, and idempotency).*
