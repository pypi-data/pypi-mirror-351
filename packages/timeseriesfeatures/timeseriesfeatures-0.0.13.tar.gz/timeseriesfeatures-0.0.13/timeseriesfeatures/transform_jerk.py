"""A jerk transform."""

import pandas as pd


def jerk_transform(series: pd.Series) -> pd.Series:
    """Transforms a series by jerk."""
    return series.pct_change().pct_change().pct_change()
