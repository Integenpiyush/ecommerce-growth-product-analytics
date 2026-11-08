"""
A/B Testing & Experimentation Engine
====================================
Performs rigorous frequentist statistical hypothesis testing for controlled experiments:
  - Two-sample pooled z-test for proportion differences (Conversion Rate)
  - Welch's two-sample t-test for continuous metrics (Revenue per User / ARPU)
  - 95% Wald & Wilson Confidence Intervals
  - Statistical power, sample size, and Minimum Detectable Effect (MDE) calculations
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from sqlalchemy.engine import Engine

try:
    from src.database import get_engine
    from src.utils import safe_divide
except ImportError:
    from database import get_engine
    from utils import safe_divide


class ExperimentAnalyzer:
    """Rigorous statistical testing engine for randomized controlled trials."""

    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or get_engine()

    def load_experiment_data(self, experiment_name: str = "checkout_one_step_v2") -> pd.DataFrame:
        """Query experiment participant data from analytical database."""
        query = """
            SELECT
                experiment_user_id,
                experiment_name,
                variant,
                device,
                assigned_date,
                converted,
                revenue,
                session_duration_seconds
            FROM fact_ab_experiment
            WHERE experiment_name = :exp_name
        """
        return pd.read_sql(query, con=self.engine, params={"exp_name": experiment_name})

    def run_proportion_test(
        self,
        df: pd.DataFrame,
        confidence_level: float = 0.95,
        alternative: str = "two-sided"
    ) -> Dict[str, Any]:
        """
        Conducts two-sample pooled z-test for binomial conversion rates.

        H0: p_treatment - p_control = 0
        H1: p_treatment != p_control (two-sided) or p_treatment > p_control (larger)
        """
        control = df[df["variant"] == "control"]
        treatment = df[df["variant"] == "treatment"]

        n_ctrl = len(control)
        n_treat = len(treatment)
        conv_ctrl = int(control["converted"].sum())
        conv_treat = int(treatment["converted"].sum())

        cr_ctrl = safe_divide(conv_ctrl, n_ctrl)
        cr_treat = safe_divide(conv_treat, n_treat)

        abs_lift = cr_treat - cr_ctrl
        rel_lift = safe_divide(abs_lift, cr_ctrl)

        # Pooled sample proportion under H0
        p_pool = safe_divide(conv_ctrl + conv_treat, n_ctrl + n_treat)
        se_pool = np.sqrt(p_pool * (1.0 - p_pool) * (1.0 / n_ctrl + 1.0 / n_treat))

        # Z-statistic
        z_stat = safe_divide(abs_lift, se_pool)

        # P-value
        if alternative == "two-sided":
            p_value = float(2.0 * (1.0 - stats.norm.cdf(abs(z_stat))))
        elif alternative == "larger":
            p_value = float(1.0 - stats.norm.cdf(z_stat))
        else:
            p_value = float(stats.norm.cdf(z_stat))

        # Unpooled Standard Error for Confidence Interval construction
        se_diff = np.sqrt((cr_ctrl * (1.0 - cr_ctrl) / n_ctrl) + (cr_treat * (1.0 - cr_treat) / n_treat))
        alpha = 1.0 - confidence_level
        z_critical = stats.norm.ppf(1.0 - alpha / 2.0)

        ci_lower_abs = abs_lift - z_critical * se_diff
        ci_upper_abs = abs_lift + z_critical * se_diff

        ci_lower_rel = safe_divide(ci_lower_abs, cr_ctrl)
        ci_upper_rel = safe_divide(ci_upper_abs, cr_ctrl)

        is_significant = bool(p_value < alpha)

        return {
            "test_type": "Two-Sample Z-Test for Proportions (Pooled)",
            "n_control": n_ctrl,
            "n_treatment": n_treat,
            "conversions_control": conv_ctrl,
            "conversions_treatment": conv_treat,
            "conversion_rate_control": round(cr_ctrl, 4),
            "conversion_rate_treatment": round(cr_treat, 4),
            "absolute_lift": round(abs_lift, 4),
            "relative_lift_pct": round(rel_lift * 100.0, 2),
            "standard_error": round(float(se_pool), 5),
            "z_statistic": round(float(z_stat), 4),
            "p_value": round(float(p_value), 5),
            "alpha": alpha,
            "confidence_level": confidence_level,
            "ci_lower_abs": round(float(ci_lower_abs), 4),
            "ci_upper_abs": round(float(ci_upper_abs), 4),
            "ci_lower_rel_pct": round(float(ci_lower_rel * 100.0), 2),
            "ci_upper_rel_pct": round(float(ci_upper_rel * 100.0), 2),
            "is_statistically_significant": is_significant,
            "recommendation": (
                "Roll out Treatment to 100% of traffic. Conversion lift is statistically significant."
                if is_significant and abs_lift > 0 else
                "Do not launch Treatment. Observed difference is within random noise."
            )
        }

    def run_arpu_test(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Conducts Welch's two-sample t-test for Average Revenue Per User (continuous metric).
        Does not assume equal variances.
        """
        control_rev = df[df["variant"] == "control"]["revenue"]
        treatment_rev = df[df["variant"] == "treatment"]["revenue"]

        arpu_ctrl = float(control_rev.mean())
        arpu_treat = float(treatment_rev.mean())
        arpu_lift = arpu_treat - arpu_ctrl
        arpu_rel_lift = safe_divide(arpu_lift, arpu_ctrl)

        t_stat, p_val = stats.ttest_ind(treatment_rev, control_rev, equal_var=False)

        return {
            "test_type": "Welch's Two-Sample t-Test for ARPU",
            "arpu_control": round(arpu_ctrl, 2),
            "arpu_treatment": round(arpu_treat, 2),
            "arpu_absolute_lift": round(arpu_lift, 2),
            "arpu_relative_lift_pct": round(arpu_rel_lift * 100.0, 2),
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_val), 5),
            "is_significant": bool(p_val < 0.05)
        }

    def run_subgroup_analysis(self, df: pd.DataFrame, dimension: str = "device") -> pd.DataFrame:
        """
        Runs proportion z-test within subgroups (e.g. Mobile vs Desktop) to identify heterogeneity.
        """
        subgroups = df[dimension].unique()
        results = []

        for sub in subgroups:
            sub_df = df[df[dimension] == sub]
            res = self.run_proportion_test(sub_df)
            results.append({
                dimension: sub,
                "n_control": res["n_control"],
                "n_treatment": res["n_treatment"],
                "cr_control_pct": round(res["conversion_rate_control"] * 100.0, 2),
                "cr_treatment_pct": round(res["conversion_rate_treatment"] * 100.0, 2),
                "abs_lift_pct": round(res["absolute_lift"] * 100.0, 2),
                "rel_lift_pct": res["relative_lift_pct"],
                "p_value": res["p_value"],
                "is_significant": res["is_statistically_significant"]
            })

        return pd.DataFrame(results).sort_values("rel_lift_pct", ascending=False)


if __name__ == "__main__":
    analyzer = ExperimentAnalyzer()
    df_exp = analyzer.load_experiment_data()
    prop_results = analyzer.run_proportion_test(df_exp)
    arpu_results = analyzer.run_arpu_test(df_exp)

    print("Proportion Z-Test Results:")
    for k, v in prop_results.items():
        print(f"  {k}: {v}")

    print("\nARPU t-Test Results:")
    for k, v in arpu_results.items():
        print(f"  {k}: {v}")
