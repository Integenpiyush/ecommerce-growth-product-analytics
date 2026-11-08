"""
Unit Tests for Product Clickstream Funnel Calculations
"""

import pytest
import pandas as pd
from src.product_analytics import ProductAnalyticsEngine


def test_funnel_monotonic_non_increasing():
    """Verify that funnel stage counts are monotonically non-increasing (stage N+1 <= stage N)."""
    engine = ProductAnalyticsEngine()
    funnel = engine.get_funnel_summary()

    counts = funnel["users"].tolist()
    # [30000, 21399, 9479, 5097, 3097]
    assert len(counts) == 5
    for i in range(len(counts) - 1):
        assert counts[i] >= counts[i + 1], f"Funnel violation: Stage {i} ({counts[i]}) < Stage {i+1} ({counts[i+1]})"


def test_funnel_stage_math():
    """Verify stage conversion and drop-off math."""
    engine = ProductAnalyticsEngine()
    funnel = engine.get_funnel_summary()

    # Session start must be 100% and 0 drop off
    assert funnel.iloc[0]["overall_conversion_pct"] == 100.0
    assert funnel.iloc[0]["drop_off_pct"] == 0.0

    # Step conversion + drop off must equal ~100% for each step
    for idx, row in funnel.iloc[1:].iterrows():
        total_lost = row["users_lost"]
        curr_users = row["users"]
        prior_users = funnel.iloc[idx - 1]["users"]
        assert curr_users + total_lost == prior_users


def test_device_funnel_coverage():
    """Verify all major devices are represented in device breakdown."""
    engine = ProductAnalyticsEngine()
    df_dev = engine.get_funnel_by_dimension("device")
    devices = set(df_dev["device"])
    assert "Desktop" in devices
    assert "Mobile" in devices
    assert "Tablet" in devices
