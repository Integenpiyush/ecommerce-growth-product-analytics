"""
Customer Analytics & Segmentation Engine
========================================
Implements RFM (Recency, Frequency, Monetary) scoring, customer lifecycle segmentation,
and monthly cohort retention matrices.
"""

from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sqlalchemy.engine import Engine

try:
    from src.database import get_engine
    from src.utils import safe_divide
except ImportError:
    from database import get_engine
    from utils import safe_divide


class CustomerAnalyticsEngine:
    """Core customer behavioral and lifecycle analytical engine."""

    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or get_engine()

    def compute_rfm_segments(self, reference_date: str = "2024-12-31") -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Calculates R, F, M metrics for each customer and assigns behavioral segments.
        Returns:
          - customers_rfm_df: Customer-level RFM scores and segment labels
          - segment_summary_df: Segment-level aggregated revenue, size, and averages
        """
        ref_dt = pd.to_datetime(reference_date)

        query = """
            SELECT
                c.customer_id,
                c.acquisition_channel,
                c.device_preference,
                c.city_tier,
                o.order_id,
                o.order_date,
                o.net_amount
            FROM dim_customers c
            JOIN fact_orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'Completed'
        """
        df = pd.read_sql(query, con=self.engine)
        df["order_date"] = pd.to_datetime(df["order_date"])

        # Customer-level aggregation
        rfm = df.groupby(["customer_id", "acquisition_channel", "device_preference", "city_tier"]).agg(
            last_order_date=("order_date", "max"),
            frequency=("order_id", "nunique"),
            monetary_value=("net_amount", "sum")
        ).reset_index()

        rfm["recency_days"] = (ref_dt - rfm["last_order_date"]).dt.days
        rfm["monetary_value"] = rfm["monetary_value"].round(2)

        # Quintile scoring (1 to 5)
        # Recency: Lower days is better -> reverse ranks
        rfm["r_score"] = pd.qcut(rfm["recency_days"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)

        # Frequency: Rank with method='first' to handle tied low frequencies
        rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

        # Monetary
        rfm["m_score"] = pd.qcut(rfm["monetary_value"], q=5, labels=[1, 2, 3, 4, 5]).astype(int)

        # RFM composite score
        rfm["rfm_composite"] = ((rfm["r_score"] + rfm["f_score"] + rfm["m_score"]) / 3.0).round(2)

        # Behavioral segment assignment rule
        def assign_segment(row):
            r, f, m = row["r_score"], row["f_score"], row["m_score"]
            if r >= 4 and f >= 4 and m >= 4:
                return "Champions"
            elif r >= 3 and f >= 3 and m >= 3:
                return "Loyal Customers"
            elif r >= 4 and f <= 2:
                return "Recent New Customers"
            elif r >= 3 and f >= 2 and m >= 2:
                return "Potential Loyalists"
            elif r <= 2 and f >= 4 and m >= 4:
                return "At Risk (High Value)"
            elif r <= 2 and f >= 2:
                return "Hibernating"
            elif r == 1 and f == 1:
                return "Lost / Inactive"
            else:
                return "Promising / Needs Attention"

        rfm["segment"] = rfm.apply(assign_segment, axis=1)

        # Segment summary
        total_customers = len(rfm)
        total_revenue = rfm["monetary_value"].sum()

        summary = rfm.groupby("segment").agg(
            customer_count=("customer_id", "count"),
            total_revenue=("monetary_value", "sum"),
            avg_recency_days=("recency_days", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary_value", "mean")
        ).reset_index()

        summary["customer_pct"] = ((summary["customer_count"] / total_customers) * 100.0).round(2)
        summary["revenue_share_pct"] = ((summary["total_revenue"] / total_revenue) * 100.0).round(2)
        summary["avg_recency_days"] = summary["avg_recency_days"].round(1)
        summary["avg_frequency"] = summary["avg_frequency"].round(1)
        summary["avg_monetary"] = summary["avg_monetary"].round(2)
        summary = summary.sort_values("total_revenue", ascending=False)

        return rfm, summary

    def compute_cohort_retention_matrix(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Computes monthly acquisition cohort customer counts and percentage retention matrix.
        Returns:
          - retention_users_matrix: Pivot table of active user counts
          - retention_pct_matrix: Pivot table of retention percentages
        """
        query = """
            SELECT
                customer_id,
                order_date,
                net_amount
            FROM fact_orders
            WHERE order_status = 'Completed'
        """
        df = pd.read_sql(query, con=self.engine)
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["order_month"] = df["order_date"].dt.to_period("M")

        # Cohort month: First order month
        first_order = df.groupby("customer_id")["order_month"].min().reset_index()
        first_order.rename(columns={"order_month": "cohort_month"}, inplace=True)

        merged = df.merge(first_order, on="customer_id")
        # Month distance
        merged["month_index"] = (
            (merged["order_month"].dt.year - merged["cohort_month"].dt.year) * 12 +
            (merged["order_month"].dt.month - merged["cohort_month"].dt.month)
        )

        cohort_data = merged.groupby(["cohort_month", "month_index"]).agg(
            active_customers=("customer_id", "nunique"),
            revenue=("net_amount", "sum")
        ).reset_index()

        cohort_data["cohort_month_str"] = cohort_data["cohort_month"].astype(str)

        # Pivot for user counts
        user_matrix = cohort_data.pivot(index="cohort_month_str", columns="month_index", values="active_customers").fillna(0)

        # Cohort base size (Month 0 size)
        cohort_sizes = user_matrix[0]
        pct_matrix = (user_matrix.divide(cohort_sizes, axis=0) * 100.0).round(1)

        return user_matrix, pct_matrix


if __name__ == "__main__":
    cust_engine = CustomerAnalyticsEngine()
    rfm_df, rfm_summary = cust_engine.compute_rfm_segments()
    print("RFM Segment Summary:")
    print(rfm_summary[["segment", "customer_count", "customer_pct", "total_revenue", "revenue_share_pct"]])

    user_mat, pct_mat = cust_engine.compute_cohort_retention_matrix()
    print("\nCohort Retention Matrix (%):")
    print(pct_mat.iloc[:5, :6])
