"""
Marketing Performance & Acquisition Analytics Engine
=====================================================
Calculates channel-level advertising spend, Customer Acquisition Cost (CAC),
Return on Ad Spend (ROAS), blended vs. paid efficiency, and contribution margins.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from sqlalchemy.engine import Engine

try:
    from src.database import get_engine
    from src.utils import safe_divide
except ImportError:
    from database import get_engine
    from utils import safe_divide


class MarketingAnalyticsEngine:
    """Core marketing attribution and channel performance engine."""

    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or get_engine()

    def get_channel_performance_scorecard(self) -> pd.DataFrame:
        """
        Calculates end-to-end channel acquisition efficiency:
          - Ad Spend, Impressions, Clicks, CPC, CTR
          - Customers Acquired, Attributed Orders, Revenue, Gross Profit
          - CAC, ROAS, Net Contribution Profit
        """
        spend_query = """
            SELECT
                channel,
                ROUND(SUM(spend_amount), 2) AS total_spend,
                SUM(impressions) AS total_impressions,
                SUM(clicks) AS total_clicks,
                ROUND(AVG(cpc), 3) AS avg_cpc,
                ROUND(AVG(ctr_pct), 2) AS avg_ctr_pct
            FROM fact_marketing_spend
            GROUP BY channel
        """
        spend_df = pd.read_sql(spend_query, con=self.engine)

        revenue_query = """
            WITH first_orders AS (
                SELECT
                    c.customer_id,
                    c.acquisition_channel,
                    MIN(o.order_date) AS first_order_date
                FROM dim_customers c
                JOIN fact_orders o ON c.customer_id = o.customer_id
                WHERE o.order_status = 'Completed'
                GROUP BY c.customer_id, c.acquisition_channel
            ),
            cust_counts AS (
                SELECT
                    acquisition_channel,
                    COUNT(DISTINCT customer_id) AS customers_acquired
                FROM first_orders
                GROUP BY acquisition_channel
            ),
            rev_agg AS (
                SELECT
                    c.acquisition_channel,
                    COUNT(DISTINCT o.order_id) AS completed_orders,
                    ROUND(SUM(o.net_amount), 2) AS attributed_revenue,
                    ROUND(SUM(o.gross_profit), 2) AS attributed_profit
                FROM dim_customers c
                JOIN fact_orders o ON c.customer_id = o.customer_id
                WHERE o.order_status = 'Completed'
                GROUP BY c.acquisition_channel
            )
            SELECT
                r.acquisition_channel,
                COALESCE(c.customers_acquired, 0) AS customers_acquired,
                r.completed_orders,
                r.attributed_revenue,
                r.attributed_profit
            FROM rev_agg r
            LEFT JOIN cust_counts c ON r.acquisition_channel = c.acquisition_channel
        """
        rev_df = pd.read_sql(revenue_query, con=self.engine)

        merged = pd.merge(
            spend_df,
            rev_df,
            left_on="channel",
            right_on="acquisition_channel",
            how="outer"
        )
        merged["channel"] = merged["channel"].fillna(merged["acquisition_channel"])
        merged = merged.drop(columns=["acquisition_channel"])

        merged["total_spend"] = merged["total_spend"].fillna(0.0)
        merged["total_impressions"] = merged["total_impressions"].fillna(0)
        merged["total_clicks"] = merged["total_clicks"].fillna(0)
        merged["avg_cpc"] = merged["avg_cpc"].fillna(0.0)
        merged["avg_ctr_pct"] = merged["avg_ctr_pct"].fillna(0.0)
        merged["customers_acquired"] = merged["customers_acquired"].fillna(0)
        merged["completed_orders"] = merged["completed_orders"].fillna(0)
        merged["attributed_revenue"] = merged["attributed_revenue"].fillna(0.0)
        merged["attributed_profit"] = merged["attributed_profit"].fillna(0.0)

        # Unit economics
        merged["cac"] = np.where(
            merged["customers_acquired"] > 0,
            (merged["total_spend"] / merged["customers_acquired"]).round(2),
            0.0
        )
        merged["roas"] = np.where(
            merged["total_spend"] > 0,
            (merged["attributed_revenue"] / merged["total_spend"]).round(2),
            0.0
        )
        merged["contribution_profit"] = (merged["attributed_profit"] - merged["total_spend"]).round(2)
        merged["aov"] = np.where(
            merged["completed_orders"] > 0,
            (merged["attributed_revenue"] / merged["completed_orders"]).round(2),
            0.0
        )

        return merged.sort_values("attributed_revenue", ascending=False)

    def get_monthly_marketing_trend(self) -> pd.DataFrame:
        """
        Monthly trend comparing total marketing spend against total revenue.
        """
        query_spend = """
            SELECT
                SUBSTR(spend_date, 1, 7) AS month,
                ROUND(SUM(spend_amount), 2) AS marketing_spend,
                SUM(impressions) AS impressions,
                SUM(clicks) AS clicks
            FROM fact_marketing_spend
            GROUP BY SUBSTR(spend_date, 1, 7)
        """
        spend = pd.read_sql(query_spend, con=self.engine)

        query_rev = """
            SELECT
                SUBSTR(order_date, 1, 7) AS month,
                ROUND(SUM(net_amount), 2) AS revenue,
                ROUND(SUM(gross_profit), 2) AS gross_profit,
                COUNT(DISTINCT order_id) AS orders
            FROM fact_orders
            WHERE order_status = 'Completed'
            GROUP BY SUBSTR(order_date, 1, 7)
        """
        rev = pd.read_sql(query_rev, con=self.engine)

        merged = pd.merge(spend, rev, on="month", how="inner").sort_values("month")
        merged["monthly_roas"] = (merged["revenue"] / merged["marketing_spend"]).round(2)
        merged["marketing_pct_of_rev"] = ((merged["marketing_spend"] / merged["revenue"]) * 100.0).round(2)
        return merged


if __name__ == "__main__":
    mktg = MarketingAnalyticsEngine()
    scorecard = mktg.get_channel_performance_scorecard()
    print("Channel Performance Scorecard:")
    print(scorecard[["channel", "total_spend", "attributed_revenue", "cac", "roas", "contribution_profit"]])
