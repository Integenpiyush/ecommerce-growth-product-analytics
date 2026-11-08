-- ==============================================================================
-- 04_cohort_retention.sql: Customer Cohort Retention & Cumulative LTV Progression
-- ==============================================================================
-- Business Questions Answered:
-- 1. How sticky is our customer base over 30, 60, 90, 180, and 360 days?
-- 2. Do newer cohorts retain better or worse than older cohorts?
-- 3. What is the cumulative Customer Lifetime Value (LTV) progression by cohort?
--
-- Advanced SQL concepts:
-- - Identifying customer cohort month using FIRST_VALUE() or MIN() over window
-- - Calculating month index distance (`order_month - cohort_month`)
-- - Aggregating distinct customers per cohort-month index
-- - Pivot/matrix logic for retention visualization
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 4.1: Monthly Customer Acquisition Cohort Retention Grid
-- Tracks active buyers in Month 0, 1, 2, 3... up to 11
-- ------------------------------------------------------------------------------
WITH customer_cohort AS (
    SELECT
        customer_id,
        MIN(SUBSTR(order_date, 1, 7)) AS cohort_month
    FROM fact_orders
    WHERE order_status = 'Completed'
    GROUP BY customer_id
),
order_activity AS (
    SELECT
        o.customer_id,
        c.cohort_month,
        SUBSTR(o.order_date, 1, 7) AS activity_month,
        -- Month index calculation: (year_diff * 12) + (month_diff)
        (
            (CAST(SUBSTR(o.order_date, 1, 4) AS INT) - CAST(SUBSTR(c.cohort_month, 1, 4) AS INT)) * 12 +
            (CAST(SUBSTR(o.order_date, 6, 2) AS INT) - CAST(SUBSTR(c.cohort_month, 6, 2) AS INT))
        ) AS month_number,
        o.net_amount
    FROM fact_orders o
    JOIN customer_cohort c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'Completed'
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohort
    GROUP BY cohort_month
),
retention_counts AS (
    SELECT
        a.cohort_month,
        s.cohort_size,
        a.month_number,
        COUNT(DISTINCT a.customer_id) AS active_users,
        ROUND(SUM(a.net_amount), 2) AS month_revenue
    FROM order_activity a
    JOIN cohort_sizes s ON a.cohort_month = s.cohort_month
    GROUP BY a.cohort_month, s.cohort_size, a.month_number
)
SELECT
    cohort_month,
    cohort_size,
    month_number,
    active_users,
    ROUND((active_users * 100.0) / cohort_size, 2) AS retention_rate_pct,
    month_revenue,
    ROUND(month_revenue / cohort_size, 2) AS revenue_per_cohort_member
FROM retention_counts
ORDER BY cohort_month ASC, month_number ASC;


-- ------------------------------------------------------------------------------
-- Query 4.2: Cumulative Cohort LTV Progression
-- Demonstrates: Window function SUM() OVER (PARTITION BY cohort ORDER BY month)
-- ------------------------------------------------------------------------------
WITH customer_cohort AS (
    SELECT
        customer_id,
        MIN(SUBSTR(order_date, 1, 7)) AS cohort_month
    FROM fact_orders
    WHERE order_status = 'Completed'
    GROUP BY customer_id
),
monthly_cohort_revenue AS (
    SELECT
        c.cohort_month,
        (
            (CAST(SUBSTR(o.order_date, 1, 4) AS INT) - CAST(SUBSTR(c.cohort_month, 1, 4) AS INT)) * 12 +
            (CAST(SUBSTR(o.order_date, 6, 2) AS INT) - CAST(SUBSTR(c.cohort_month, 6, 2) AS INT))
        ) AS month_number,
        COUNT(DISTINCT c.customer_id) OVER (PARTITION BY c.cohort_month) AS cohort_size,
        SUM(o.net_amount) AS incremental_revenue
    FROM fact_orders o
    JOIN customer_cohort c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.cohort_month, month_number
)
SELECT
    cohort_month,
    month_number,
    ROUND(incremental_revenue, 2) AS incremental_revenue,
    ROUND(
        SUM(incremental_revenue) OVER (
            PARTITION BY cohort_month
            ORDER BY month_number
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS cumulative_cohort_revenue,
    ROUND(
        (SUM(incremental_revenue) OVER (
            PARTITION BY cohort_month
            ORDER BY month_number
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )) / NULLIF(cohort_size, 0),
        2
    ) AS cumulative_ltv_per_customer
FROM monthly_cohort_revenue
ORDER BY cohort_month, month_number;
