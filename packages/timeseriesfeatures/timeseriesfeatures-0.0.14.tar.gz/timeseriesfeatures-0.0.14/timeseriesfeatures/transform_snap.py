"""A snap transform."""

import pandas as pd


def snap_transform(series: pd.Series) -> pd.Series:
    """Transforms a series by snap."""
    return series.pct_change().pct_change().pct_change().pct_change()
