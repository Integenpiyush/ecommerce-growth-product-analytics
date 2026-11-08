"""
Unit Tests for Customer RFM Segmentation & Cohort Logic
"""

import pytest
import pandas as pd
from src.customer_analytics import CustomerAnalyticsEngine


def test_rfm_segments_completeness():
    """Verify that all ordering customers receive an RFM segment and valid scores."""
    engine = CustomerAnalyticsEngine()
    rfm_df, summary_df = engine.compute_rfm_segments()

    assert len(rfm_df) > 0
    assert rfm_df["r_score"].isin([1, 2, 3, 4, 5]).all()
    assert rfm_df["f_score"].isin([1, 2, 3, 4, 5]).all()
    assert rfm_df["m_score"].isin([1, 2, 3, 4, 5]).all()
    assert rfm_df["segment"].notnull().all()

    # Verify segment revenue shares sum to 100% (within rounding tolerance)
    assert 99.0 <= summary_df["revenue_share_pct"].sum() <= 101.0
    assert 99.0 <= summary_df["customer_pct"].sum() <= 101.0


def test_cohort_retention_structure():
    """Verify cohort retention matrix structure and bounds."""
    engine = CustomerAnalyticsEngine()
    user_matrix, pct_matrix = engine.compute_cohort_retention_matrix()

    # Month 0 retention must be 100.0% for all cohorts
    assert (pct_matrix[0] == 100.0).all()

    # Subsequent month retention must be between 0% and 100%
    for col in pct_matrix.columns:
        valid_vals = pct_matrix[col].dropna()
        assert (valid_vals >= 0.0).all()
        assert (valid_vals <= 100.0).all()
