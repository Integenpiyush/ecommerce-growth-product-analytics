-- ==============================================================================
-- 05_marketing_efficiency.sql: Marketing Spend, CAC, ROAS & Channel Economics
-- ==============================================================================
-- Business Questions Answered:
-- 1. Which acquisition channels deliver the highest Return on Ad Spend (ROAS)?
-- 2. What is our Customer Acquisition Cost (CAC) for each paid acquisition channel?
-- 3. What is the blended CAC vs. Paid CAC?
-- 4. How does ad efficiency (CPC, CTR) correlate with customer order conversion?
--
-- Advanced SQL concepts:
-- - Blending disparate marketing fact data with first-time customer acquisition
-- - Cross-table attribution logic
-- - Calculation of ROAS, CAC, and contribution profit
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 5.1: Channel Performance Scorecard (Spend, Revenue, CAC, ROAS)
-- ------------------------------------------------------------------------------
WITH channel_spend AS (
    SELECT
        channel,
        SUM(spend_amount) AS total_ad_spend,
        SUM(impressions) AS total_impressions,
        SUM(clicks) AS total_clicks,
        ROUND(AVG(cpc), 3) AS avg_cpc,
        ROUND(AVG(ctr_pct), 2) AS avg_ctr_pct
    FROM fact_marketing_spend
    GROUP BY channel
),
customer_first_orders AS (
    SELECT
        c.customer_id,
        c.acquisition_channel,
        MIN(o.order_date) AS first_order_date
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.acquisition_channel
),
channel_customers AS (
    SELECT
        acquisition_channel,
        COUNT(DISTINCT customer_id) AS acquired_customers
    FROM customer_first_orders
    GROUP BY acquisition_channel
),
channel_revenue AS (
    SELECT
        c.acquisition_channel,
        ROUND(SUM(o.net_amount), 2) AS attributed_total_revenue,
        ROUND(SUM(o.gross_profit), 2) AS attributed_gross_profit,
        COUNT(DISTINCT o.order_id) AS total_orders
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.acquisition_channel
)
SELECT
    COALESCE(s.channel, r.acquisition_channel) AS marketing_channel,
    COALESCE(s.total_ad_spend, 0.00) AS total_spend,
    COALESCE(s.total_impressions, 0) AS total_impressions,
    COALESCE(s.total_clicks, 0) AS total_clicks,
    COALESCE(s.avg_cpc, 0.00) AS avg_cpc,
    COALESCE(s.avg_ctr_pct, 0.00) AS avg_ctr_pct,
    COALESCE(c.acquired_customers, 0) AS customers_acquired,
    COALESCE(r.total_orders, 0) AS completed_orders,
    COALESCE(r.attributed_total_revenue, 0.00) AS attributed_revenue,
    COALESCE(r.attributed_gross_profit, 0.00) AS attributed_profit,
    -- Customer Acquisition Cost (CAC) = Total Spend / Customers Acquired
    ROUND(COALESCE(s.total_ad_spend, 0.00) / NULLIF(c.acquired_customers, 0), 2) AS customer_acquisition_cost_cac,
    -- Return on Ad Spend (ROAS) = Attributed Revenue / Total Ad Spend
    ROUND(COALESCE(r.attributed_total_revenue, 0.00) / NULLIF(s.total_ad_spend, 0), 2) AS return_on_ad_spend_roas,
    -- Contribution Profit = Attributed Profit - Total Spend
    ROUND(COALESCE(r.attributed_gross_profit, 0.00) - COALESCE(s.total_ad_spend, 0.00), 2) AS net_channel_contribution_profit
FROM channel_spend s
FULL OUTER JOIN channel_revenue r ON s.channel = r.acquisition_channel
LEFT JOIN channel_customers c ON COALESCE(s.channel, r.acquisition_channel) = c.acquisition_channel
ORDER BY attributed_revenue DESC;


-- ------------------------------------------------------------------------------
-- Query 5.2: Monthly Blended CAC vs Paid CAC
-- Compares overall efficiency against paid advertising channels
-- ------------------------------------------------------------------------------
WITH monthly_spend AS (
    SELECT
        SUBSTR(spend_date, 1, 7) AS spend_month,
        SUM(spend_amount) AS total_marketing_spend,
        SUM(CASE WHEN channel IN ('Paid Search', 'Paid Social') THEN spend_amount ELSE 0 END) AS paid_channel_spend
    FROM fact_marketing_spend
    GROUP BY SUBSTR(spend_date, 1, 7)
),
customer_first_orders AS (
    SELECT
        c.customer_id,
        c.acquisition_channel,
        MIN(o.order_date) AS first_order_date,
        SUBSTR(MIN(o.order_date), 1, 7) AS cohort_month
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.acquisition_channel
),
monthly_acquisitions AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_new_customers,
        COUNT(DISTINCT CASE WHEN acquisition_channel IN ('Paid Search', 'Paid Social') THEN customer_id ELSE NULL END) AS paid_new_customers
    FROM customer_first_orders
    GROUP BY cohort_month
)
SELECT
    s.spend_month,
    s.total_marketing_spend,
    s.paid_channel_spend,
    a.total_new_customers,
    a.paid_new_customers,
    -- Blended CAC: Total marketing spend / All new customers
    ROUND(s.total_marketing_spend / NULLIF(a.total_new_customers, 0), 2) AS blended_cac,
    -- Paid CAC: Paid media spend / Customers acquired via paid media
    ROUND(s.paid_channel_spend / NULLIF(a.paid_new_customers, 0), 2) AS paid_cac
FROM monthly_spend s
JOIN monthly_acquisitions a ON s.spend_month = a.cohort_month
ORDER BY s.spend_month ASC;
