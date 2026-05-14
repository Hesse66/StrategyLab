# Fold-3 Robustness Repair - run_11a1fb629ebb

## Objective

Repair the cost-calibrated XAUUSD GHL+DC parent's remaining robustness weakness without changing the economic engine. The frozen base was `run_049fc3825db7` / `ver_af9769fef878`, which used the IC Markets cost proxy `commission_pct=0.0035` and failed robustness as `needs_review`: walk-forward `3/4`, cost stress `2/3`.

The known weak period was fold 3: `2022-02-02 11:00 UTC` to `2024-03-18 11:00 UTC`.

## Mutation Tested

Single rule-family repair: extend the existing UTC time-risk entry filter.

| Field | Before | Repair Candidate |
|---|---|---|
| `time_risk_filter_enabled` | `true` | `true` |
| `time_risk_block_utc_hours` | `[1, 7, 12, 14, 21]` | `[1, 7, 8, 11, 12, 13, 14, 21]` |
| `time_risk_block_weekdays` | `[]` | `[]` |

This keeps the GHL+DC entry, Gann-state exit, ATR stop, sizing, slippage, and commission model unchanged.

## Saved Candidate

| Field | Value |
|---|---|
| Run | `run_11a1fb629ebb` |
| Version | `ver_af40d5cbc512` |
| Dataset | `ds_4e109af56413` |
| Verdict | `promotion_candidate` |
| Robustness label | `production_robustness_candidate` |

## Full-History Comparison

| Metric | Cost-Calibrated Base | Repair Candidate | Delta |
|---|---:|---:|---:|
| Net PnL | 100,854.49 | 90,271.88 | -10,582.61 |
| Profit Factor | 1.5358 | 1.5603 | +0.0245 |
| Max Drawdown | 5.60% | 5.52% | -0.08 |
| Trades | 876 | 779 | -97 |
| Daily Sharpe | 1.5779 | 1.5520 | -0.0259 |
| Daily Sortino | 1.7848 | 1.6908 | -0.0940 |
| Worst Daily Return | -1.36% | -1.01% | +0.35 |
| Calmar | 18.0133 | 16.3489 | -1.6644 |

The candidate gives up about `10.49%` of full-history net PnL and `97` trades. In exchange it improves PF, slightly lowers drawdown, materially improves worst daily return, and passes the full robustness gate.

## Walk-Forward Result

| Fold | Passed | Return | PF | Trades | DD | Daily Sharpe | Daily Sortino | Calmar |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | yes | 11.53% | 1.5138 | 172 | 4.09% | 1.4167 | 1.4769 | 2.8192 |
| 2 | yes | 8.34% | 1.2057 | 213 | 5.52% | 0.8693 | 0.7874 | 1.5112 |
| 3 | yes | 8.29% | 1.2699 | 184 | 4.55% | 0.9869 | 0.9149 | 1.8216 |
| 4 | yes | 45.41% | 2.0550 | 209 | 4.79% | 2.5384 | 3.4294 | 9.4892 |

The repair fixes the original weak fold and also keeps fold 2 above the minimum daily Sortino threshold. This matters because nearby alternatives fixed fold 3 while moving the failure into fold 2.

## Cost Stress Result

| Scenario | Passed | Commission | Slippage Ticks | Return | PF | DD | Daily Sortino | Calmar |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `commission_2x` | yes | 0.0070 | 10 | 80.21% | 1.5004 | 5.94% | 1.5286 | 13.4944 |
| `slippage_2x` | yes | 0.0035 | 20 | 76.90% | 1.4852 | 6.11% | 1.4770 | 12.5804 |
| `commission_2x_slippage_2x` | yes | 0.0070 | 20 | 67.55% | 1.4283 | 6.53% | 1.3172 | 10.3401 |

Unlike the base cost-calibrated run, the combined doubled-cost scenario no longer fails the robustness gate.

## Rejected Nearby Alternatives

Several nearby time-filter repairs improved fold 3 but did not pass the complete gate:

- Add `11,13`: fixed fold 3 but moved the daily Sortino failure to fold 2.
- Add `6,11,13`: stronger full-history balance, but still failed fold 2 daily Sortino.
- Add `4,11,13`: fixed fold 3 but failed fold 2 daily Sortino and reduced trade count more aggressively.
- Add weekday filters: repaired fold 3 only by cutting too much activity and damaging full-history evidence.

## Practical Decision

`run_11a1fb629ebb` / `ver_af40d5cbc512` is the best robustness-repaired StrategyLab parent currently found. It should replace `run_049fc3825db7` as the current research dossier candidate if the priority is robustness readiness rather than maximum full-history PnL.

It is still not live-production ready. The next gate is MT5 parity/backtest export using this exact rule contract and IC Markets cost assumptions, followed by paper-demo only if MT5 behavior matches the StrategyLab dossier.
