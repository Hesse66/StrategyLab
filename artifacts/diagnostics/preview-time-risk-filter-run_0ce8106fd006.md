# Unsaved Preview - UTC Time-Risk Filter on run_0ce8106fd006

Frozen parent: `run_0ce8106fd006`

Dataset: `ds_4e109af56413`

Implemented rule family: UTC entry-hour risk filter for `ghl_dc_breakout_v1`.

## First Active Candidate

```json
{
  "time_risk_filter_enabled": true,
  "time_risk_block_utc_hours": [1, 7, 21],
  "time_risk_block_weekdays": [],
  "breakeven_stop_enabled": false
}
```

| Metric | Frozen Parent | First Candidate | Delta |
|---|---:|---:|---:|
| Net PnL | 90923.34 | 106404.03 | +15480.69 |
| Return % | 90.92 | 106.40 | +15.48 |
| Profit Factor | 1.4079 | 1.5251 | +0.1172 |
| Max Drawdown % | 5.39 | 5.63 | +0.24 |
| Expected Payoff | 90.02 | 113.92 | +23.90 |
| Total Trades | 1010 | 934 | -76 |
| Daily Sharpe | 1.4130 | 1.6153 | +0.2023 |
| Daily Sortino | 1.6192 | 1.8868 | +0.2676 |
| Worst Daily Return % | -1.35 | -1.35 | 0.00 |
| Calmar | 16.8553 | 18.8847 | +2.0294 |
| Outperformance % | -172.61 | -157.13 | +15.48 |
| Calmar Delta | 6.7048 | 8.7343 | +2.0295 |

Diagnostics:

- Entry blocks: `98`
- Long blocks: `98`
- Short blocks: `0`
- Trades: `934`
- Gann-state exits: `677`, net PnL `233639.58`
- Stop exits: `256`, net PnL `-126928.92`

Interpretation: the first active candidate survived. It improves most portfolio and expectancy metrics while preserving a large trade sample. The only notable cost is a small max drawdown increase from `5.39%` to `5.63%`.

## Post-Survival Curated Optimization

Only the new time-risk hour set was varied.

| Blocked UTC Hours | Net PnL | PF | DD % | Payoff | Trades | Daily Sharpe | Daily Sortino | Calmar | Blocks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `[1,7,12,14,21]` | 113504.68 | 1.5977 | 5.17 | 129.57 | 876 | 1.7114 | 1.9770 | 21.9339 | 175 |
| `[1,7,14,21]` | 108790.49 | 1.5575 | 5.17 | 120.34 | 904 | 1.6563 | 1.9191 | 21.0229 | 140 |
| `[1,7,21]` | 106404.03 | 1.5251 | 5.63 | 113.92 | 934 | 1.6153 | 1.8868 | 18.8847 | 98 |
| `[1,21]` | 105451.56 | 1.5075 | 5.39 | 110.54 | 954 | 1.5998 | 1.8658 | 19.5485 | 72 |
| `[]` | 90923.34 | 1.4079 | 5.39 | 90.02 | 1010 | 1.4130 | 1.6192 | 16.8553 | 0 |

## Result

The optimized time-risk candidate is:

```json
{
  "time_risk_filter_enabled": true,
  "time_risk_block_utc_hours": [1, 7, 12, 14, 21],
  "time_risk_block_weekdays": []
}
```

It improves net PnL by `22581.34`, PF by `0.1898`, max drawdown by `-0.22`, expected payoff by `39.55`, Daily Sharpe by `0.2984`, Daily Sortino by `0.3578`, and Calmar by `5.0786` versus the frozen parent.

Trade count falls from `1010` to `876`. This is a meaningful reduction but not a low-sample collapse. It should be accepted as a survived phase-3 mutation candidate, then validated with period decomposition and robustness gates before promotion.

## Routing

Route to save or promote only after operator review. Do not route to phase 4 until this candidate is saved as the next full-whitebox parent and re-diagnosed.
