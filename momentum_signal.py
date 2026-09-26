import numpy as np
import pandas as pd


def momentum_12_1(total_returns, returns_in_percent):
    """Compounded 12-1 momentum.

    For each date t: the total return compounded from t - 12 months to t - 1 month,
    i.e. the last 12 months excluding the most recent month.

    total_returns: daily total returns, DATE index x security ID columns.
    returns_in_percent: True if 1.5 means 1.5% (divide by 100), False if 0.015 means 1.5%.
    """
    daily = total_returns / 100.0 if returns_in_percent else total_returns
    dates = daily.index

    # Cumulative growth of 1 unit. A missing day inside a security's history
    # (e.g. a trading halt) is treated as a zero return.
    growth = (1.0 + daily.fillna(0.0)).cumprod()

    def growth_as_of(offset):
        # Growth on the last available date on or before (t - offset).
        lagged = growth.reindex(dates - offset, method="ffill")
        lagged.index = dates
        return lagged

    signal = growth_as_of(pd.DateOffset(months=1)) / growth_as_of(pd.DateOffset(months=12)) - 1.0

    # Only score a security once it has returns covering the full 12-month lookback.
    first_return = daily.apply(pd.Series.first_valid_index)
    lookback_start = pd.Series(dates - pd.DateOffset(months=12), index=dates)
    has_history = pd.DataFrame(
        {sec: lookback_start >= first for sec, first in first_return.items()}, index=dates
    )
    return signal.where(has_history)
