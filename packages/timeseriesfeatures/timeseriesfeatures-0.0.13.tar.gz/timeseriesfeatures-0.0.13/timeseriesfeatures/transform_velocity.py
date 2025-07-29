"""A velocity transform."""

import pandas as pd


def velocity_transform(series: pd.Series) -> pd.Series:
    """Transforms a series by velocity."""
    return series.pct_change()
