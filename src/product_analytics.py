"""
Product & Funnel Analytics Engine
=================================
Calculates multi-stage conversion funnels, stage-to-stage drop-off rates,
device & channel segmentation, and catalog product performance.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from sqlalchemy.engine import Engine

try:
    from src.database import get_engine
    from src.utils import safe_divide
except ImportError:
    from database import get_engine
    from utils import safe_divide


class ProductAnalyticsEngine:
    """Core product and clickstream funnel analytical engine."""

    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or get_engine()

    def get_funnel_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        devices: Optional[List[str]] = None,
        channels: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calculate total users at each funnel stage and stage-to-stage drop-off rates.
        Stages:
          1. Session Start (100%)
          2. View Item
          3. Add to Cart
          4. Begin Checkout
          5. Purchase Completed
        """
        query = "SELECT * FROM fact_sessions WHERE 1=1"
        params = {}
        if start_date:
            query += " AND session_date >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND session_date <= :end_date"
            params["end_date"] = end_date
        if devices:
            placeholders = ", ".join([f":dev_{i}" for i in range(len(devices))])
            query += f" AND device IN ({placeholders})"
            for i, d in enumerate(devices):
                params[f"dev_{i}"] = d
        if channels:
            placeholders = ", ".join([f":ch_{i}" for i in range(len(channels))])
            query += f" AND traffic_channel IN ({placeholders})"
            for i, c in enumerate(channels):
                params[f"ch_{i}"] = c

        df = pd.read_sql(query, con=self.engine, params=params)

        total_sessions = len(df)
        views = int(df["has_view_item"].sum())
        carts = int(df["has_add_to_cart"].sum())
        checkouts = int(df["has_begin_checkout"].sum())
        purchases = int(df["has_purchase"].sum())

        stages = [
            {
                "stage_order": 1,
                "stage_name": "Session Start",
                "users": total_sessions,
                "overall_conversion_pct": 100.0,
                "stage_conversion_pct": 100.0,
                "drop_off_pct": 0.0,
                "users_lost": 0
            },
            {
                "stage_order": 2,
                "stage_name": "View Item",
                "users": views,
                "overall_conversion_pct": round(safe_divide(views * 100.0, total_sessions), 2),
                "stage_conversion_pct": round(safe_divide(views * 100.0, total_sessions), 2),
                "drop_off_pct": round(safe_divide((total_sessions - views) * 100.0, total_sessions), 2),
                "users_lost": total_sessions - views
            },
            {
                "stage_order": 3,
                "stage_name": "Add to Cart",
                "users": carts,
                "overall_conversion_pct": round(safe_divide(carts * 100.0, total_sessions), 2),
                "stage_conversion_pct": round(safe_divide(carts * 100.0, views), 2),
                "drop_off_pct": round(safe_divide((views - carts) * 100.0, views), 2),
                "users_lost": views - carts
            },
            {
                "stage_order": 4,
                "stage_name": "Begin Checkout",
                "users": checkouts,
                "overall_conversion_pct": round(safe_divide(checkouts * 100.0, total_sessions), 2),
                "stage_conversion_pct": round(safe_divide(checkouts * 100.0, carts), 2),
                "drop_off_pct": round(safe_divide((carts - checkouts) * 100.0, carts), 2),
                "users_lost": carts - checkouts
            },
            {
                "stage_order": 5,
                "stage_name": "Purchase Completed",
                "users": purchases,
                "overall_conversion_pct": round(safe_divide(purchases * 100.0, total_sessions), 2),
                "stage_conversion_pct": round(safe_divide(purchases * 100.0, checkouts), 2),
                "drop_off_pct": round(safe_divide((checkouts - purchases) * 100.0, checkouts), 2),
                "users_lost": checkouts - purchases
            }
        ]

        return pd.DataFrame(stages)

    def get_funnel_by_dimension(self, dimension: str = "device") -> pd.DataFrame:
        """
        Compare funnel conversion rates across a dimension (e.g. 'device' or 'traffic_channel').
        """
        query = f"""
            SELECT
                {dimension},
                COUNT(session_id) AS total_sessions,
                SUM(has_view_item) AS views,
                SUM(has_add_to_cart) AS carts,
                SUM(has_begin_checkout) AS checkouts,
                SUM(has_purchase) AS purchases,
                ROUND((SUM(has_view_item) * 100.0) / COUNT(session_id), 2) AS view_rate_pct,
                ROUND((SUM(has_add_to_cart) * 100.0) / NULLIF(SUM(has_view_item), 0), 2) AS cart_rate_pct,
                ROUND((SUM(has_begin_checkout) * 100.0) / NULLIF(SUM(has_add_to_cart), 0), 2) AS checkout_rate_pct,
                ROUND((SUM(has_purchase) * 100.0) / NULLIF(SUM(has_begin_checkout), 0), 2) AS checkout_to_purchase_pct,
                ROUND((SUM(has_purchase) * 100.0) / COUNT(session_id), 2) AS end_to_end_conversion_pct
            FROM fact_sessions
            GROUP BY {dimension}
            ORDER BY total_sessions DESC
        """
        return pd.read_sql(query, con=self.engine)

    def get_top_performing_products(self, limit: int = 15) -> pd.DataFrame:
        """
        Retrieve highest grossing products with unit volumes and margins.
        """
        query = f"""
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                p.subcategory,
                SUM(oi.quantity) AS units_sold,
                ROUND(SUM(oi.total_price), 2) AS total_revenue,
                ROUND(SUM(oi.item_profit), 2) AS total_profit,
                ROUND((SUM(oi.item_profit) * 100.0) / NULLIF(SUM(oi.total_price), 0), 2) AS margin_pct
            FROM fact_order_items oi
            JOIN dim_products p ON oi.product_id = p.product_id
            JOIN fact_orders o ON oi.order_id = o.order_id
            WHERE o.order_status = 'Completed'
            GROUP BY p.product_id, p.product_name, p.category, p.subcategory
            ORDER BY total_revenue DESC
            LIMIT {limit}
        """
        return pd.read_sql(query, con=self.engine)


if __name__ == "__main__":
    engine = ProductAnalyticsEngine()
    funnel = engine.get_funnel_summary()
    print("Funnel Summary:")
    print(funnel[["stage_name", "users", "overall_conversion_pct", "drop_off_pct"]])
