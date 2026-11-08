-- ==============================================================================
-- 02_product_funnel.sql: Product Clickstream Funnel & Conversion Analytics
-- ==============================================================================
-- Business Questions Answered:
-- 1. Where do users drop off between session landing and order completion?
-- 2. How does the funnel conversion rate diverge between Desktop, Mobile, and Tablet?
-- 3. Which traffic channels deliver the highest intent and funnel progression?
-- 4. Which product categories and individual SKUs generate the highest conversion?
--
-- Advanced SQL concepts:
-- - Multi-tier CTEs for funnel milestones
-- - Conditional ratios and drop-off arithmetic
-- - Granular breakdowns using GROUP BY and CASE
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 2.1: Macro E-commerce Funnel Conversion & Drop-off Rates
-- ------------------------------------------------------------------------------
WITH funnel_counts AS (
    SELECT
        COUNT(session_id) AS total_sessions,
        SUM(has_view_item) AS count_view_item,
        SUM(has_add_to_cart) AS count_add_to_cart,
        SUM(has_begin_checkout) AS count_begin_checkout,
        SUM(has_purchase) AS count_purchase
    FROM fact_sessions
)
SELECT
    'Stage 1: Session Start' AS funnel_stage,
    total_sessions AS users_at_stage,
    100.00 AS pct_of_initial_traffic,
    0.00 AS drop_off_pct
FROM funnel_counts

UNION ALL

SELECT
    'Stage 2: View Item' AS funnel_stage,
    count_view_item AS users_at_stage,
    ROUND((count_view_item * 100.0) / total_sessions, 2) AS pct_of_initial_traffic,
    ROUND(((total_sessions - count_view_item) * 100.0) / total_sessions, 2) AS drop_off_pct
FROM funnel_counts

UNION ALL

SELECT
    'Stage 3: Add to Cart' AS funnel_stage,
    count_add_to_cart AS users_at_stage,
    ROUND((count_add_to_cart * 100.0) / total_sessions, 2) AS pct_of_initial_traffic,
    ROUND(((count_view_item - count_add_to_cart) * 100.0) / NULLIF(count_view_item, 0), 2) AS drop_off_pct
FROM funnel_counts

UNION ALL

SELECT
    'Stage 4: Begin Checkout' AS funnel_stage,
    count_begin_checkout AS users_at_stage,
    ROUND((count_begin_checkout * 100.0) / total_sessions, 2) AS pct_of_initial_traffic,
    ROUND(((count_add_to_cart - count_begin_checkout) * 100.0) / NULLIF(count_add_to_cart, 0), 2) AS drop_off_pct
FROM funnel_counts

UNION ALL

SELECT
    'Stage 5: Purchase Completed' AS funnel_stage,
    count_purchase AS users_at_stage,
    ROUND((count_purchase * 100.0) / total_sessions, 2) AS pct_of_initial_traffic,
    ROUND(((count_begin_checkout - count_purchase) * 100.0) / NULLIF(count_begin_checkout, 0), 2) AS drop_off_pct
FROM funnel_counts;


-- ------------------------------------------------------------------------------
-- Query 2.2: Device-Level Funnel Performance & Conversion Rates
-- Explains the conversion gap between Mobile and Desktop
-- ------------------------------------------------------------------------------
SELECT
    device,
    COUNT(session_id) AS total_sessions,
    SUM(has_view_item) AS views,
    SUM(has_add_to_cart) AS carts,
    SUM(has_begin_checkout) AS checkouts,
    SUM(has_purchase) AS purchases,
    ROUND((SUM(has_view_item) * 100.0) / COUNT(session_id), 2) AS view_rate_pct,
    ROUND((SUM(has_add_to_cart) * 100.0) / NULLIF(SUM(has_view_item), 0), 2) AS cart_rate_pct,
    ROUND((SUM(has_begin_checkout) * 100.0) / NULLIF(SUM(has_add_to_cart), 0), 2) AS checkout_rate_pct,
    ROUND((SUM(has_purchase) * 100.0) / NULLIF(SUM(has_begin_checkout), 0), 2) AS checkout_to_purchase_pct,
    ROUND((SUM(has_purchase) * 100.0) / COUNT(session_id), 2) AS end_to_end_conversion_rate_pct
FROM fact_sessions
GROUP BY device
ORDER BY total_sessions DESC;


-- ------------------------------------------------------------------------------
-- Query 2.3: Channel-Level Funnel Conversion Efficiency
-- Demonstrates which acquisition channels bring high-intent shoppers
-- ------------------------------------------------------------------------------
SELECT
    traffic_channel,
    COUNT(session_id) AS sessions,
    SUM(has_purchase) AS purchases,
    ROUND((SUM(has_purchase) * 100.0) / COUNT(session_id), 2) AS conversion_rate_pct,
    ROUND(AVG(pages_viewed), 2) AS avg_pages_viewed,
    ROUND(AVG(session_duration_seconds), 1) AS avg_duration_sec
FROM fact_sessions
GROUP BY traffic_channel
ORDER BY conversion_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- Query 2.4: Top Product Categories by Volume, Revenue, and Gross Profit
-- Evaluates merchandise performance across departments
-- ------------------------------------------------------------------------------
SELECT
    p.category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.total_price), 2) AS total_revenue,
    ROUND(SUM(oi.item_profit), 2) AS total_profit,
    ROUND((SUM(oi.item_profit) * 100.0) / NULLIF(SUM(oi.total_price), 0), 2) AS profit_margin_pct,
    ROUND(SUM(oi.total_price) / NULLIF(SUM(oi.quantity), 0), 2) AS avg_selling_price
FROM fact_order_items oi
JOIN dim_products p ON oi.product_id = p.product_id
JOIN fact_orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.category
ORDER BY total_revenue DESC;
