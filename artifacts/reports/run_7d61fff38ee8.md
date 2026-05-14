# Mutation Lab Run run_7d61fff38ee8

- Family: `btc_intraday`
- Version: `BTC Intraday Parent | tuned atr_len=103, fast_len=26, max_no_cross=1, slow_len=104... | tuned atr_len=70, fast_len=30, stop_mult=5.1 | tuned breakeven_lock_r=1, breakeven_stop_enabled=True, breakeven_trigger_mfe_r=0.25, short_quality_gate_enabled=True... | tuned hybrid_time_decay_triage_checkpoints=[30], hybrid_time_decay_triage_enabled=True, hybrid_time_decay_triage_max_mfe_r=0.15, hybrid_time_decay_triage_max_unrealized_r=-0.45 | tuned notional_pct=0.5, risk_pct=0.01, sizing_mode=fixed_risk_pct`
- Stage: `white_box`
- Verdict: `promotion_candidate`
- Dataset: `ds_d14d74e36d0d`

## Frozen Strategy Contract

This run freezes `ma_cross_atr_stop_v1` on `BTCUSDT` at `Binance Spot` / `15m`. The live parameters are `{"allow_long": true, "allow_short": true, "atr_len": 70, "atr_timeframe": "15m", "breakeven_lock_r": 1.0, "breakeven_stop_enabled": true, "breakeven_trigger_mfe_r": 0.25, "commission_pct": 0.04, "entry_mode": "crossover_only", "execution_model": "next_bar_open", "fast_len": 30, "hybrid_reverse_exit_min_mfe_r": 0.1, "hybrid_reverse_exit_triage_enabled": true, "hybrid_time_decay_triage_checkpoints": [30], "hybrid_time_decay_triage_enabled": true, "hybrid_time_decay_triage_max_mfe_r": 0.15, "hybrid_time_decay_triage_max_unrealized_r": -0.45, "initial_capital": 100000.0, "ma_kind": "sma", "max_leverage": 1.0, "max_no_cross": 1, "noise_lookback": 25, "notional_pct": 0.5, "quantity": 1.0, "risk_pct": 0.01, "short_quality_gate_enabled": true, "short_quality_gate_len_bars": 24960, "short_quality_gate_rule": "block_below_sma", "sizing_mode": "fixed_risk_pct", "slippage_ticks": 2, "slow_len": 104, "stop_mult": 5.1, "tick_size": 0.01, "time_decay_bars": 40, "time_decay_exit_enabled": true, "time_decay_min_mfe_r": 0.35, "time_risk_block_utc_hours": [13, 15, 21], "time_risk_block_weekdays": [6], "time_risk_filter_enabled": true}`.

## Metrics

- Net PnL: `5564778.97`
- Return %: `5564.78`
- Profit Factor: `4.2541`
- Max Drawdown %: `3.96`
- Expected Payoff: `7274.22`
- Total Trades: `765`
- Win Rate %: `75.42`
- Avg Win / Avg Loss Ratio: `1.3861`
- Approx Breakeven Win Rate: `41.91`
- Execution Model: `next_bar_open`
- Equity Marking: `mark_to_market`
- Trade-Level Sharpe: `20.9451`
- Trade-Level Sortino: `20.5427`
- Daily Portfolio Sharpe: `5.8325`
- Daily Portfolio Sortino: `4.0819`
- Daily Volatility %: `8.03`
- Worst Daily Return %: `-2.06`
- Positive Day %: `17.67`
- Calmar: `1404.9111`
- Sizing Mode: `fixed_risk_pct`
- Avg Entry Exposure %: `56.75`
- Max Entry Exposure %: `100.0`
- Avg Initial Risk %: `0.9714`
- Max Initial Risk %: `1.0`
- Buy & Hold Net PnL: `1637469.62`
- Buy & Hold Asset Return %: `1637.47`
- Buy & Hold Max Drawdown %: `83.97`
- Buy & Hold Calmar: `19.5009`
- Buy & Hold Start/End: `4316.75` -> `75002.22`
- Outperformance %: `3927.31`
- Calmar Delta: `1385.4103`

## Performance Interpretation

This report separates the headline result from the mechanics that created it. A low win rate is not automatically a defect when the average win/loss ratio is high; the important question is whether the strategy preserves enough right-tail winners while reducing avoidable churn, weak sides, poor regimes, or expensive stop exits. Use the diagnostics below to decide the next full-whitebox mutation instead of guessing from the headline metrics alone.

## Production Gate

- Core failures: `[]`
- Portfolio / benchmark failures: `[]`
- Production sizing modes: `['fixed_notional_pct', 'fixed_risk_pct']`
- Benchmark policy: `outperform_return_or_calmar`
- Execution model: `next_bar_open`

The platform-level rule is deliberately generic: first prove the strategy has enough activity, positive expectancy, bounded mark-to-market drawdown, acceptable daily portfolio Sharpe/Sortino/Calmar, bounded daily loss, and bounded per-trade risk; then judge it under a portfolio sizing model against buy-and-hold. Trade-level Sharpe/Sortino are diagnostic only and may overstate deployable portfolio quality. A strategy does not need to beat buy-and-hold on raw return if it delivers better drawdown-adjusted efficiency, but if it loses on both raw return and Calmar it is not production-comparable yet.

## Capital Model Warning

- fixed_risk_pct sizes each trade by stop distance; `0.01` means `1.0%` of current equity is the intended loss budget before leverage caps.

## Parent Comparison

- Profit Factor Delta: `-0.6413`
- Net PnL Delta: `5182673.96`
- Drawdown % Delta: `2.34`
- Trade Count Delta: `1`

## Single Mutation

- Summary: `notional_pct=0.5, risk_pct=0.01, sizing_mode=fixed_risk_pct`
- Rationale: 

## Diagnostics

- Entries: `765`
- Long signals: `656`
- Short signals: `371`
- Short quality gate blocks: `294`
- Breakeven stop moves: `566`
- Time risk filter blocks: `244`
- Stop exits: `630`
- Reverse exits: `11`
- Time-decay exits: `98`
- Time exits: `0`
- Pending entry orders: `754`
- Pending order fills: `0`
- Dropped pending orders at end of data: `0`

## Side Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| long | 490 | 3526960.95 | 4.2211 | 75.51% | 12491.66 | -9124.6 | 16.26 |
| short | 275 | 2037818.02 | 4.3129 | 75.27% | 12816.1 | -9045.81 | 14.21 |

## Exit-Reason Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| hybrid_time_decay_triage | 26 | -281287.44 | 0.0 | 0.0% | 0.0 | -10818.75 | 30.0 |
| reverse | 11 | 55201.77 | 2.8335 | 9.09% | 85308.65 | -3010.69 | 26.55 |
| stop | 630 | 6124077.26 | 6.8253 | 89.05% | 12790.3 | -15235.97 | 10.93 |
| time_decay | 98 | -333212.62 | 0.0408 | 15.31% | 945.24 | -4185.44 | 40.0 |

## Period Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 13 | 8557.75 | 6.1353 | 76.92% | 1022.42 | -555.48 | 19.92 |
| 2018 | 45 | 17337.28 | 2.2703 | 62.22% | 1106.62 | -802.82 | 17.49 |
| 2019 | 88 | 90090.49 | 6.9775 | 75.0% | 1593.37 | -685.08 | 15.01 |
| 2020 | 91 | 114152.75 | 3.5681 | 73.63% | 2367.22 | -1852.13 | 17.67 |
| 2021 | 112 | 299117.06 | 4.5783 | 76.79% | 4450.11 | -3215.08 | 13.88 |
| 2022 | 62 | 247005.78 | 4.6705 | 74.19% | 6832.63 | -4205.94 | 14.42 |
| 2023 | 104 | 620116.05 | 4.8568 | 77.88% | 9640.78 | -6990.74 | 16.33 |
| 2024 | 103 | 1353807.48 | 6.0558 | 82.52% | 19077.4 | -14876.2 | 14.02 |
| 2025 | 124 | 2342127.05 | 3.9096 | 74.19% | 34207.67 | -25155.59 | 15.49 |
| 2026 | 23 | 472467.28 | 2.8838 | 69.57% | 45204.55 | -35829.37 | 16.87 |

## Trade Duration

- 25th percentile bars held: `4.0`
- Median bars held: `10.0`
- 75th percentile bars held: `27.0`
- 90th percentile bars held: `40.0`
- 95th percentile bars held: `40.0`

## Excursion Diagnostics

- Average MFE/R: `0.3701`
- Average MAE/R: `-0.3724`

MFE/R and MAE/R are decision-time diagnostic fields for full-whitebox research. They help identify whether losses had enough favorable movement for breakeven or trailing-stop logic, and whether winners required wide adverse movement that a tighter stop would have destroyed.

## Full-Whitebox Diagnostic Queue

Before testing a new rule mutation, inspect whether the weakness is side-specific, exit-specific, period-specific, duration-specific, or excursion-specific. Good next mutations should attack one localized defect while preserving the parent contract and the right-tail behavior that funds the strategy.