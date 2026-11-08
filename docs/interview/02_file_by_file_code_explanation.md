# 02. File-by-File Code & SQL Implementation Deep-Dive

This document breaks down every critical Python and SQL file in the platform. It is written to give you 100% confidence when defending the codebase in senior technical interviews.

---

## Part 1: Python Core Architecture

### 1. `src/database.py`

#### What problem does it solve?
In production, data teams connect to hosted PostgreSQL or Snowflake databases. In local interviews or public portfolio hosting (Streamlit Community Cloud), requiring an external database cluster creates connection failures. `database.py` creates a unified database interface that automatically detects whether to connect to a production PostgreSQL instance or fallback seamlessly to an embedded SQLite database (`ecommerce.db`).

#### Key Functions Explained

##### `get_db_url() -> str`
- **Logic**: Inspects `os.getenv("POSTGRES_URL")`. If empty, inspects standard individual PostgreSQL variables (`POSTGRES_USER`, `POSTGRES_HOST`, etc.). If still absent or unconfigured, constructs an absolute path to `data/processed/ecommerce.db` with SQLite prefix `sqlite:///`.
- **Inputs**: None (reads `.env` environment).
- **Outputs**: SQLAlchemy connection URL string (e.g. `sqlite:////Users/.../ecommerce.db`).
- **What breaks if removed**: The application cannot locate the database; all queries fail with connection errors.

##### `get_engine(db_url: Optional[str] = None) -> Engine`
- **Logic**: Calls SQLAlchemy's `create_engine()`. For SQLite, applies `connect_args={"check_same_thread": False}` so multiple Streamlit threads can query the file concurrently. For PostgreSQL, configures connection pooling (`pool_size=10, max_overflow=20, pool_pre_ping=True`) to maintain active connections and prevent dropped sockets.
- **Inputs**: Optional database URL string.
- **Outputs**: `sqlalchemy.engine.Engine` instance.
- **Example**: `eng = get_engine(); conn = eng.connect()`

##### `init_db(engine: Optional[Engine] = None, ddl_path: Optional[str] = None) -> None`
- **Logic**: Reads either `schema_sqlite.sql` or `schema_postgresql.sql`, parses semicolons into distinct SQL statements, and executes them within an atomic transaction (`with engine.begin() as conn:`).
- **What breaks if removed**: Tables are never provisioned in the database.

---

### 2. `src/etl_pipeline.py`

#### What problem does it solve?
Raw incoming data contains dirty inputs, missing fields, or broken referential relationships. Ingesting unvalidated data directly corrupts financial statements. `etl_pipeline.py` acts as an automated quality gate and ETL orchestrator.

#### Key Functions Explained

##### `DataQualityAudit` Class
- **Purpose**: Collects results of validation checks and generates `reports/data_quality_report.md`.
- **Method `record(test_name, table, status, details, severity)`**: Appends a dictionary test record.
- **Method `has_critical_errors()`**: Returns `True` if any test with severity `CRITICAL` had status `FAIL`.

##### `validate_raw_datasets(datasets, audit)`
- **Line-by-line Logic**:
  1. Primary Key Duplicates: `df[pk].duplicated().sum()`. If $> 0$, records critical failure.
  2. Null Checks: Evaluates critical fields (`order_id`, `net_amount`, `customer_id`).
  3. Foreign Key Integrity: Uses `(~orders['customer_id'].isin(valid_custs)).sum()`. Finds orders that reference non-existent customers.
  4. Math Consistency: `np.abs((orders['gross_amount'] - orders['discount_amount']) - orders['net_amount']) > 0.02`. Asserts that Gross minus Discount strictly equals Net.
  5. Chronological Validity: Merges orders with customer signup dates and checks `order_date < signup_date`.
- **What breaks if removed**: Corrupted, orphaned, or mathematically invalid records enter the database, skewing revenue and AOV calculations.

##### `clean_and_transform(datasets) -> Dict[str, pd.DataFrame]`
- **Logic**:
  - Converts boolean columns to binary integers (`0` / `1`).
  - Generates contiguous `dim_dates` calendar table.
  - Derives order-level metrics:
    ```python
    ord_df["gross_profit"] = (ord_df["net_amount"] - ord_df["total_cogs"]).round(2)
    ord_df["profit_margin_pct"] = np.where(
        ord_df["net_amount"] > 0,
        ((ord_df["gross_profit"] / ord_df["net_amount"]) * 100).round(2),
        0.00
    )
    ```
- **Inputs**: Raw dataframes dictionary.
- **Outputs**: Transformed analytical tables ready for relational insertion.

##### `run_pipeline(data_dir, engine)`
- **Logic**: Orchestrates Extraction $\to$ Validation $\to$ Gate Check $\to$ Transformation $\to$ Database Load $\to$ Report Generation.

---

### 3. `src/kpi_engine.py`

#### What problem does it solve?
Provides centralized, consistent business logic for financial KPIs. Prevents different stakeholders from calculating revenue or AOV using conflicting definitions.

#### Key Functions Explained

##### `load_filtered_orders(...) -> pd.DataFrame`
- **Logic**: Builds a dynamic parameterized SQL query joining `fact_orders`, `dim_customers`, and `dim_products`. Dynamically appends `AND` clauses based on date range, selected channels, devices, or categories.
- **Why parameterized?**: Prevents SQL injection and allows database query engine caching.

##### `compute_summary_kpis(orders_df: pd.DataFrame) -> Dict[str, Any]`
- **Logic**:
  - Filters strictly for `order_status == 'Completed'` when calculating `net_revenue`, `gross_profit`, and `aov`.
  - Calculates repeat purchase rate: counts customers with $>1$ completed order divided by active ordering customers.
  - Computes operational leakage: cancellation rate and return rate against total placed orders.
- **What breaks if removed**: Dashboard executive metric cards display empty or inaccurate totals.

##### `compute_monthly_trend(orders_df: pd.DataFrame) -> pd.DataFrame`
- **Logic**: Groups completed orders by month (`pd.to_datetime().dt.to_period('M')`). Computes `mom_growth_pct` using Pandas `.shift(1)`:
  $$\text{MoM Growth} = \frac{\text{Revenue}_t - \text{Revenue}_{t-1}}{\text{Revenue}_{t-1}} \times 100$$

##### `compute_daily_rolling(orders_df: pd.DataFrame) -> pd.DataFrame`
- **Logic**: Aggregates daily net revenue and applies rolling window smoothing:
  ```python
  daily["rolling_7d_revenue"] = daily["revenue"].rolling(window=7, min_periods=1).mean().round(2)
  daily["rolling_30d_revenue"] = daily["revenue"].rolling(window=30, min_periods=1).mean().round(2)
  ```
- **Business Purpose**: Removes day-of-week seasonality (weekend dips) to show true underlying momentum.

---

### 4. `src/product_analytics.py`

#### What problem does it solve?
Translates 30,000 raw clickstream session logs into an actionable multi-step conversion funnel.

#### Key Functions Explained

##### `get_funnel_summary(...) -> pd.DataFrame`
- **Logic**:
  - Sums milestone flags: `has_view_item`, `has_add_to_cart`, `has_begin_checkout`, `has_purchase`.
  - Computes two distinct conversion percentages for each step:
    1. **Overall Conversion (%)**: Users at step / Total initial sessions.
    2. **Step-to-Step Conversion (%)**: Users at step / Users at immediate prior step.
  - Computes **Drop-off (%)**: $(Users_{prior} - Users_{current}) / Users_{prior} \times 100\%$.
- **What breaks if removed**: Stakeholders cannot pinpoint where customers abandon the website.

##### `get_funnel_by_dimension(dimension: str) -> pd.DataFrame`
- **Logic**: Executes SQL aggregation grouping by `device` or `traffic_channel` to compute conversion rates across cohorts.

---

### 5. `src/customer_analytics.py`

#### What problem does it solve?
Solves customer segmentation and cohort retention tracking. Answers who the best customers are and how long they stay active.

#### Key Functions Explained

##### `compute_rfm_segments(reference_date: str) -> Tuple[pd.DataFrame, pd.DataFrame]`
- **Logic**:
  1. Computes **Recency**: Days elapsed between customer's most recent order date and observation cutoff (`2024-12-31`).
  2. Computes **Frequency**: Distinct count of completed orders.
  3. Computes **Monetary**: Total net spend across completed orders.
  4. Scoring via Quintiles (1 to 5):
     - Uses `pd.qcut()`. For Recency, lower days get higher score (`labels=[5,4,3,2,1]`). For Frequency and Monetary, higher is better (`labels=[1,2,3,4,5]`).
  5. Segment Assignment: Applies business rule mapping scores into 8 actionable groups (Champions, Loyal Customers, At Risk, Hibernating, etc.).
- **What breaks if removed**: Marketing cannot run targeted lifecycle campaigns.

##### `compute_cohort_retention_matrix() -> Tuple[pd.DataFrame, pd.DataFrame]`
- **Logic**:
  1. Identifies first purchase month for each customer: `cohort_month = df.groupby('customer_id')['order_month'].min()`.
  2. Merges back to orders and calculates month distance:
     $$\text{Month Index} = (\text{Year}_{order} - \text{Year}_{cohort}) \times 12 + (\text{Month}_{order} - \text{Month}_{cohort})$$
  3. Pivots data into a matrix of cohorts (rows) vs. month index (columns).
  4. Divides each column by Month 0 base size to yield percentage retention.
- **Outputs**: Pivot table formatted for heatmap rendering.

---

### 6. `src/ab_testing.py`

#### What problem does it solve?
Evaluates whether differences between experiment variants are caused by actual feature improvements or random sampling noise.

#### Key Functions Explained

##### `run_proportion_test(...) -> Dict[str, Any]`
- **Mathematical Formula**:
  - Sample proportions: $\hat{p}_1 = \frac{x_1}{n_1}$, $\hat{p}_2 = \frac{x_2}{n_2}$
  - Absolute Lift: $\Delta = \hat{p}_2 - \hat{p}_1$
  - Pooled Proportion: $\hat{p}_{pool} = \frac{x_1 + x_2}{n_1 + n_2}$
  - Pooled Standard Error: $SE = \sqrt{\hat{p}_{pool}(1 - \hat{p}_{pool})\left(\frac{1}{n_1} + \frac{1}{n_2}\right)}$
  - Z-Statistic: $Z = \frac{\Delta}{SE}$
  - p-value: $2 \times (1 - \Phi(|Z|))$ using `scipy.stats.norm.cdf`
  - 95% Confidence Interval: $\Delta \pm 1.96 \times \sqrt{\frac{\hat{p}_1(1-\hat{p}_1)}{n_1} + \frac{\hat{p}_2(1-\hat{p}_2)}{n_2}}$
- **Why two-sided?**: Guardrails against negative consequences. Even if we hope Treatment is better, we must detect if Treatment hurts conversion.

##### `run_arpu_test(...) -> Dict[str, Any]`
- **Logic**: Executes Welch's two-sample t-test (`scipy.stats.ttest_ind(..., equal_var=False)`) on revenue per visitor.
- **Why Welch's t-test?**: Unlike Student's t-test, Welch's t-test does not assume equal variances between Control and Treatment, making it robust for skewed e-commerce spending distributions.

---

## Part 2: SQL Analytics Scripts Explained

### 1. `sql/analytics/01_business_kpis.sql`
- **Query 1.1 (Platform Summary)**: Uses CTEs `order_base` and `customer_base` joined via `CROSS JOIN`. Aggregates completed revenue vs. cancelled/returned amounts using conditional `CASE WHEN order_status = 'Completed' THEN net_amount ELSE 0 END`.
- **Query 1.2 (Monthly Growth)**: Uses window function `LAG(monthly_revenue, 1) OVER (ORDER BY order_month)` to pull the previous month's revenue onto the current month's row without self-joins.
- **Query 1.3 (Rolling Averages)**: Uses `AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` to generate a true trailing 7-day moving average.

### 2. `sql/analytics/02_product_funnel.sql`
- **Query 2.1 (Funnel Stages)**: Uses a CTE to aggregate milestone counts, followed by `UNION ALL` across stages to construct a normalized stage-by-stage dataset suitable for BI funnel visualizers.
- **Query 2.2 (Device Funnel)**: Computes step conversion ratios using `NULLIF()` in denominators to prevent division-by-zero errors.

### 3. `sql/analytics/03_customer_rfm.sql`
- **Query 3.1 (RFM Quintiles)**:
  - Recency is calculated via `CAST((JULIANDAY('2024-12-31') - JULIANDAY(MAX(order_date))) AS INT)`.
  - Assigns quintiles using `NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score`.
  - Classifies customer tiers using nested `CASE WHEN` logic.

### 4. `sql/analytics/04_cohort_retention.sql`
- **Query 4.1 (Cohort Matrix)**:
  - First identifies customer acquisition cohort: `MIN(SUBSTR(order_date, 1, 7)) AS cohort_month`.
  - Computes relative month index using date subtraction arithmetic.
  - Joins back to cohort base sizes to calculate active user retention percentages.
- **Query 4.2 (Cumulative LTV)**: Uses unbounded window summation `SUM(incremental_revenue) OVER (PARTITION BY cohort_month ORDER BY month_number ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` to compute lifetime value progression.

### 5. `sql/analytics/05_marketing_efficiency.sql`
- **Query 5.1 (Channel Scorecard)**: Full outer join between `channel_spend` and `channel_revenue`. Calculates Customer Acquisition Cost (CAC) and Return on Ad Spend (ROAS).
- **Query 5.2 (Blended vs. Paid CAC)**: Compares total blended marketing spend against all acquired customers versus paid spend against paid-channel acquisitions.
