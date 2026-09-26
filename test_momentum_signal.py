"""Tests for the 12-1 momentum signal used in asx200_momentum_12_1.ipynb.

Runs locally without BQuant (needs pandas and numpy):
    python backtests/test_momentum_signal.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from momentum_signal import momentum_12_1

HERE = Path(__file__).resolve().parent


def make_returns():
    rng = np.random.default_rng(0)
    dates = pd.bdate_range("2019-01-01", "2021-12-31")
    r = pd.DataFrame(rng.normal(0.0005, 0.02, (len(dates), 3)), index=dates, columns=["A", "B", "C"])
    r.loc[:"2020-03-15", "C"] = np.nan              # C lists in March 2020
    r.loc["2021-06-01":"2021-06-03", "B"] = np.nan  # B halted for three days
    return r


def lookback_window(index, t):
    end = index[index <= t - pd.DateOffset(months=1)][-1]
    start = index[index <= t - pd.DateOffset(months=12)][-1]
    return (index > start) & (index <= end)


def test_percent_and_decimal_inputs_agree():
    r = make_returns()
    pct = momentum_12_1(r * 100, returns_in_percent=True)
    dec = momentum_12_1(r, returns_in_percent=False)
    assert np.allclose(pct.fillna(-9), dec.fillna(-9))


def test_matches_hand_calculation():
    r = make_returns()
    t = pd.Timestamp("2021-08-31")
    window = lookback_window(r.index, t)
    expected = (1 + r.loc[window, "A"]).prod() - 1
    assert np.isclose(momentum_12_1(r, False).loc[t, "A"], expected)


def test_most_recent_month_excluded():
    r = make_returns()
    t = pd.Timestamp("2021-08-31")
    bumped = r.copy()
    bumped.loc["2021-08-01":"2021-08-31", "A"] += 0.05
    assert np.isclose(momentum_12_1(bumped, False).loc[t, "A"], momentum_12_1(r, False).loc[t, "A"])


def test_halted_days_are_zero_return():
    r = make_returns()
    t = pd.Timestamp("2021-08-31")
    window = lookback_window(r.index, t)
    expected = (1 + r.loc[window, "B"].fillna(0)).prod() - 1
    assert np.isclose(momentum_12_1(r, False).loc[t, "B"], expected)


def test_requires_full_12_month_history():
    sig = momentum_12_1(make_returns(), False)
    assert sig.loc[:"2019-12-31"].isna().all().all()
    assert sig.loc[:"2021-03-15", "C"].isna().all()
    assert sig.loc["2021-03-16":, "C"].notna().all()


def test_notebook_uses_same_function():
    notebook = json.loads((HERE / "asx200_momentum_12_1.ipynb").read_text())
    cells = ["".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code"]
    module_src = (HERE / "momentum_signal.py").read_text()
    function_src = module_src[module_src.index("def momentum_12_1"):].strip()
    assert any(function_src in cell for cell in cells), "notebook copy of momentum_12_1 has drifted"


if __name__ == "__main__":
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"{len(tests)} passed")
