# ASX 200 12-1 Momentum Backtest

A classic 12-1 price momentum backtest on the S&P/ASX 200, built with Bloomberg BQuant's
Equity Signal Lab (BQESL).

## Strategy

| Setting | Value |
| --- | --- |
| Universe | S&P/ASX 200 (`AS51 Index`) members |
| Benchmark | ASX 200 index weights |
| Signal | Compounded AUD total return (gross dividends) from t−12 months to t−1 month |
| Transformations | Winsorize (IQR, ±1.5) → z-score → beta and BICS Level 1 sector neutralization |
| Portfolios | Long-only top quintile, and long-short top/bottom quintile, equal weight |
| Rebalance | Month end, 1 business day implementation lag |
| Period | 2006-08-31 to 2026-08-31 |
| Costs | 5 bps linear |

## Files

- `asx200_momentum_12_1.ipynb`: the backtest. Builds a DataPack, defines the signal, runs both portfolios, and plots the analytics.
- `momentum_signal.py`: the 12-1 momentum function (the same code as in the notebook).
- `test_momentum_signal.py`: tests for the signal. They run without BQuant.

## Running

The notebook runs inside BQuant Enterprise and needs:

- the Equity Signal Lab add-on
- historical BICS sector names enabled on your account (request via `HELP HELP`)
- point-in-time index membership for `AS51 Index`, to avoid survivorship bias

The first DataPack fetch covers 20 years of data and takes a while. To reuse it on later runs, set `CREATE_DATA_PACK = False`.

To test the signal locally:

```
pip install -r requirements.txt
python test_momentum_signal.py
```

Not affiliated with Bloomberg. For research and testing only.
