# System Architecture & Technical Specifications

This document outlines the system architecture, component design, data flow, and technology choices of the E-commerce Growth & Product Analytics Platform.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Data Generation
        Gen[data_generator.py (Seed: 42)] --> CSV[Raw CSVs (data/raw/)]
    end

    subgraph Data Pipeline & Quality Gate
        CSV --> Val[Data Quality Audit (33 Checks)]
        Val --> Clean[Transformations & Date Dimension]
        Clean --> DB[(Relational Analytical Warehouse)]
    end

    subgraph Analytical Core
        DB --> KPI[kpi_engine.py]
        DB --> Prod[product_analytics.py]
        DB --> Cust[customer_analytics.py]
        DB --> Mktg[marketing_analytics.py]
        DB --> AB[ab_testing.py]
    end

    subgraph Interactive UI
        KPI --> Dash[dashboard/app.py]
        Prod --> Dash
        Cust --> Dash
        Mktg --> Dash
        AB --> Dash
    end
```

---

## 2. Core Components

### 2.1 Synthetic Data Generation Engine (`src/data_generator.py`)
- Seed: `42` (ensuring 100% mathematical reproducibility).
- Realistic business logic:
  - Pareto power-law customer repeat ordering distributions.
  - Device conversion penalties: Mobile has higher drop-offs at PDP and checkout.
  - Multi-tiered product margins across 5 distinct categories.
  - Q4 seasonal surges (Black Friday / holiday shopping patterns).

### 2.2 Production ETL & Validation Engine (`src/etl_pipeline.py`)
- Automated validation gate executing 33 unit checks.
- Pre-computation of order profit margins and calendar dimension (`dim_dates`).
- Atomic transactions ensuring zero partial loads.

### 2.3 Relational Warehouse (`sql/ddl/`)
- Dual dialect compatibility:
  - `schema_postgresql.sql`: Production schema with primary keys, foreign keys, check constraints, and B-tree indices.
  - `schema_sqlite.sql`: Embedded lightweight database for local execution and Streamlit Community Cloud demo mode.

### 2.4 Analytical Engine Layer (`src/`)
- `kpi_engine.py`: Dynamic metric calculations with time slicing and rolling moving averages.
- `product_analytics.py`: Multi-stage funnel event progression and device breakdown.
- `customer_analytics.py`: Quintile-based RFM scoring and monthly cohort retention matrices.
- `marketing_analytics.py`: First-touch attribution, CAC, ROAS, and contribution profit.
- `ab_testing.py`: Two-sample proportion Z-test and Welch's t-test for ARPU.

### 2.5 Presentation Layer (`dashboard/app.py`)
- Streamlit multi-page interface.
- Plotly interactive charts with hover details and zoom/pan.
- Unified sidebar filter state.

---

## 3. Technology Stack Evaluation

| Layer | Technology | Justification |
|---|---|---|
| Language | Python 3.9+ | Ubiquitous analytical standard with high-performance C-extensions (`numpy`, `scipy`). |
| Ingestion & Transformation | Pandas & SQLAlchemy | Reliable vectorized manipulation with database dialect independence. |
| Database Storage | PostgreSQL / SQLite | Enterprise relational rigor paired with zero-friction local portability. |
| Statistical Computing | SciPy (`scipy.stats`) | Proven numerical precision for hypothesis testing and p-value generation. |
| Dashboard Presentation | Streamlit & Plotly | Rapid Python-based reactive dashboard deployment with interactive SVG visuals. |
| Quality Testing | Pytest | Industry standard automated testing framework. |
