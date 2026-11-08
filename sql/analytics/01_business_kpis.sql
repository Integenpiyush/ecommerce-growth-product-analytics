-- ==============================================================================
-- 01_business_kpis.sql: Core Executive Financial & Operational KPIs
-- ==============================================================================
-- Business Questions Answered:
-- 1. What are the platform-level revenue, gross profit, orders, and AOV?
-- 2. What is our month-over-month (MoM) revenue growth?
-- 3. What are the return and cancellation rates impacting our top line?
-- 4. How does the 7-day and 30-day rolling moving average of revenue trend over time?
--
-- Advanced SQL concepts:
-- - Common Table Expressions (CTEs)
-- - Window functions (LAG, SUM OVER, AVG OVER ROWS BETWEEN)
-- - CASE WHEN conditional aggregations
-- - Rounding and safe division
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 1.1: Platform Executive KPI Summary (All-Time Baseline)
-- ------------------------------------------------------------------------------
-- Grain: 1 row summary
WITH order_base AS (
    SELECT
        COUNT(order_id) AS total_orders_placed,
        COUNT(DISTINCT customer_id) AS ordering_customers,
        SUM(CASE WHEN order_status = 'Completed' THEN net_amount ELSE 0 END) AS net_revenue_completed,
        SUM(CASE WHEN order_status = 'Completed' THEN gross_profit ELSE 0 END) AS gross_profit_completed,
        SUM(CASE WHEN order_status = 'Completed' THEN total_cogs ELSE 0 END) AS total_cogs_completed,
        SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
        SUM(CASE WHEN order_status = 'Returned' THEN refund_amount ELSE 0 END) AS total_refunds
    FROM fact_orders
),
customer_base AS (
    SELECT
        COUNT(DISTINCT customer_id) AS total_registered_customers
    FROM dim_customers
),
repeat_orders AS (
    SELECT
        customer_id,
        COUNT(order_id) AS order_count
    FROM fact_orders
    WHERE order_status = 'Completed'
    GROUP BY customer_id
    HAVING COUNT(order_id) > 1
)
SELECT
    c.total_registered_customers,
    o.ordering_customers,
    o.total_orders_placed,
    ROUND(o.net_revenue_completed, 2) AS net_revenue,
    ROUND(o.gross_profit_completed, 2) AS gross_profit,
    ROUND((o.gross_profit_completed * 100.0) / NULLIF(o.net_revenue_completed, 0), 2) AS gross_profit_margin_pct,
    ROUND(o.net_revenue_completed / NULLIF(SUM(CASE WHEN f.order_status = 'Completed' THEN 1 ELSE 0 END), 0), 2) AS average_order_value_aov,
    ROUND((COUNT(DISTINCT r.customer_id) * 100.0) / NULLIF(o.ordering_customers, 0), 2) AS repeat_purchase_rate_pct,
    ROUND((o.cancelled_orders * 100.0) / NULLIF(o.total_orders_placed, 0), 2) AS cancellation_rate_pct,
    ROUND((o.returned_orders * 100.0) / NULLIF(o.total_orders_placed, 0), 2) AS return_rate_pct
FROM order_base o
CROSS JOIN customer_base c
LEFT JOIN repeat_orders r ON 1=1
CROSS JOIN fact_orders f
GROUP BY
    c.total_registered_customers,
    o.ordering_customers,
    o.total_orders_placed,
    o.net_revenue_completed,
    o.gross_profit_completed,
    o.cancelled_orders,
    o.returned_orders;


-- ------------------------------------------------------------------------------
-- Query 1.2: Monthly Revenue Trend & Month-over-Month (MoM) Growth
-- Demonstrates: Window function LAG() to compare prior month revenue
-- ------------------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT
        SUBSTR(order_date, 1, 7) AS order_month,
        COUNT(order_id) AS total_orders,
        SUM(CASE WHEN order_status = 'Completed' THEN 1 ELSE 0 END) AS completed_orders,
        COUNT(DISTINCT customer_id) AS active_customers,
        ROUND(SUM(CASE WHEN order_status = 'Completed' THEN net_amount ELSE 0 END), 2) AS monthly_revenue,
        ROUND(SUM(CASE WHEN order_status = 'Completed' THEN gross_profit ELSE 0 END), 2) AS monthly_profit,
        ROUND(AVG(CASE WHEN order_status = 'Completed' THEN net_amount ELSE NULL END), 2) AS monthly_aov
    FROM fact_orders
    GROUP BY SUBSTR(order_date, 1, 7)
)
SELECT
    order_month,
    total_orders,
    completed_orders,
    active_customers,
    monthly_revenue,
    monthly_profit,
    monthly_aov,
    LAG(monthly_revenue, 1) OVER (ORDER BY order_month) AS prior_month_revenue,
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY order_month)) * 100.0) /
        NULLIF(LAG(monthly_revenue, 1) OVER (ORDER BY order_month), 0),
        2
    ) AS mom_revenue_growth_pct
FROM monthly_metrics
ORDER BY order_month;


-- ------------------------------------------------------------------------------
-- Query 1.3: 7-Day & 30-Day Rolling Moving Average of Revenue
-- Demonstrates: Rolling window frames `ROWS BETWEEN n PRECEDING AND CURRENT ROW`
-- ------------------------------------------------------------------------------
WITH daily_revenue AS (
    SELECT
        order_date,
        SUM(CASE WHEN order_status = 'Completed' THEN net_amount ELSE 0 END) AS daily_completed_revenue,
        COUNT(CASE WHEN order_status = 'Completed' THEN order_id ELSE NULL END) AS daily_completed_orders
    FROM fact_orders
    GROUP BY order_date
)
SELECT
    order_date,
    ROUND(daily_completed_revenue, 2) AS daily_revenue,
    daily_completed_orders,
    ROUND(
        AVG(daily_completed_revenue) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS rolling_7d_avg_revenue,
    ROUND(
        AVG(daily_completed_revenue) OVER (
            ORDER BY order_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS rolling_30d_avg_revenue
FROM daily_revenue
ORDER BY order_date;
