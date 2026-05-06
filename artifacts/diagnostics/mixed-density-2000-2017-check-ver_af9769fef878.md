# Mixed-Density 2000-2017 Check - ver_af9769fef878

## Purpose

This is a diagnostic-only check requested to see how the current XAUUSD GHL+DC cost-calibrated parent behaves on the older MT5 export segment before the existing full M30 dataset begins.

The source file is `artifacts/data/XAUUSD_M30_200001030000_202605011600.csv`. Although the file is labeled M30, the segment from 2000 through 2015 is mostly daily data, 2016 is mixed-density intraday data, and early 2017 is still not as clean as the later M30 history. Therefore this run must not be treated as a production-grade M30 backtest.

## Dataset Created

| Field | Value |
|---|---|
| Dataset id | `ds_3d6a4f4a0f5c` |
| Name | `icmarkets-xauusd-30m-diagnostic-20000103-20171102-mixed-density` |
| Source range | `2000-01-03 00:00 UTC` to `2017-11-02 06:30 UTC` |
| Rows | `18,552` |
| Output path | `artifacts/data/ds_3d6a4f4a0f5c.csv` |

## Strategy Tested

| Field | Value |
|---|---|
| Version | `ver_af9769fef878` |
| Engine | `ghl_dc_breakout_v1` |
| Asset | `XAUUSD` |
| Timeframe contract | `30m` |
| Commission model | `commission_pct=0.0035` |
| Slippage | `10` ticks |
| Active whitebox mutation | UTC time-risk block `[1, 7, 12, 14, 21]` |

## Result

| Metric | Value |
|---|---:|
| Verdict | `graveyard` |
| Net PnL | 22,923.85 |
| Return | 22.92% |
| Profit Factor | 1.5907 |
| Max Drawdown | 3.67% |
| Total Trades | 140 |
| Daily Sharpe | 0.5065 |
| Daily Sortino | 0.1636 |
| Worst Daily Return | -1.01% |
| Calmar | 6.2421 |
| Buy & Hold Return | 346.98% |
| Outperformance | -324.05% |

Exit reasons:

| Reason | Trades |
|---|---:|
| `gann_state_exit` | 109 |
| `stop` | 30 |
| `time_exit` | 1 |

## Interpretation

The parent does not collapse on the old segment: PF is still positive at `1.5907`, drawdown is controlled, and net PnL is positive. However, the evidence is not suitable for promotion because the dataset is mixed-density and the result underperforms buy-and-hold by a wide margin. Daily Sortino is also far below the current production threshold.

The low trade count is expected because most of 2000-2015 is not true M30 data. Indicators and entry logic that were designed for 30-minute bars are being fed daily or mixed-density bars, so the result is only a rough historical stress read.

## Practical Conclusion

Do not merge this segment into the main M30 research dataset. Use it only as a diagnostic stress note: the strategy remains profitable but not superior on the mixed-density 2000-2017 segment.

For real Mutation Lab decisions, keep `run_049fc3825db7` on `ds_4e109af56413` as the valid cost-calibrated parent/dataset pair unless a clean M30 export before 2017 becomes available.
