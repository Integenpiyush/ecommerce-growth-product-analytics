# E-commerce Growth & Product Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791.svg)](https://www.postgresql.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Demo%20Mode-003B57.svg)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg)](https://streamlit.io/)
[![Pytest](https://img.shields.io/badge/Pytest-15%2F15%20Passing-green.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end, production-style e-commerce growth and product analytics platform built from scratch. Demonstrates senior competencies across **Data Analyst**, **Product Analyst**, **Business Analyst**, and **Analytics Engineer** roles.

The platform models, ingests, validates, and analyzes multi-touch retail data to answer the core questions that drive executive decision-making:
- **Why is revenue increasing or decreasing?** (Revenue decomposition & operational leakage)
- **Where are users dropping off in the product funnel?** (Multi-stage clickstream analysis by device & channel)
- **Which customers generate the highest value?** (RFM segmentation & monthly cohort retention)
- **Which acquisition channels perform best?** (CAC, ROAS, and contribution profit economics)
- **Is an A/B experiment statistically significant?** (Two-sample proportion Z-tests, Welch's t-test, & confidence intervals)
- **What commercial actions should stakeholders take?** (6 empirical business case studies)

---

## 🏛️ Architecture Overview

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

## 📊 Verified Core Business Metrics (Ground Truth)

All metrics below are computed directly from the platform's data engine (Seed: 42):

| Metric Category | Verified Platform Value | Business Interpretation |
|---|---|---|
| **Completed Orders** | **14,978** (of 18,000 placed) | 83.21% completion rate across 2024 |
| **Gross Merchandise Value** | **$5,069,551.90** | Total undiscounted transaction volume |
| **Promotional Discounts** | **$235,760.27** | 4.65% platform-wide discount rate |
| **Net Revenue** | **$4,833,791.63** | Invoiced sales realized after discounts |
| **Gross Profit** | **$2,034,574.71** | Realized profit after $2.80M in product COGS |
| **Gross Profit Margin** | **42.09%** | Blended catalog gross margin percentage |
| **Average Order Value (AOV)**| **$322.73** | Net basket size per completed order |
| **Active Ordering Customers**| **2,095 unique buyers** | Out of 2,500 registered user accounts |
| **Repeat Purchase Rate** | **76.55%** | 1,604 buyers placed 2 or more orders |
| **Order Cancellation Rate** | **6.74%** (1,213 orders) | Operational leakage prior to dispatch |
| **Product Return Rate** | **10.05%** (1,809 orders) | Post-delivery returns ($610K refunded) |
| **Total Refund Cash Drag** | **$999,800.95** | Combined refund loss from cancels + returns |
| **End-to-End Funnel CR** | **10.32%** | 3,097 completed purchases / 30,000 sessions |
| **A/B Test Relative Lift** | **+8.83%** (+1.32% abs) | Control: 15.06% vs. Treatment: 16.38% |
| **A/B Test Statistical Sig** | **p = 0.04547 (Z = 2.0003)** | Statistically significant at $\alpha = 0.05$ |

---

## 📁 Repository Structure

```
ecommerce-growth-product-analytics/
├── data/
│   ├── raw/                          # Extracted raw CSVs (customers, orders, sessions, etc.)
│   └── processed/                    # SQLite demo warehouse (ecommerce.db)
├── sql/
│   ├── ddl/
│   │   ├── schema_postgresql.sql     # Enterprise PostgreSQL production DDL & indices
│   │   └── schema_sqlite.sql         # SQLite DDL for local & Streamlit Cloud demo mode
│   └── analytics/
│       ├── 01_business_kpis.sql      # Executive revenue, AOV, MoM growth, rolling averages
│       ├── 02_product_funnel.sql     # 5-stage funnel, stage conversion, device splits
│       ├── 03_customer_rfm.sql       # RFM quintile scoring (NTILE 5) & segment tiers
│       ├── 04_cohort_retention.sql   # Monthly acquisition cohort retention & LTV progression
│       └── 05_marketing_efficiency.sql# Channel spend, CAC, ROAS, & contribution profit
├── src/
│   ├── __init__.py
│   ├── data_generator.py             # Reproducible synthetic retail data generator (Seed: 42)
│   ├── etl_pipeline.py               # Data quality audit gate, transformations, & loader
│   ├── database.py                   # SQLAlchemy engine & dialect connection manager
│   ├── kpi_engine.py                 # Core financial & operational KPI engine
│   ├── product_analytics.py          # Clickstream funnel & merchandise analytics
│   ├── customer_analytics.py         # RFM segmentation & cohort retention matrix engine
│   ├── marketing_analytics.py        # Attribution, CAC, ROAS & marketing efficiency
│   ├── ab_testing.py                 # Two-sample Z-test, Welch's t-test, & CI engine
│   └── utils.py                      # Currency, percentage, & division helper utilities
├── dashboard/
│   └── app.py                        # Interactive 5-page Streamlit dashboard with Plotly
├── reports/
│   ├── data_quality_report.md        # 33-test automated quality gate audit report
│   └── business_case_studies.md      # 6 in-depth empirical business case studies
├── tests/
│   ├── __init__.py
│   ├── test_kpis.py                  # Pytest unit tests for revenue, AOV, margins, growth
│   ├── test_funnel.py                # Tests for monotonic funnels & step-to-step drop-offs
│   ├── test_rfm.py                   # Tests for RFM score distribution & cohort matrices
│   ├── test_ab_testing.py            # Tests for proportion Z-test, Welch's t-test, & bounds
│   └── test_data_validation.py       # Tests for table row counts & referential integrity
├── docs/
│   ├── architecture.md               # Architecture documentation & design trade-offs
│   ├── database_schema.md            # Kimball Star Schema documentation & grain specs
│   ├── data_dictionary.md            # Complete entity & column catalog
│   └── interview/                    # 🎓 Complete Interview Preparation System
│       ├── 01_project_architecture_explained.md
│       ├── 02_file_by_file_code_explanation.md
│       ├── 03_analytics_fundamentals.md
│       ├── 04_project_interview_questions_100.md  # 100 Technical & Behavioral Q&As
│       ├── 05_project_defense.md                  # Comprehensive defense playbook
│       ├── 06_mock_interview_system.md            # 6-Level Progressive Mock Interview
│       ├── 07_resume_defense.md                   # Resume bullets & metric proofs
│       └── 08_14_day_learning_roadmap.md          # 14-day interview study curriculum
├── notebooks/
│   └── exploratory_data_analysis.ipynb # Interactive EDA walkthrough notebook
├── .streamlit/
│   └── config.toml                   # Headless server & telemetry settings
├── requirements.txt                  # Python dependencies
├── .gitignore
├── .env.example
└── LICENSE                           # MIT License
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.9+ (Python 3.9, 3.10, 3.11, or 3.12)
- Git

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-username/ecommerce-growth-product-analytics.git
cd ecommerce-growth-product-analytics

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Generate Synthetic Data & Run ETL Pipeline
The repository comes pre-loaded with reproducible data generation scripts. You can regenerate the entire warehouse with one command:

```bash
# Step 1: Generate 18,000 orders, 30,000 sessions, 12,000 experiment subjects
python3 src/data_generator.py

# Step 2: Execute automated Data Quality Gate (33 tests) and ingest into analytical warehouse
python3 src/etl_pipeline.py
```

### 4. Run Automated Test Suite (Pytest)
Verify calculations and schema integrity:
```bash
pytest tests/ -v
```
*Output: 15 passed in ~2.3 seconds.*

### 5. Launch Interactive Analytics Dashboard
```bash
streamlit run dashboard/app.py
```
Open your browser to `http://localhost:8501`.

---

## 🌐 Cloud Deployment (Streamlit Community Cloud)

This platform is configured for **zero-friction 1-click deployment** on Streamlit Community Cloud:

1. **Push this repository to your GitHub account**.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/).
3. Click **"New app"**, select your repository and branch (`main`).
4. Set the **Main file path** to `dashboard/app.py`.
5. *(Optional)* If connecting to a hosted PostgreSQL database (Supabase, Neon, AWS RDS), add your connection URL to **App Settings > Secrets**:
   ```toml
   POSTGRES_URL = "postgresql://user:password@ep-host.region.aws.neon.tech/ecommerce_analytics"
   ```
   *If `POSTGRES_URL` is omitted, the app automatically runs in standalone local mode using the pre-built `data/processed/ecommerce.db` SQLite database with 100% functionality.*

---

## 🧪 Statistical Experimentation Summary

We conducted a randomized controlled trial testing a **1-step checkout flow** (`treatment`) against the existing **2-step checkout flow** (`control`) across 12,000 unique subjects.

```
                    Control (2-Step)         Treatment (1-Step)
Sample Size:             6,043                     5,957
Conversions:               910                       976
Conversion Rate:        15.06%                    16.38%

Observed Absolute Lift:  +1.32% percentage points
Observed Relative Lift:  +8.83%
Pooled Standard Error:   0.00665
Z-Statistic:             2.0003
Two-Tailed p-value:      0.04547 (Statistically Significant at alpha = 0.05)
95% Confidence Interval: [+0.03%, +2.63%] (relative: [+0.21%, +17.48%])
Guardrail Metric (ARPU): Control: $12.66 vs Treatment: $13.70 (+$1.04, t = 1.602, p = 0.109)
```

**Final Decision**: **Full rollout to 100% of traffic**. The conversion rate lift is statistically significant, the 95% confidence interval strictly excludes zero, and the ARPU guardrail confirmed no basket cannibalization.

---

## 🎓 Master Interview Preparation System

Inside `docs/interview/`, you will find an exhaustive, beginner-friendly curriculum designed to teach and defend every technical line of code:

1. [**01_project_architecture_explained.md**](docs/interview/01_project_architecture_explained.md): Architecture, data flow, tech stack justification, and trade-offs.
2. [**02_file_by_file_code_explanation.md**](docs/interview/02_file_by_file_code_explanation.md): Line-by-line breakdown of every Python function and SQL query.
3. [**03_analytics_fundamentals.md**](docs/interview/03_analytics_fundamentals.md): Theoretical foundations and exact math for 15 core metrics.
4. [**04_project_interview_questions_100.md**](docs/interview/04_project_interview_questions_100.md): 100 Master technical and behavioral Q&As (25 SQL, 20 Python, 20 Product, 15 Business, 10 Stats, 10 Architecture).
5. [**05_project_defense.md**](docs/interview/05_project_defense.md): Comprehensive defense playbook addressing tough interviewer pushbacks.
6. [**06_mock_interview_system.md**](docs/interview/06_mock_interview_system.md): 6-level interactive mock interview simulation with scoring rubrics.
7. [**07_resume_defense.md**](docs/interview/07_resume_defense.md): Defendable resume bullet points with underlying proofs and claims to avoid.
8. [**08_14_day_learning_roadmap.md**](docs/interview/08_14_day_learning_roadmap.md): 14-day study plan covering daily topics, SQL practice, and exercises.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
