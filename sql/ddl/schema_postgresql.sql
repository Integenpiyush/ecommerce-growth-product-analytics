-- ==============================================================================
-- PostgreSQL Analytical Database DDL
-- Project: E-commerce Growth & Product Analytics Platform
-- Architecture: Kimball Dimensional Model (Star Schema)
-- ==============================================================================

-- Drop tables if exists in reverse dependency order
DROP TABLE IF EXISTS fact_order_items CASCADE;
DROP TABLE IF EXISTS fact_orders CASCADE;
DROP TABLE IF EXISTS fact_sessions CASCADE;
DROP TABLE IF EXISTS fact_marketing_spend CASCADE;
DROP TABLE IF EXISTS fact_ab_experiment CASCADE;
DROP TABLE IF EXISTS dim_products CASCADE;
DROP TABLE IF EXISTS dim_customers CASCADE;
DROP TABLE IF EXISTS dim_dates CASCADE;

-- ------------------------------------------------------------------------------
-- 1. DIMENSION TABLES
-- ------------------------------------------------------------------------------

-- Dim Customers: Customer demographic & initial acquisition profile
-- Grain: 1 row per registered customer
CREATE TABLE dim_customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    signup_date DATE NOT NULL,
    acquisition_channel VARCHAR(50) NOT NULL,
    device_preference VARCHAR(30) NOT NULL,
    city_tier VARCHAR(20) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    age INT CHECK (age >= 18 AND age <= 120),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_customers_signup ON dim_customers(signup_date);
CREATE INDEX idx_dim_customers_channel ON dim_customers(acquisition_channel);
CREATE INDEX idx_dim_customers_city_tier ON dim_customers(city_tier);

-- Dim Products: Product catalog, category hierarchies, and unit economic benchmarks
-- Grain: 1 row per unique product SKU
CREATE TABLE dim_products (
    product_id VARCHAR(32) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50) NOT NULL,
    cost_price NUMERIC(10, 2) NOT NULL CHECK (cost_price >= 0),
    retail_price NUMERIC(10, 2) NOT NULL CHECK (retail_price >= 0),
    target_margin_pct NUMERIC(5, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_products_category ON dim_products(category);
CREATE INDEX idx_dim_products_subcategory ON dim_products(subcategory);

-- Dim Dates: Pre-computed date dimension supporting time intelligence
-- Grain: 1 row per calendar day
CREATE TABLE dim_dates (
    date_key DATE PRIMARY KEY,
    year INT NOT NULL,
    quarter INT NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month INT NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name VARCHAR(20) NOT NULL,
    week_of_year INT NOT NULL CHECK (week_of_year BETWEEN 1 AND 53),
    day_of_month INT NOT NULL CHECK (day_of_month BETWEEN 1 AND 31),
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday_season BOOLEAN NOT NULL
);

CREATE INDEX idx_dim_dates_year_month ON dim_dates(year, month);

-- ------------------------------------------------------------------------------
-- 2. FACT TABLES
-- ------------------------------------------------------------------------------

-- Fact Orders: Transaction header recording sales, costs, discounts, and fulfillment
-- Grain: 1 row per checkout order transaction
CREATE TABLE fact_orders (
    order_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL REFERENCES dim_customers(customer_id),
    session_id VARCHAR(32),
    order_date DATE NOT NULL REFERENCES dim_dates(date_key),
    order_status VARCHAR(20) NOT NULL CHECK (order_status IN ('Completed', 'Cancelled', 'Returned')),
    payment_method VARCHAR(40) NOT NULL,
    gross_amount NUMERIC(10, 2) NOT NULL CHECK (gross_amount >= 0),
    discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0),
    net_amount NUMERIC(10, 2) NOT NULL CHECK (net_amount >= 0),
    shipping_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    tax_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    total_cogs NUMERIC(10, 2) NOT NULL CHECK (total_cogs >= 0),
    gross_profit NUMERIC(10, 2) NOT NULL,
    profit_margin_pct NUMERIC(6, 2),
    refund_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    delivery_days INT,
    return_reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_orders_customer ON fact_orders(customer_id);
CREATE INDEX idx_fact_orders_date ON fact_orders(order_date);
CREATE INDEX idx_fact_orders_status ON fact_orders(order_status);
CREATE INDEX idx_fact_orders_composite_cust_date ON fact_orders(customer_id, order_date);

-- Fact Order Items: Line-item granularity connecting individual products to orders
-- Grain: 1 row per product SKU per order
CREATE TABLE fact_order_items (
    order_item_id VARCHAR(32) PRIMARY KEY,
    order_id VARCHAR(32) NOT NULL REFERENCES fact_orders(order_id) ON DELETE CASCADE,
    product_id VARCHAR(32) NOT NULL REFERENCES dim_products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    unit_cost NUMERIC(10, 2) NOT NULL CHECK (unit_cost >= 0),
    total_price NUMERIC(10, 2) NOT NULL CHECK (total_price >= 0),
    total_cost NUMERIC(10, 2) NOT NULL CHECK (total_cost >= 0),
    item_profit NUMERIC(10, 2) NOT NULL
);

CREATE INDEX idx_fact_order_items_order ON fact_order_items(order_id);
CREATE INDEX idx_fact_order_items_product ON fact_order_items(product_id);

-- Fact Sessions: Clickstream session events and micro-conversion flags
-- Grain: 1 row per user website/app session
CREATE TABLE fact_sessions (
    session_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32) REFERENCES dim_customers(customer_id),
    session_date DATE NOT NULL REFERENCES dim_dates(date_key),
    traffic_channel VARCHAR(50) NOT NULL,
    device VARCHAR(30) NOT NULL,
    pages_viewed INT NOT NULL CHECK (pages_viewed >= 1),
    session_duration_seconds INT NOT NULL CHECK (session_duration_seconds >= 0),
    has_view_item INT NOT NULL CHECK (has_view_item IN (0, 1)),
    has_add_to_cart INT NOT NULL CHECK (has_add_to_cart IN (0, 1)),
    has_begin_checkout INT NOT NULL CHECK (has_begin_checkout IN (0, 1)),
    has_purchase INT NOT NULL CHECK (has_purchase IN (0, 1)),
    order_id VARCHAR(32)
);

CREATE INDEX idx_fact_sessions_date ON fact_sessions(session_date);
CREATE INDEX idx_fact_sessions_device ON fact_sessions(device);
CREATE INDEX idx_fact_sessions_channel ON fact_sessions(traffic_channel);
CREATE INDEX idx_fact_sessions_customer ON fact_sessions(customer_id);

-- Fact Marketing Spend: Channel-level daily acquisition budgets and performance metrics
-- Grain: 1 row per marketing channel per calendar day
CREATE TABLE fact_marketing_spend (
    spend_id SERIAL PRIMARY KEY,
    spend_date DATE NOT NULL REFERENCES dim_dates(date_key),
    channel VARCHAR(50) NOT NULL,
    spend_amount NUMERIC(10, 2) NOT NULL CHECK (spend_amount >= 0),
    impressions INT NOT NULL CHECK (impressions >= 0),
    clicks INT NOT NULL CHECK (clicks >= 0),
    cpc NUMERIC(8, 3) NOT NULL DEFAULT 0.000,
    ctr_pct NUMERIC(6, 2) NOT NULL DEFAULT 0.00,
    CONSTRAINT uq_spend_date_channel UNIQUE (spend_date, channel)
);

CREATE INDEX idx_fact_marketing_spend_date ON fact_marketing_spend(spend_date);
CREATE INDEX idx_fact_marketing_spend_channel ON fact_marketing_spend(channel);

-- Fact AB Experiment: Randomized controlled experiment tracking user assignment & conversion
-- Grain: 1 row per participating experiment subject
CREATE TABLE fact_ab_experiment (
    experiment_user_id VARCHAR(32) PRIMARY KEY,
    experiment_name VARCHAR(100) NOT NULL,
    variant VARCHAR(20) NOT NULL CHECK (variant IN ('control', 'treatment')),
    device VARCHAR(30) NOT NULL,
    assigned_date DATE NOT NULL REFERENCES dim_dates(date_key),
    converted INT NOT NULL CHECK (converted IN (0, 1)),
    revenue NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (revenue >= 0),
    session_duration_seconds INT NOT NULL CHECK (session_duration_seconds >= 0)
);

CREATE INDEX idx_fact_ab_variant ON fact_ab_experiment(variant);
CREATE INDEX idx_fact_ab_converted ON fact_ab_experiment(converted);
CREATE INDEX idx_fact_ab_device ON fact_ab_experiment(device);
