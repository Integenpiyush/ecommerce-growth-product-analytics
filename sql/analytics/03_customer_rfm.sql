-- ==============================================================================
-- 03_customer_rfm.sql: Customer Lifetime Segmentation (RFM Analysis)
-- ==============================================================================
-- Business Questions Answered:
-- 1. Which customers are our most valuable advocates (Champions)?
-- 2. How many customers are at risk of churning, and how much revenue do they represent?
-- 3. What percentage of our total revenue is concentrated in top tier customers?
--
-- Advanced SQL concepts:
-- - Date arithmetic for Recency
-- - Window function NTILE(5) for quintile bucket assignment
-- - CASE WHEN logic for behavioral segment classification
-- - Aggregating segment financial metrics
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 3.1: RFM Scoring & Segment Assignment
-- Reference Date: 2024-12-31 (End of operational year)
-- ------------------------------------------------------------------------------
WITH customer_aggregates AS (
    SELECT
        c.customer_id,
        c.acquisition_channel,
        c.city_tier,
        MAX(o.order_date) AS last_order_date,
        -- Calculate Recency in days from reference date '2024-12-31'
        CAST((JULIANDAY('2024-12-31') - JULIANDAY(MAX(o.order_date))) AS INT) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(o.net_amount), 2) AS monetary_value
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.acquisition_channel, c.city_tier
),
rfm_scores AS (
    SELECT
        customer_id,
        acquisition_channel,
        city_tier,
        recency_days,
        frequency,
        monetary_value,
        -- Recency: Lower days = higher score (5 is best)
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        -- Frequency: Higher count = higher score (5 is best)
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        -- Monetary: Higher spend = higher score (5 is best)
        NTILE(5) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM customer_aggregates
),
rfm_segments AS (
    SELECT
        customer_id,
        acquisition_channel,
        city_tier,
        recency_days,
        frequency,
        monetary_value,
        r_score,
        f_score,
        m_score,
        (r_score || f_score || m_score) AS rfm_cell,
        ROUND((r_score + f_score + m_score) / 3.0, 2) AS rfm_composite_score,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent New Customers'
            WHEN r_score >= 3 AND f_score >= 2 AND m_score >= 2 THEN 'Potential Loyalists'
            WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'At Risk (High Value)'
            WHEN r_score <= 2 AND f_score >= 2 THEN 'Hibernating'
            WHEN r_score = 1 AND f_score = 1 THEN 'Lost / Inactive'
            ELSE 'Promising / Needs Attention'
        END AS rfm_segment
    FROM rfm_scores
)
-- Segment Summary: Revenue share and customer density by segment
SELECT
    rfm_segment,
    COUNT(customer_id) AS customer_count,
    ROUND((COUNT(customer_id) * 100.0) / (SELECT COUNT(*) FROM rfm_segments), 2) AS customer_pct,
    ROUND(SUM(monetary_value), 2) AS total_segment_revenue,
    ROUND((SUM(monetary_value) * 100.0) / (SELECT SUM(monetary_value) FROM rfm_segments), 2) AS revenue_share_pct,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 1) AS avg_orders_per_customer,
    ROUND(AVG(monetary_value), 2) AS avg_monetary_ltv
FROM rfm_segments
GROUP BY rfm_segment
ORDER BY total_segment_revenue DESC;
