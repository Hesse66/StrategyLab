# Robustness Cost Model Check - run_049fc3825db7

## Purpose

This check replaces the prior XAUUSD zero-commission assumption with an IC Markets Metals Raw Spread proxy before re-running robustness. The previous `commission_pct=0.0` made the `commission_2x` stress scenario a no-op, so cost stress was incomplete even though the slippage stress was still informative.

The cost proxy used here is `commission_pct=0.0035`, modeled as a per-side notional commission. This approximates IC Markets Metals Raw Spread pricing of `7 USD` round-turn per standard lot, or `3.50 USD` per side. In the current StrategyLab engine, commission is applied as a percent of entry and exit notional, so `0.0035%` is the closest available representation.

## Saved Cost-Calibrated Version

| Field | Value |
|---|---|
| Source parent | `run_2579435b99a9` / `ver_9a0ca0f8616c` |
| Cost-calibrated run | `run_049fc3825db7` |
| Cost-calibrated version | `ver_af9769fef878` |
| Dataset | `ds_4e109af56413` |
| Asset / venue / timeframe | `XAUUSD` / `IC Markets MT5` / `30m` |
| Engine | `ghl_dc_breakout_v1` |
| Commission model | `commission_pct=0.0035` |
| Slippage | `slippage_ticks=10`, `tick_size=0.01` |
| Verdict | `promotion_candidate` |

## Full-History Result With Cost Model

| Metric | Zero-Commission Parent | Cost-Calibrated |
|---|---:|---:|
| Net PnL | 113,504.68 | 100,854.49 |
| Profit Factor | 1.5977 | 1.5358 |
| Max Drawdown | 5.17% | 5.60% |
| Trades | 876 | 876 |
| Daily Sharpe | 1.7114 | 1.5779 |
| Daily Sortino | 1.9770 | 1.7848 |
| Worst Daily Return | -1.35% | -1.36% |
| Calmar | 21.9339 | 18.0133 |

The strategy remains a promotion candidate after realistic commission is applied, but its cushion is lower. Net PnL falls by `12,650.19`, PF falls by `0.0619`, and max drawdown increases by `0.43` percentage points.

## Robustness Result

Summary: `needs_review`.

| Gate | Passed | Total |
|---|---:|---:|
| Walk-forward | 3 | 4 |
| Cost stress | 2 | 3 |

## Walk-Forward Detail

| Fold | Passed | Failures | Return | PF | Trades | DD | Daily Sharpe | Daily Sortino | Calmar |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | yes | none | 11.07% | 1.4233 | 196 | 4.93% | 1.3198 | 1.4284 | 2.2459 |
| 2 | yes | none | 13.38% | 1.2848 | 238 | 5.60% | 1.1686 | 1.1795 | 2.3906 |
| 3 | no | `low_profit_factor`, `low_daily_sortino` | 5.17% | 1.1449 | 208 | 5.31% | 0.6267 | 0.5648 | 0.9740 |
| 4 | yes | none | 51.65% | 2.0533 | 233 | 5.29% | 2.6820 | 3.7016 | 9.7546 |

The same weak chronological fold remains the limiting factor: `2022-02-02 11:00 UTC` to `2024-03-18 11:00 UTC`. With realistic commission, that fold now fails both PF and daily Sortino.

## Cost Stress Detail

| Scenario | Commission | Slippage Ticks | Passed | Failures | Return | PF | DD | Daily Sortino | Calmar |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|
| `commission_2x` | 0.0070 | 10 | yes | none | 88.95% | 1.4768 | 6.02% | 1.6073 | 14.7735 |
| `slippage_2x` | 0.0035 | 20 | yes | none | 85.00% | 1.4618 | 6.26% | 1.5502 | 13.5807 |
| `commission_2x_slippage_2x` | 0.0070 | 20 | no | `weak_vs_buy_hold_benchmark` | 74.04% | 1.4058 | 7.68% | 1.3777 | 9.6408 |

The combined execution-cost stress does not fail the core strategy gates. It fails because the benchmark policy flags weak comparison versus buy-and-hold under the harsher combined-cost scenario. That is still relevant for routing, but it is not the same as the strategy losing money or collapsing under costs.

## Root Cause

The original robustness result overstated cost-stress confidence because XAUUSD was stored with `commission_pct=0.0`. In StrategyLab, the stress scenarios multiply the existing commission value. Multiplying zero by two remains zero, so `commission_2x` and the commission side of `commission_2x_slippage_2x` were not measuring commission pressure.

The engine did not have a calculation bug. The issue was a missing broker-cost assumption in the XAUUSD parent/run contract.

## Practical Conclusion

`run_049fc3825db7` / `ver_af9769fef878` is now the correct cost-calibrated research parent for XAUUSD GHL+DC. It remains viable, but it is not production-ready. Its routing stays `needs_review` because walk-forward is `3/4` and cost stress is `2/3`.

The next practical step is not another hybrid mutation. The efficient next step is robustness repair around the known weak 2022-2024 fold or a stricter dossier decision: either accept this as a research-only candidate pending paper evidence later, or route back to whitebox robustness repair with the cost-calibrated parent as the frozen base.
