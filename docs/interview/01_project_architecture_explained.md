# 01. Project Architecture Explained

## 1. End-to-End System Architecture

The **E-commerce Growth & Product Analytics Platform** is an end-to-end, production-style analytical system designed to model, ingest, validate, analyze, and visualize multi-touch e-commerce retail data.

```
+-----------------------------------------------------------------------------------+
|                              1. DATA GENERATION & SEED                            |
|  - Synthetic generator (Seed: 42)                                                 |
|  - 2,500 Customers | 120 Products | 30,000 Sessions | 18,000 Orders | 12,000 Exp |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        2. DATA QUALITY & INGESTION PIPELINE                       |
|  - Automated Data Quality Gate (33 tests: PK uniqueness, null checks, FK integrity)|
|  - ETL Transformation Engine (Gross -> Net, COGS derivation, Calendar Dimension)  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                      3. RELATIONAL ANALYTICAL WAREHOUSE                           |
|  - Kimball Dimensional Model (Star Schema)                                        |
|  - Production: PostgreSQL (DDL, Indices, Foreign Keys)                            |
|  - Local/Cloud Demo: SQLite Standalone (`data/processed/ecommerce.db`)            |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                      4. PYTHON & SQL ANALYTICS CORE                               |
|  - KPI Engine: Revenue, AOV, Gross Profit, Repeat Purchase Rate, Rolling 30d      |
|  - Product Analytics: 5-Stage Funnel, Stage Conversion, Drop-offs, Device Splits  |
|  - Customer Analytics: RFM Quintiles (NTILE 5), Segment Clusters, Cohort Heatmap  |
|  - Marketing Engine: First-Touch Attribution, Blended & Paid CAC, ROAS            |
|  - Experimentation Engine: Two-Sample Proportion Z-Test, Welch's t-Test, MDE      |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        5. INTERACTIVE PRESENTATION LAYER                          |
|  - Streamlit Dashboard (5 Focused Pages)                                          |
|  - Interactive Plotly Visualizations (Funnels, Heatmaps, CIs, Rolling Trends)     |
|  - Dynamic Global Dimension Filtering (Date, Channel, Device, Category)           |
+-----------------------------------------------------------------------------------+
```

---

## 2. Detailed Data Flow

1. **Extraction (Raw Layer)**:
   - Data is extracted from raw CSV files in `data/raw/`.
   - Each dataset represents a distinct business process: account creation (`customers.csv`), merchandising catalog (`products.csv`), digital clickstream (`sessions.csv`), financial transactions (`orders.csv` and `order_items.csv`), marketing ad networks (`marketing_spend.csv`), and product experiment logs (`ab_experiment.csv`).

2. **Validation Gate (`DataQualityAudit`)**:
   - Before any database ingestion occurs, the pipeline runs 33 programmatic validation checks.
   - If any critical check fails (e.g. negative net price, orphan order without customer, duplicate primary key), the pipeline halts immediately. This prevents database corruption.

3. **Transformation & Cleaning**:
   - Computes derived financial columns: $\text{Gross Profit} = \text{Net Amount} - \text{Total COGS}$ and $\text{Profit Margin} = (\text{Gross Profit} / \text{Net Amount}) \times 100$.
   - Generates the date dimension (`dim_dates`) spanning 453 contiguous calendar days to prevent date-gap bugs in time-series queries.

4. **Database Loading (Warehouse Layer)**:
   - Tables are loaded atomically using SQLAlchemy transactions.
   - Dimension tables (`dim_dates`, `dim_customers`, `dim_products`) are populated first to satisfy referential foreign key constraints, followed by fact tables.

5. **Analytical Query Layer**:
   - Python analytical engines query the warehouse using SQL queries optimized with CTEs, window functions (`LAG`, `SUM OVER`, `NTILE`), and composite indices.

6. **Serving & Dashboard Layer**:
   - Streamlit queries the analytical engine via cached resource sessions. Global sidebar filters slice the dataset dynamically.

---

## 3. Technology Stack Justification & Alternatives Considered

| Technology | Role in Architecture | Why Selected | Alternatives Considered | Trade-Offs / Reason Rejected |
|---|---|---|---|---|
| **Python 3** | Core language | Standard data science & analytics engineering language; rich ecosystem (`pandas`, `scipy`). | R, Julia, Go | R has smaller engineering footprint; Python enables unified backend and frontend. |
| **Pandas / NumPy** | Vectorized computation | In-memory transformations, cohort pivots, array manipulations. | Polars, PySpark | Polars is faster for >10GB data, but Pandas is ubiquitous in industry interviews. PySpark is overkill for <1M rows. |
| **PostgreSQL & SQLite** | Analytical database | PostgreSQL is the industry standard open-source relational DB; SQLite enables zero-friction demo execution on Streamlit Cloud without hosting costs. | Snowflake, BigQuery, DuckDB | Cloud warehouses incur monthly cloud hosting fees; DuckDB is great, but SQL dialect differs slightly from standard Postgres ANSI SQL. |
| **SQLAlchemy** | Database ORM / Core Abstraction | Enables database-agnostic connection pooling, dialect switching, and transaction safety. | Raw `psycopg2`, `sqlite3` | Raw drivers lock code to a single database dialect. SQLAlchemy allows seamless switching between Postgres and SQLite via `.env`. |
| **Streamlit** | Interactive UI | Rapid Python dashboard deployment; state management; native reactive reactivity. | Tableau, PowerBI, Dash, React | BI tools require commercial licenses; Dash requires extensive boilerplate HTML/CSS; React requires a separate Node.js frontend repo. |
| **Plotly** | Visualization | Interactive SVG/WebGL charts, hover tooltips, zoom/pan, native Streamlit embedding. | Matplotlib, Seaborn, Altair | Matplotlib produces static PNG images; Plotly allows executive hover exploration. |
| **SciPy / Statsmodels** | Experimentation stats | Exact p-values, z-scores, t-tests, and confidence interval calculations. | Custom math formulas | Pre-compiled Fortran/C routines guarantee numerical precision and statistical validity. |
| **Pytest** | Automated Testing | Industry standard testing framework with fixtures, parameterized tests, and clean reporting. | Unittest | Pytest requires less boilerplate and produces much more readable diffs upon test failure. |

---

## 4. Architectural Trade-offs & Limitations

1. **In-Memory vs. In-Database Computation**:
   - *Decision*: Simple aggregations (KPI cards, counts) run directly in SQL; complex multi-dimensional pivots (RFM quantiles, cohort retention grids) are processed in Pandas.
   - *Trade-off*: In production at 50M+ rows, loading full tables into Pandas RAM will cause Out-Of-Memory (OOM) errors. At that scale, cohort calculations must run directly inside a distributed warehouse (Snowflake/BigQuery) using `dbt` models.

2. **First-Touch Marketing Attribution**:
   - *Decision*: Marketing spend is attributed based on the customer's initial signup channel.
   - *Trade-off*: Ignores intermediate touchpoints (e.g., user discovers via Paid Social, clicks an Email 2 weeks later, and purchases via Google Search). A production enterprise system would require a multi-touch attribution (MTA) Markov chain or Shapley value model.

3. **Dual-Database Support (SQLite vs PostgreSQL)**:
   - *Decision*: SQLite was chosen for zero-dependency local runs and Streamlit Cloud, while PostgreSQL DDL was designed for enterprise readiness.
   - *Trade-off*: SQLite lacks native window function features like `NTILE()` in older builds and date-interval math (requiring `JULIANDAY` instead of `INTERVAL '30 days'`). The SQL scripts use ANSI-compliant patterns compatible across both engines.
