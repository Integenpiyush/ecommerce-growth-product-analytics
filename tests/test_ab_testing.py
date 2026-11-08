"""
Unit Tests for A/B Testing & Statistical Experimentation
"""

import pytest
import numpy as np
import pandas as pd
from src.ab_testing import ExperimentAnalyzer


@pytest.fixture
def synthetic_experiment_df():
    """Constructs controlled experiment with known lift and conversion."""
    np.random.seed(42)
    n = 2000
    ctrl_conv = np.random.binomial(1, 0.10, n)
    treat_conv = np.random.binomial(1, 0.14, n)

    df_ctrl = pd.DataFrame({
        "variant": ["control"] * n,
        "converted": ctrl_conv,
        "revenue": ctrl_conv * 50.0,
        "device": ["Mobile"] * n
    })
    df_treat = pd.DataFrame({
        "variant": ["treatment"] * n,
        "converted": treat_conv,
        "revenue": treat_conv * 50.0,
        "device": ["Mobile"] * n
    })
    return pd.concat([df_ctrl, df_treat], ignore_index=True)


def test_proportion_z_test_significance(synthetic_experiment_df):
    analyzer = ExperimentAnalyzer()
    res = analyzer.run_proportion_test(synthetic_experiment_df)

    assert res["n_control"] == 2000
    assert res["n_treatment"] == 2000
    assert res["conversion_rate_control"] < res["conversion_rate_treatment"]
    assert res["absolute_lift"] > 0
    assert res["relative_lift_pct"] > 0
    assert res["z_statistic"] > 2.0
    assert res["p_value"] < 0.05
    assert res["is_statistically_significant"] is True
    # CI should strictly exclude 0 for this strong lift
    assert res["ci_lower_abs"] > 0


def test_welch_t_test_arpu(synthetic_experiment_df):
    analyzer = ExperimentAnalyzer()
    res = analyzer.run_arpu_test(synthetic_experiment_df)

    assert res["arpu_treatment"] > res["arpu_control"]
    assert res["arpu_absolute_lift"] > 0
    assert res["t_statistic"] > 2.0
    assert res["p_value"] < 0.05
    assert res["is_significant"] is True


def test_identical_variants_edge_case():
    """Verify test handles 0 lift gracefully."""
    df_null = pd.DataFrame({
        "variant": ["control"] * 500 + ["treatment"] * 500,
        "converted": [1] * 50 + [0] * 450 + [1] * 50 + [0] * 450,
        "revenue": [20.0] * 50 + [0.0] * 450 + [20.0] * 50 + [0.0] * 450
    })
    analyzer = ExperimentAnalyzer()
    res = analyzer.run_proportion_test(df_null)

    assert res["absolute_lift"] == 0.0
    assert res["relative_lift_pct"] == 0.0
    assert res["z_statistic"] == 0.0
    assert res["p_value"] == 1.0
    assert res["is_statistically_significant"] is False
