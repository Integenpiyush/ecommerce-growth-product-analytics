# Analytical Database Architecture & Schema Design

## 1. Architectural Overview

The **E-commerce Growth & Product Analytics Platform** is built upon a **Kimball Dimensional Model (Star Schema)**. In operational systems (OLTP), third-normal-form (3NF) relational structures are preferred to maximize write throughput and eliminate redundant writes. However, in analytical environments (OLAP), 3NF creates heavily normalized table webs requiring multi-table joins that degrade query latency and confuse business analysts.

The Star Schema decouples numerical business measurements (**Fact Tables**) from business context and filtering attributes (**Dimension Tables**).

```
                   +---------------------+
                   |     dim_dates       |
                   +----------+----------+
                              |
       +----------------------+----------------------+
       |                      |                      |
+------+------+        +------+------+        +------+------+
| fact_orders |        |fact_sessions|        |  fact_mktg  |
+------+------+        +------+------+        +-------------+
       |                      |
       |               +------+------+
+------+-----------+   |dim_customers|
| fact_order_items |   +-------------+
+------+-----------+
       |
+------+-------+
| dim_products |
+--------------+
```

---

## 2. Dimensional Model Justification

### Why Star Schema?
1. **Analytical Performance**: Eliminates recursive joins. A typical executive query requires joining `fact_orders` directly with `dim_customers` and `dim_dates`, minimizing query execution time.
2. **Business User Accessibility**: Queries are predictable, consistent, and intuitive for business stakeholders and BI tools like Streamlit and Metabase.
3. **Decoupled Facts**: Separates disparate business processes (Clickstream Sessions vs. Order Fulfillment vs. Marketing Spend) into distinct fact tables while linking them via conformed dimensions (`dim_dates`, `dim_customers`).

---

## 3. Table Catalog & Detailed Grain Specifications

### 3.1 `dim_customers`
- **Purpose**: Provides persistent customer profile data including original acquisition source, device preference, geographic tier, and demographics.
- **Grain**: Exactly **one record per registered customer** (`customer_id`).
- **Why this grain matters**: Maintains 1-to-many relationship with orders and sessions. If multiple records existed per customer without time validity keys, any order join would duplicate order totals (the dreaded Cartesian fan-out).
- **Primary Key**: `customer_id` (e.g. `CUST-0001`).

### 3.2 `dim_products`
- **Purpose**: Master product catalog maintaining categories, subcategories, cost prices, and retail MSRP.
- **Grain**: Exactly **one record per distinct product SKU** (`product_id`).
- **Why this grain matters**: Anchors product-level margin calculations, category roll-ups, and merchandise performance.
- **Primary Key**: `product_id` (e.g. `PROD-001`).

### 3.3 `dim_dates`
- **Purpose**: Centralized time dimension providing rich calendar attributes (day of week, quarters, holiday seasons, weekend flags) without requiring expensive runtime SQL date parsing.
- **Grain**: Exactly **one record per calendar day** (`date_key`).
- **Why this grain matters**: Guarantees zero date gaps in time-series reporting. When performing cohort analyses or rolling 30-day window functions, joining against `dim_dates` prevents omitted dates from distorting moving averages.
- **Primary Key**: `date_key` (YYYY-MM-DD).

### 3.4 `fact_orders`
- **Purpose**: Captures financial transaction headers—gross sales, discounts, net sales, taxes, shipping, total cost of goods sold (COGS), status (Completed, Cancelled, Returned), and refund amounts.
- **Grain**: Exactly **one record per order placed** (`order_id`).
- **Why this grain matters**: Prevents double-counting of high-level transaction attributes like shipping charges, discount codes applied to the entire basket, and payment fees.
- **Primary Key**: `order_id` (e.g. `ORD-00001`).
- **Foreign Keys**: `customer_id` -> `dim_customers`, `order_date` -> `dim_dates`.

### 3.5 `fact_order_items`
- **Purpose**: Detailed itemized line-items for each product purchased in an order.
- **Grain**: Exactly **one record per product SKU per order** (`order_item_id`).
- **Why this grain matters**: Enables granular basket analysis, product co-purchasing affinity, and category-level gross margin calculations.
- **Primary Key**: `order_item_id` (e.g. `ITEM-000001`).
- **Foreign Keys**: `order_id` -> `fact_orders`, `product_id` -> `dim_products`.

### 3.6 `fact_sessions`
- **Purpose**: Digital clickstream funnel tracking every website or app visit, along with micro-conversion milestones (`has_view_item`, `has_add_to_cart`, `has_begin_checkout`, `has_purchase`).
- **Grain**: Exactly **one record per unique session** (`session_id`).
- **Why this grain matters**: Funnel conversion cannot be accurately measured from order tables alone because 90%+ of visitors bounce before creating an order. Measuring bounce and drop-off requires session-level recording.
- **Primary Key**: `session_id`.
- **Foreign Keys**: `customer_id` (nullable for anonymous visitors), `session_date` -> `dim_dates`.

### 3.7 `fact_marketing_spend`
- **Purpose**: Tracks acquisition expenditures, ad impressions, clicks, CPC, and CTR by channel.
- **Grain**: Exactly **one record per marketing channel per calendar day** (`spend_date`, `channel`).
- **Why this grain matters**: Matches the daily budget reporting cadence of platforms like Google Ads and Meta Ads Manager. Allows accurate Customer Acquisition Cost (CAC) and Return on Ad Spend (ROAS) calculations when blended with daily new customer orders.
- **Primary Key**: Composite (`spend_date`, `channel`).

### 3.8 `fact_ab_experiment`
- **Purpose**: Records randomized variant assignment and conversion outcomes for experimentation.
- **Grain**: Exactly **one record per subject/user assigned to an experiment** (`experiment_user_id`).
- **Why this grain matters**: Strict unit-of-diversion tracking is critical to ensure independence of observations in two-sample hypothesis testing and avoid Unit-of-Analysis violations.
- **Primary Key**: `experiment_user_id`.

---

## 4. Potential Data Duplication & Mitigation Strategy

| Risk Scenario | Cause | Impact | Mitigation Implemented |
|---|---|---|---|
| **Fan-out on Order Join** | Joining `fact_orders` directly with `fact_order_items` when summing revenue | Total revenue is multiplied by the number of line items in each basket | In SQL queries, aggregate `fact_order_items` before joining to `fact_orders`, or query `fact_orders` directly for overall revenue KPIs |
| **Double Counting Guest Sessions** | Guest sessions subsequently associating with a created account | Duplicating visitor counts | Unique `session_id` primary key; session counting uses `COUNT(DISTINCT session_id)` |
| **Marketing Spend Multi-Attribution** | Attempting to join marketing daily spend directly to order line items | Massive duplication of daily spend across every order | Fact-to-Fact joins are prohibited; metrics are aggregated at the conformed `spend_date` and `channel` grain |
| **Pipeline Re-Runs** | Ingesting raw CSV files repeatedly | Duplicate order or customer records | Idempotent table truncates or `ON CONFLICT DO UPDATE` upserts in ETL pipeline |

---

## 5. Storage & Indexing Strategy

1. **B-Tree Indices on Foreign Keys**: Created on `customer_id`, `product_id`, `order_date`, `session_date` to accelerate join lookups.
2. **Composite Indices**: Created on `(customer_id, order_date)` for fast window function execution in RFM and cohort queries.
3. **Low-Cardinality Dimension Filtering**: B-Tree indices on `order_status`, `category`, and `variant` allow PostgreSQL / SQLite query planners to perform index scans on dashboard filter selections.
