"""
Unit Tests for Data Pipeline Validation and Relational Integrity
"""

import pytest
import pandas as pd
from sqlalchemy import text
from src.database import get_engine
from src.etl_pipeline import DataQualityAudit, validate_raw_datasets


def test_database_entity_row_counts():
    """Verify expected operational table record counts in analytical warehouse."""
    engine = get_engine()

    counts = {
        "dim_customers": 2500,
        "dim_products": 120,
        "fact_orders": 18000,
        "fact_order_items": 30142,
        "fact_sessions": 30000,
        "fact_marketing_spend": 1830,
        "fact_ab_experiment": 12000
    }

    with engine.connect() as conn:
        for table, expected_min in counts.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            actual_count = result.scalar()
            assert actual_count >= expected_min, f"Table {table} has {actual_count} rows, expected >= {expected_min}"


def test_no_orphaned_orders():
    """Verify referential integrity between fact_orders and dim_customers."""
    engine = get_engine()
    query = """
        SELECT COUNT(o.order_id)
        FROM fact_orders o
        LEFT JOIN dim_customers c ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """
    df = pd.read_sql(query, con=engine)
    orphans = df.iloc[0, 0]
    assert orphans == 0, f"Found {orphans} orphaned orders without matching customer profile!"


def test_revenue_and_pricing_sanity():
    """Ensure no negative retail prices, costs, or gross amounts exist."""
    engine = get_engine()
    query = """
        SELECT
            (SELECT COUNT(*) FROM dim_products WHERE cost_price < 0 OR retail_price < 0) AS invalid_products,
            (SELECT COUNT(*) FROM fact_orders WHERE gross_amount < 0 OR net_amount < 0) AS invalid_orders
    """
    df = pd.read_sql(query, con=engine)
    assert df.iloc[0]["invalid_products"] == 0
    assert df.iloc[0]["invalid_orders"] == 0
