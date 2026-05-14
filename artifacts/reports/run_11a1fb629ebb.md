# Mutation Lab Run run_11a1fb629ebb

- Family: `xauusd_ghl_dc`
- Version: `XAUUSD GHL+DC Parent | robustness repair UTC block 1,7,8,11,12,13,14,21`
- Stage: `white_box`
- Verdict: `promotion_candidate`
- Dataset: `ds_4e109af56413`

## Frozen Strategy Contract

This run freezes `ghl_dc_breakout_v1` on `XAUUSD` at `IC Markets MT5` / `30m`. The live parameters are `{"allow_long": true, "allow_short": false, "atr_len": 34, "breakeven_lock_r": 0.0, "breakeven_stop_enabled": false, "breakeven_trigger_mfe_r": 0.75, "commission_pct": 0.0035, "donchian_length": 55, "gann_high_period": 21, "gann_low_period": 13, "initial_capital": 100000.0, "max_breakout_bars": 12, "max_leverage": 1.0, "notional_pct": 0.25, "quantity": 1.0, "risk_pct": 0.01, "sizing_mode": "fixed_risk_pct", "slippage_ticks": 10, "stop_mode": "atr", "stop_mult": 2.5, "tick_size": 0.01, "time_risk_block_utc_hours": [1, 7, 8, 11, 12, 13, 14, 21], "time_risk_block_weekdays": [], "time_risk_filter_enabled": true}`.

## Metrics

- Net PnL: `90271.88`
- Return %: `90.27`
- Profit Factor: `1.5603`
- Max Drawdown %: `5.52`
- Expected Payoff: `115.88`
- Total Trades: `779`
- Win Rate %: `38.51`
- Avg Win / Avg Loss Ratio: `2.4912`
- Approx Breakeven Win Rate: `28.64`
- Trade-Level Sharpe: `3.7675`
- Trade-Level Sortino: `7.7405`
- Daily Portfolio Sharpe: `1.552`
- Daily Portfolio Sortino: `1.6908`
- Daily Volatility %: `7.07`
- Worst Daily Return %: `-1.01`
- Positive Day %: `12.05`
- Calmar: `16.3489`
- Sizing Mode: `fixed_risk_pct`
- Avg Entry Exposure %: `99.64`
- Max Entry Exposure %: `100.0`
- Avg Initial Risk %: `0.4085`
- Max Initial Risk %: `1.0`
- Buy & Hold Net PnL: `263532.97`
- Buy & Hold Asset Return %: `263.53`
- Buy & Hold Max Drawdown %: `25.96`
- Buy & Hold Calmar: `10.1504`
- Buy & Hold Start/End: `1275.81` -> `4637.99`
- Outperformance %: `-173.26`
- Calmar Delta: `6.1985`

## Performance Interpretation

This report separates the headline result from the mechanics that created it. A low win rate is not automatically a defect when the average win/loss ratio is high; the important question is whether the strategy preserves enough right-tail winners while reducing avoidable churn, weak sides, poor regimes, or expensive stop exits. Use the diagnostics below to decide the next full-whitebox mutation instead of guessing from the headline metrics alone.

## Production Gate

- Core failures: `[]`
- Portfolio / benchmark failures: `[]`
- Production sizing modes: `['fixed_notional_pct', 'fixed_risk_pct']`
- Benchmark policy: `outperform_return_or_calmar`

The platform-level rule is deliberately generic: first prove the strategy has enough activity, positive expectancy, bounded drawdown, acceptable daily portfolio Sharpe/Sortino/Calmar, bounded daily loss, and bounded per-trade risk; then judge it under a portfolio sizing model against buy-and-hold. Trade-level Sharpe/Sortino are diagnostic only and may overstate deployable portfolio quality. A strategy does not need to beat buy-and-hold on raw return if it delivers better drawdown-adjusted efficiency, but if it loses on both raw return and Calmar it is not production-comparable yet.

## Capital Model Warning

- fixed_risk_pct sizes each trade by stop distance; `0.01` means `1.0%` of current equity is the intended loss budget before leverage caps.

## Parent Comparison

- Profit Factor Delta: `0.0245`
- Net PnL Delta: `-10582.61`
- Drawdown % Delta: `-0.08`
- Trade Count Delta: `-97`

## Single Mutation

- Summary: `time_risk_block_utc_hours=[1, 7, 8, 11, 12, 13, 14, 21], time_risk_block_weekdays=[], time_risk_filter_enabled=True`
- Rationale: 

## Diagnostics

- Entries: `779`
- Long signals: `1118`
- Short signals: `0`
- Short quality gate blocks: `0`
- Breakeven stop moves: `0`
- Time risk filter blocks: `311`
- Stop exits: `198`
- Reverse exits: `0`
- Time-decay exits: `0`
- Time exits: `1`

## Side Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| long | 779 | 90271.88 | 1.5603 | 38.51% | 837.99 | -336.38 | 16.46 |
| short | 0 | 0.0 | 0.0 | 0.0% | 0.0 | 0.0 | 0.0 |

## Exit-Reason Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| gann_state_exit | 580 | 187334.27 | 3.9242 | 51.72% | 837.99 | -228.8 | 20.62 |
| stop | 198 | -96766.37 | 0.0 | 0.0% | 0.0 | -488.72 | 4.35 |
| time_exit | 1 | -296.02 | 0.0 | 0.0% | 0.0 | -296.02 | 4.0 |

## Period Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 17 | 2313.55 | 2.5396 | 52.94% | 424.03 | -187.84 | 20.06 |
| 2018 | 74 | -2705.06 | 0.7398 | 31.08% | 334.4 | -203.85 | 14.76 |
| 2019 | 88 | 13646.83 | 2.2347 | 43.18% | 650.0 | -221.06 | 18.25 |
| 2020 | 104 | 6254.1 | 1.2697 | 35.58% | 795.85 | -346.16 | 16.3 |
| 2021 | 96 | 217.49 | 1.0105 | 35.42% | 617.23 | -334.97 | 15.36 |
| 2022 | 80 | 3974.79 | 1.2645 | 41.25% | 575.78 | -319.7 | 15.69 |
| 2023 | 91 | 8458.36 | 1.4783 | 38.46% | 746.9 | -315.77 | 14.86 |
| 2024 | 103 | -2300.61 | 0.9085 | 34.95% | 634.23 | -375.12 | 14.34 |
| 2025 | 96 | 35282.38 | 2.6127 | 43.75% | 1360.94 | -405.13 | 20.05 |
| 2026 | 30 | 25130.05 | 2.7338 | 43.33% | 3048.0 | -852.58 | 20.27 |

## Trade Duration

- 25th percentile bars held: `6.0`
- Median bars held: `14.0`
- 75th percentile bars held: `22.0`
- 90th percentile bars held: `34.0`
- 95th percentile bars held: `43.0`

## Excursion Diagnostics

- Average MFE/R: `1.3683`
- Average MAE/R: `-0.6957`

MFE/R and MAE/R are decision-time diagnostic fields for full-whitebox research. They help identify whether losses had enough favorable movement for breakeven or trailing-stop logic, and whether winners required wide adverse movement that a tighter stop would have destroyed.

## Full-Whitebox Diagnostic Queue

Before testing a new rule mutation, inspect whether the weakness is side-specific, exit-specific, period-specific, duration-specific, or excursion-specific. Good next mutations should attack one localized defect while preserving the parent contract and the right-tail behavior that funds the strategy.