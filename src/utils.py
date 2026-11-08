"""
Analytical Utility Functions
============================
Helper functions for formatting financial metrics, date manipulation,
and analytical aggregations across the platform.
"""

from typing import Union, Optional
import numpy as np
import pandas as pd


def format_currency(val: Union[int, float, None], decimals: int = 2) -> str:
    """Format numeric values as USD currency ($X,XXX.XX)."""
    if val is None or np.isnan(val):
        return "$0.00"
    if val >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    if val >= 1_000:
        return f"${val:,.{decimals}f}"
    return f"${val:.{decimals}f}"


def format_percentage(val: Union[int, float, None], decimals: int = 1) -> str:
    """Format numeric float or ratio as percentage (XX.X%)."""
    if val is None or np.isnan(val):
        return "0.0%"
    # If passed as 0.158 -> format as 15.8%
    if abs(val) <= 1.0 and val != 0:
        val = val * 100.0
    return f"{val:.{decimals}f}%"


def calculate_growth_rate(current: float, prior: float) -> Optional[float]:
    """Calculate percentage growth rate between two periods."""
    if prior is None or prior == 0 or np.isnan(prior):
        return None
    return ((current - prior) / prior) * 100.0


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero or null."""
    if denominator is None or denominator == 0 or np.isnan(denominator):
        return default
    return float(numerator / denominator)
