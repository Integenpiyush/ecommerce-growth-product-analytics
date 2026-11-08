-- ==============================================================================
-- SQLite Analytical Database DDL (Demo & Standalone Execution Mode)
-- Project: E-commerce Growth & Product Analytics Platform
-- Architecture: Kimball Dimensional Model (Star Schema)
-- ==============================================================================

DROP TABLE IF EXISTS fact_order_items;
DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS fact_sessions;
DROP TABLE IF EXISTS fact_marketing_spend;
DROP TABLE IF EXISTS fact_ab_experiment;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_customers;
DROP TABLE IF EXISTS dim_dates;

CREATE TABLE dim_customers (
    customer_id TEXT PRIMARY KEY,
    signup_date TEXT NOT NULL,
    acquisition_channel TEXT NOT NULL,
    device_preference TEXT NOT NULL,
    city_tier TEXT NOT NULL,
    gender TEXT NOT NULL,
    age INTEGER CHECK (age >= 18 AND age <= 120),
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_customers_signup ON dim_customers(signup_date);
CREATE INDEX idx_dim_customers_channel ON dim_customers(acquisition_channel);

CREATE TABLE dim_products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    cost_price REAL NOT NULL CHECK (cost_price >= 0),
    retail_price REAL NOT NULL CHECK (retail_price >= 0),
    target_margin_pct REAL NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_products_category ON dim_products(category);

CREATE TABLE dim_dates (
    date_key TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    is_weekend INTEGER NOT NULL,
    is_holiday_season INTEGER NOT NULL
);

CREATE TABLE fact_orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES dim_customers(customer_id),
    session_id TEXT,
    order_date TEXT NOT NULL REFERENCES dim_dates(date_key),
    order_status TEXT NOT NULL CHECK (order_status IN ('Completed', 'Cancelled', 'Returned')),
    payment_method TEXT NOT NULL,
    gross_amount REAL NOT NULL CHECK (gross_amount >= 0),
    discount_amount REAL NOT NULL DEFAULT 0.00,
    net_amount REAL NOT NULL CHECK (net_amount >= 0),
    shipping_amount REAL NOT NULL DEFAULT 0.00,
    tax_amount REAL NOT NULL DEFAULT 0.00,
    total_cogs REAL NOT NULL CHECK (total_cogs >= 0),
    gross_profit REAL NOT NULL,
    profit_margin_pct REAL,
    refund_amount REAL NOT NULL DEFAULT 0.00,
    delivery_days INTEGER,
    return_reason TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_orders_customer ON fact_orders(customer_id);
CREATE INDEX idx_fact_orders_date ON fact_orders(order_date);
CREATE INDEX idx_fact_orders_status ON fact_orders(order_status);

CREATE TABLE fact_order_items (
    order_item_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES fact_orders(order_id) ON DELETE CASCADE,
    product_id TEXT NOT NULL REFERENCES dim_products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    unit_cost REAL NOT NULL CHECK (unit_cost >= 0),
    total_price REAL NOT NULL CHECK (total_price >= 0),
    total_cost REAL NOT NULL CHECK (total_cost >= 0),
    item_profit REAL NOT NULL
);

CREATE INDEX idx_fact_order_items_order ON fact_order_items(order_id);
CREATE INDEX idx_fact_order_items_product ON fact_order_items(product_id);

CREATE TABLE fact_sessions (
    session_id TEXT PRIMARY KEY,
    customer_id TEXT REFERENCES dim_customers(customer_id),
    session_date TEXT NOT NULL REFERENCES dim_dates(date_key),
    traffic_channel TEXT NOT NULL,
    device TEXT NOT NULL,
    pages_viewed INTEGER NOT NULL,
    session_duration_seconds INTEGER NOT NULL,
    has_view_item INTEGER NOT NULL,
    has_add_to_cart INTEGER NOT NULL,
    has_begin_checkout INTEGER NOT NULL,
    has_purchase INTEGER NOT NULL,
    order_id TEXT
);

CREATE INDEX idx_fact_sessions_date ON fact_sessions(session_date);
CREATE INDEX idx_fact_sessions_device ON fact_sessions(device);
CREATE INDEX idx_fact_sessions_channel ON fact_sessions(traffic_channel);

CREATE TABLE fact_marketing_spend (
    spend_id INTEGER PRIMARY KEY AUTOINCREMENT,
    spend_date TEXT NOT NULL REFERENCES dim_dates(date_key),
    channel TEXT NOT NULL,
    spend_amount REAL NOT NULL CHECK (spend_amount >= 0),
    impressions INTEGER NOT NULL CHECK (impressions >= 0),
    clicks INTEGER NOT NULL CHECK (clicks >= 0),
    cpc REAL NOT NULL DEFAULT 0.0,
    ctr_pct REAL NOT NULL DEFAULT 0.0,
    UNIQUE (spend_date, channel)
);

CREATE INDEX idx_fact_marketing_spend_date ON fact_marketing_spend(spend_date);
CREATE INDEX idx_fact_marketing_spend_channel ON fact_marketing_spend(channel);

CREATE TABLE fact_ab_experiment (
    experiment_user_id TEXT PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    variant TEXT NOT NULL CHECK (variant IN ('control', 'treatment')),
    device TEXT NOT NULL,
    assigned_date TEXT NOT NULL REFERENCES dim_dates(date_key),
    converted INTEGER NOT NULL CHECK (converted IN (0, 1)),
    revenue REAL NOT NULL DEFAULT 0.0 CHECK (revenue >= 0),
    session_duration_seconds INTEGER NOT NULL
);

CREATE INDEX idx_fact_ab_variant ON fact_ab_experiment(variant);
CREATE INDEX idx_fact_ab_converted ON fact_ab_experiment(converted);
