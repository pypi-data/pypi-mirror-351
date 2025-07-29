"""An acceleration transform."""

import pandas as pd


def acceleration_transform(series: pd.Series) -> pd.Series:
    """Transforms a series by acceleration."""
    return series.pct_change().pct_change()
