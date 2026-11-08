"""
Executive KPI Engine
====================
Computes platform-level financial and operational key performance indicators (KPIs),
growth metrics, rolling averages, and category breakdowns.
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


class KPIEngine:
    """Core financial and operational KPI calculation engine."""

    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or get_engine()

    def load_filtered_orders(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        channels: Optional[list] = None,
        devices: Optional[list] = None,
        categories: Optional[list] = None
    ) -> pd.DataFrame:
        """
        Load orders dataset joined with customers, products, and categories,
        applying dynamic dashboard filters.
        """
        query = """
            SELECT
                o.order_id,
                o.customer_id,
                o.order_date,
                o.order_status,
                o.payment_method,
                o.gross_amount,
                o.discount_amount,
                o.net_amount,
                o.shipping_amount,
                o.tax_amount,
                o.total_cogs,
                o.gross_profit,
                o.profit_margin_pct,
                o.refund_amount,
                c.acquisition_channel,
                c.device_preference,
                c.city_tier,
                p.category
            FROM fact_orders o
            JOIN dim_customers c ON o.customer_id = c.customer_id
            LEFT JOIN (
                SELECT DISTINCT order_id, product_id FROM fact_order_items
            ) oi ON o.order_id = oi.order_id
            LEFT JOIN dim_products p ON oi.product_id = p.product_id
            WHERE 1=1
        """
        params = {}
        if start_date:
            query += " AND o.order_date >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND o.order_date <= :end_date"
            params["end_date"] = end_date
        if channels:
            placeholders = ", ".join([f":ch_{i}" for i in range(len(channels))])
            query += f" AND c.acquisition_channel IN ({placeholders})"
            for i, ch in enumerate(channels):
                params[f"ch_{i}"] = ch
        if devices:
            placeholders = ", ".join([f":dev_{i}" for i in range(len(devices))])
            query += f" AND c.device_preference IN ({placeholders})"
            for i, dev in enumerate(devices):
                params[f"dev_{i}"] = dev
        if categories:
            placeholders = ", ".join([f":cat_{i}" for i in range(len(categories))])
            query += f" AND p.category IN ({placeholders})"
            for i, cat in enumerate(categories):
                params[f"cat_{i}"] = cat

        df = pd.read_sql(query, con=self.engine, params=params)
        # Deduplicate if join on multiple items produced duplicates
        df = df.drop_duplicates(subset=["order_id"])
        return df

    def compute_summary_kpis(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute top-level executive metrics from an orders dataframe.
        """
        total_orders = len(orders_df)
        if total_orders == 0:
            return {
                "total_orders": 0,
                "completed_orders": 0,
                "net_revenue": 0.0,
                "gross_revenue": 0.0,
                "gross_profit": 0.0,
                "profit_margin_pct": 0.0,
                "aov": 0.0,
                "unique_customers": 0,
                "repeat_customer_rate_pct": 0.0,
                "cancellation_rate_pct": 0.0,
                "return_rate_pct": 0.0,
                "total_refunds": 0.0
            }

        completed = orders_df[orders_df["order_status"] == "Completed"]
        cancelled = orders_df[orders_df["order_status"] == "Cancelled"]
        returned = orders_df[orders_df["order_status"] == "Returned"]

        net_rev = float(completed["net_amount"].sum())
        gross_rev = float(completed["gross_amount"].sum())
        gross_profit = float(completed["gross_profit"].sum())
        profit_margin = safe_divide(gross_profit * 100.0, net_rev)
        aov = safe_divide(net_rev, len(completed))

        unique_customers = orders_df["customer_id"].nunique()
        cust_order_counts = completed.groupby("customer_id")["order_id"].count()
        repeat_custs = (cust_order_counts > 1).sum()
        active_buyers = len(cust_order_counts)
        repeat_rate = safe_divide(repeat_custs * 100.0, active_buyers)

        cancel_rate = safe_divide(len(cancelled) * 100.0, total_orders)
        return_rate = safe_divide(len(returned) * 100.0, total_orders)
        total_refunds = float(returned["refund_amount"].sum() + cancelled["refund_amount"].sum())

        return {
            "total_orders": total_orders,
            "completed_orders": len(completed),
            "net_revenue": round(net_rev, 2),
            "gross_revenue": round(gross_rev, 2),
            "gross_profit": round(gross_profit, 2),
            "profit_margin_pct": round(profit_margin, 2),
            "aov": round(aov, 2),
            "unique_customers": unique_customers,
            "repeat_customer_rate_pct": round(repeat_rate, 2),
            "cancellation_rate_pct": round(cancel_rate, 2),
            "return_rate_pct": round(return_rate, 2),
            "total_refunds": round(total_refunds, 2)
        }

    def compute_monthly_trend(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute monthly time-series metrics including MoM growth.
        """
        df = orders_df.copy()
        df["month"] = pd.to_datetime(df["order_date"]).dt.to_period("M").astype(str)

        completed = df[df["order_status"] == "Completed"]
        monthly = completed.groupby("month").agg(
            revenue=("net_amount", "sum"),
            orders=("order_id", "count"),
            customers=("customer_id", "nunique"),
            profit=("gross_profit", "sum")
        ).reset_index()

        monthly["aov"] = (monthly["revenue"] / monthly["orders"]).round(2)
        monthly["margin_pct"] = ((monthly["profit"] / monthly["revenue"]) * 100.0).round(2)

        # MoM growth using shift (equivalent to SQL LAG)
        monthly["prior_month_revenue"] = monthly["revenue"].shift(1)
        monthly["mom_growth_pct"] = (
            ((monthly["revenue"] - monthly["prior_month_revenue"]) / monthly["prior_month_revenue"]) * 100.0
        ).round(2)

        return monthly

    def compute_daily_rolling(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute 7-day and 30-day rolling moving averages of daily revenue.
        """
        completed = orders_df[orders_df["order_status"] == "Completed"].copy()
        completed["date"] = pd.to_datetime(completed["order_date"])

        daily = completed.groupby("date").agg(
            revenue=("net_amount", "sum"),
            orders=("order_id", "count")
        ).reset_index().sort_values("date")

        daily["rolling_7d_revenue"] = daily["revenue"].rolling(window=7, min_periods=1).mean().round(2)
        daily["rolling_30d_revenue"] = daily["revenue"].rolling(window=30, min_periods=1).mean().round(2)

        return daily

    def compute_category_breakdown(self) -> pd.DataFrame:
        """
        Aggregate revenue and profit across catalog product categories.
        """
        query = """
            SELECT
                p.category,
                COUNT(DISTINCT oi.order_id) AS orders,
                SUM(oi.quantity) AS units_sold,
                ROUND(SUM(oi.total_price), 2) AS revenue,
                ROUND(SUM(oi.item_profit), 2) AS profit,
                ROUND((SUM(oi.item_profit) * 100.0) / NULLIF(SUM(oi.total_price), 0), 2) AS margin_pct
            FROM fact_order_items oi
            JOIN dim_products p ON oi.product_id = p.product_id
            JOIN fact_orders o ON oi.order_id = o.order_id
            WHERE o.order_status = 'Completed'
            GROUP BY p.category
            ORDER BY revenue DESC
        """
        return pd.read_sql(query, con=self.engine)


if __name__ == "__main__":
    kpis = KPIEngine()
    df_orders = kpis.load_filtered_orders()
    summary = kpis.compute_summary_kpis(df_orders)
    print("Executive Summary KPIs:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
