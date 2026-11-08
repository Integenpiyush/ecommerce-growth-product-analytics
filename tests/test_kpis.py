"""
Unit Tests for KPI Engine & Financial Metrics
"""

import pytest
import pandas as pd
import numpy as np
from src.kpi_engine import KPIEngine
from src.utils import format_currency, format_percentage, calculate_growth_rate, safe_divide


@pytest.fixture
def sample_orders_df():
    """Provides a synthetic fixture of orders with known ground truth."""
    return pd.DataFrame([
        {
            "order_id": "ORD-1",
            "customer_id": "C-1",
            "order_date": "2024-01-10",
            "order_status": "Completed",
            "gross_amount": 100.0,
            "discount_amount": 10.0,
            "net_amount": 90.0,
            "total_cogs": 50.0,
            "gross_profit": 40.0,
            "refund_amount": 0.0
        },
        {
            "order_id": "ORD-2",
            "customer_id": "C-1",
            "order_date": "2024-01-20",
            "order_status": "Completed",
            "gross_amount": 200.0,
            "discount_amount": 20.0,
            "net_amount": 180.0,
            "total_cogs": 100.0,
            "gross_profit": 80.0,
            "refund_amount": 0.0
        },
        {
            "order_id": "ORD-3",
            "customer_id": "C-2",
            "order_date": "2024-02-05",
            "order_status": "Cancelled",
            "gross_amount": 150.0,
            "discount_amount": 0.0,
            "net_amount": 150.0,
            "total_cogs": 70.0,
            "gross_profit": 80.0,
            "refund_amount": 150.0
        },
        {
            "order_id": "ORD-4",
            "customer_id": "C-3",
            "order_date": "2024-02-15",
            "order_status": "Returned",
            "gross_amount": 80.0,
            "discount_amount": 0.0,
            "net_amount": 80.0,
            "total_cogs": 40.0,
            "gross_profit": 40.0,
            "refund_amount": 80.0
        }
    ])


def test_kpi_calculations(sample_orders_df):
    engine = KPIEngine()
    kpis = engine.compute_summary_kpis(sample_orders_df)

    assert kpis["total_orders"] == 4
    assert kpis["completed_orders"] == 2
    # Net revenue should only sum completed orders: 90 + 180 = 270.0
    assert kpis["net_revenue"] == 270.0
    # Gross profit: 40 + 80 = 120.0
    assert kpis["gross_profit"] == 120.0
    # AOV: 270 / 2 = 135.0
    assert kpis["aov"] == 135.0
    # Profit Margin: 120 / 270 * 100 = 44.44%
    assert kpis["profit_margin_pct"] == 44.44
    # Cancellation rate: 1 / 4 = 25.0%
    assert kpis["cancellation_rate_pct"] == 25.0
    # Return rate: 1 / 4 = 25.0%
    assert kpis["return_rate_pct"] == 25.0
    # Repeat customer rate: C-1 has 2 completed orders, C-2 has 0 completed, C-3 has 0 completed.
    # 1 active buyer, 1 repeat buyer -> 100%
    assert kpis["repeat_customer_rate_pct"] == 100.0


def test_growth_rate_utility():
    assert calculate_growth_rate(120.0, 100.0) == 20.0
    assert calculate_growth_rate(80.0, 100.0) == -20.0
    assert calculate_growth_rate(100.0, 0.0) is None
    assert calculate_growth_rate(100.0, None) is None


def test_safe_divide():
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
    assert safe_divide(10, None, default=99.0) == 99.0


def test_formatting_utils():
    assert format_currency(1250000.0) == "$1.25M"
    assert format_currency(1500.5) == "$1,500.50"
    assert format_currency(45.2) == "$45.20"
    assert format_percentage(0.158) == "15.8%"
    assert format_percentage(15.8) == "15.8%"
