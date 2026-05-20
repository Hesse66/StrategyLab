# Mutation Lab Run run_dbb3abb43b8d

- Family: `btc_intraday`
- Version: `BTC Intraday Parent | tuned atr_len=103, fast_len=26, max_no_cross=1, slow_len=104... | tuned atr_len=70, fast_len=30, stop_mult=5.1 | tuned breakeven_lock_r=1, breakeven_stop_enabled=True, breakeven_trigger_mfe_r=0.25, short_quality_gate_enabled=True... | tuned hybrid_time_decay_triage_checkpoints=[30], hybrid_time_decay_triage_enabled=True, hybrid_time_decay_triage_max_mfe_r=0.15, hybrid_time_decay_triage_max_unrealized_r=-0.45 | tuned notional_pct=0.5, risk_pct=0.01, sizing_mode=fixed_risk_pct`
- Stage: `white_box`
- Verdict: `graveyard`
- Dataset: `ds_d14d74e36d0d`

## Frozen Strategy Contract

This run freezes `ma_cross_atr_stop_v1` on `BTCUSDT` at `Binance Spot` / `15m`. The live parameters are `{"allow_long": true, "allow_short": true, "atr_len": 70, "atr_timeframe": "15m", "breakeven_lock_r": 1.0, "breakeven_stop_enabled": true, "breakeven_trigger_mfe_r": 0.25, "commission_pct": 0.04, "contract_size": 100.0, "entry_exposure_gate_enabled": false, "entry_exposure_gate_max_pct": 75.0, "entry_mode": "crossover_only", "execution_model": "mt5_bar_proxy", "fast_len": 30, "hybrid_reverse_exit_min_mfe_r": 0.1, "hybrid_reverse_exit_triage_enabled": true, "hybrid_time_decay_triage_checkpoints": [30], "hybrid_time_decay_triage_enabled": true, "hybrid_time_decay_triage_max_mfe_r": 0.15, "hybrid_time_decay_triage_max_unrealized_r": -0.45, "initial_capital": 100000.0, "lot_step": 0.01, "ma_kind": "sma", "max_leverage": 1.0, "max_lot": 100.0, "max_no_cross": 1, "min_lot": 0.01, "noise_lookback": 25, "notional_pct": 0.5, "quantity": 1.0, "reverse_confirm_allow_if_unrealized_r_lte": -0.35, "reverse_confirm_max_bars": 2, "reverse_confirm_min_mfe_r": 0.2, "reverse_confirm_require_no_breakeven_move": false, "reverse_confirmation_enabled": false, "risk_pct": 0.01, "short_quality_gate_enabled": true, "short_quality_gate_len_bars": 24960, "short_quality_gate_rule": "block_below_sma", "sizing_mode": "fixed_risk_pct", "skip_below_min_lot": true, "slippage_ticks": 2, "slow_len": 104, "stop_mult": 5.1, "tick_size": 0.01, "time_decay_bars": 40, "time_decay_confirm_max_mfe_r": 0.35, "time_decay_confirm_max_unrealized_r": 0.0, "time_decay_confirm_require_no_breakeven_move": false, "time_decay_exit_enabled": true, "time_decay_min_mfe_r": 0.35, "time_decay_triage_confirmation_enabled": false, "time_risk_block_utc_hours": [13, 15, 21], "time_risk_block_weekdays": [6], "time_risk_filter_enabled": true}`.

## Metrics

- Net PnL: `388811.91`
- Return %: `388.81`
- Profit Factor: `1.5116`
- Max Drawdown %: `47.38`
- Expected Payoff: `529.72`
- Total Trades: `734`
- Win Rate %: `46.05`
- Avg Win / Avg Loss Ratio: `1.771`
- Approx Breakeven Win Rate: `36.09`
- Execution Model: `mt5_bar_proxy`
- Equity Marking: `mark_to_market`
- Trade-Level Sharpe: `2.7774`
- Trade-Level Sortino: `8.379`
- Daily Portfolio Sharpe: `1.0067`
- Daily Portfolio Sortino: `0.7726`
- Daily Volatility %: `20.14`
- Worst Daily Return %: `-11.62`
- Positive Day %: `22.08`
- Calmar: `8.2059`
- Sizing Mode: `fixed_risk_pct`
- Avg Entry Exposure %: `57.75`
- Max Entry Exposure %: `100.0`
- Avg Initial Risk %: `0.9695`
- Max Initial Risk %: `1.0`
- Buy & Hold Net PnL: `1637469.62`
- Buy & Hold Asset Return %: `1637.47`
- Buy & Hold Max Drawdown %: `83.97`
- Buy & Hold Calmar: `19.5009`
- Buy & Hold Start/End: `4316.75` -> `75002.22`
- Outperformance %: `-1248.66`
- Calmar Delta: `-11.2949`

## Performance Interpretation

This report separates the headline result from the mechanics that created it. A low win rate is not automatically a defect when the average win/loss ratio is high; the important question is whether the strategy preserves enough right-tail winners while reducing avoidable churn, weak sides, poor regimes, or expensive stop exits. Use the diagnostics below to decide the next full-whitebox mutation instead of guessing from the headline metrics alone.

## Production Gate

- Core failures: `['excess_drawdown', 'low_daily_sortino', 'excess_worst_daily_loss']`
- Portfolio / benchmark failures: `['weak_vs_buy_hold_benchmark']`
- Production sizing modes: `['fixed_notional_pct', 'fixed_risk_pct', 'mt5_fixed_risk_lot']`
- Benchmark policy: `outperform_return_or_calmar`
- Execution model: `mt5_bar_proxy`

The platform-level rule is deliberately generic: first prove the strategy has enough activity, positive expectancy, bounded mark-to-market drawdown, acceptable daily portfolio Sharpe/Sortino/Calmar, bounded daily loss, and bounded per-trade risk; then judge it under a portfolio sizing model against buy-and-hold. Trade-level Sharpe/Sortino are diagnostic only and may overstate deployable portfolio quality. A strategy does not need to beat buy-and-hold on raw return if it delivers better drawdown-adjusted efficiency, but if it loses on both raw return and Calmar it is not production-comparable yet.

## Capital Model Warning

- fixed_risk_pct sizes each trade by stop distance; `0.01` means `1.0%` of current equity is the intended loss budget before leverage caps.

## Parent Comparison

- Profit Factor Delta: `-3.3838`
- Net PnL Delta: `6706.9`
- Drawdown % Delta: `45.76`
- Trade Count Delta: `-30`

## Single Mutation

- Summary: `notional_pct=0.5, risk_pct=0.01, sizing_mode=fixed_risk_pct`
- Rationale: 

## Diagnostics

- Entries: `734`
- Long signals: `656`
- Short signals: `371`
- Short quality gate blocks: `294`
- Entry exposure gate blocks: `0`
- Entry exposure gate long blocks: `0`
- Entry exposure gate short blocks: `0`
- Breakeven stop moves: `300`
- MT5 stop modify rejects: `38487`
- Time risk filter blocks: `244`
- Stop exits: `466`
- Reverse exits: `102`
- Reverse confirmation candidates: `0`
- Reverse confirmation exits allowed: `0`
- Reverse confirmation adverse escapes allowed: `0`
- Reverse confirmation suppressed: `0`
- Reverse confirmation suppressed Net PnL: `0`
- Time-decay exits: `143`
- Time-decay confirmation candidates: `0`
- Time-decay confirmation exits allowed: `0`
- Time-decay confirmation suppressed: `0`
- Time-decay confirmation suppressed Net PnL: `0`
- Time exits: `0`
- Pending entry orders: `632`
- Pending order fills: `734`
- Dropped pending orders at end of data: `0`

## Side Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| long | 451 | 344782.94 | 1.7896 | 48.78% | 3552.01 | -1890.3 | 140.98 |
| short | 283 | 44028.97 | 1.1362 | 41.7% | 3113.47 | -1959.76 | 75.1 |

## Exit-Reason Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| hybrid_time_decay_triage | 23 | -47212.97 | 0.0 | 0.0% | 0.0 | -2052.74 | 30.0 |
| reverse | 102 | 350591.78 | 6.2897 | 37.25% | 10970.25 | -1035.59 | 379.94 |
| stop | 466 | 177332.52 | 1.3231 | 58.37% | 2669.89 | -2829.27 | 85.13 |
| time_decay | 143 | -91899.42 | 0.0589 | 19.58% | 205.39 | -849.13 | 40.0 |

## Period Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 5 | -342.57 | 0.8507 | 40.0% | 976.24 | -765.01 | 141.0 |
| 2018 | 31 | 30974.01 | 2.6274 | 41.94% | 3846.65 | -1057.36 | 702.94 |
| 2019 | 88 | 54214.53 | 2.0535 | 40.91% | 2935.47 | -989.66 | 85.91 |
| 2020 | 95 | 31296.21 | 1.484 | 46.32% | 2180.92 | -1267.93 | 81.32 |
| 2021 | 111 | 40788.78 | 1.4214 | 46.85% | 2645.7 | -1640.47 | 76.34 |
| 2022 | 53 | -1249.25 | 0.9822 | 39.62% | 3278.13 | -2190.31 | 167.81 |
| 2023 | 108 | 87396.03 | 1.7427 | 44.44% | 4272.41 | -1961.32 | 93.5 |
| 2024 | 103 | 14924.37 | 1.1055 | 50.49% | 3007.21 | -2773.54 | 69.83 |
| 2025 | 120 | 107934.7 | 1.6342 | 47.5% | 4879.21 | -2701.28 | 73.63 |
| 2026 | 20 | 22875.1 | 1.8672 | 65.0% | 3788.62 | -3768.14 | 177.85 |

## Trade Duration

- 25th percentile bars held: `30.0`
- Median bars held: `40.0`
- 75th percentile bars held: `85.0`
- 90th percentile bars held: `195.0`
- 95th percentile bars held: `289.0`

## Excursion Diagnostics

- Average MFE/R: `1.283`
- Average MAE/R: `-0.6538`

MFE/R and MAE/R are decision-time diagnostic fields for full-whitebox research. They help identify whether losses had enough favorable movement for breakeven or trailing-stop logic, and whether winners required wide adverse movement that a tighter stop would have destroyed.

## Full-Whitebox Diagnostic Queue

Before testing a new rule mutation, inspect whether the weakness is side-specific, exit-specific, period-specific, duration-specific, or excursion-specific. Good next mutations should attack one localized defect while preserving the parent contract and the right-tail behavior that funds the strategy.