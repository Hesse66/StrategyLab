# Mutation Lab Run run_de1a4e5de65a

- Family: `asm_fib_liquidity`
- Version: `ASM Fibonacci Liquidity FVG Universal Parent | tuned context_bias_max_age_bars=12, context_bias_must_align_with_external_bias=False, external_pivot_period=2, fib_entry_retracement=0.55...`
- Stage: `white_box`
- Verdict: `graveyard`
- Dataset: `ds_d14d74e36d0d`

## Frozen Strategy Contract

This run freezes `asm_fib_liquidity_fvg_v1` on `BTCUSDT` at `Binance Spot` / `15m`. The live parameters are `{"active_timeframe_profile": "intraday_15m", "allow_long": true, "allow_short": true, "break_confirmation": "close", "commission_pct": 0.04, "context_bias_event": "bos_or_choch", "context_bias_max_age_bars": 12, "context_bias_must_align_with_external_bias": false, "context_bias_required": true, "context_bias_source": "context_external_structure", "context_timeframe": "1h", "displacement_atr_len": 14, "entry_order_type": "limit_touch", "entry_price_source": "fib_level", "entry_validation_stream": "internal_structure", "execution_timeframe": "15m", "exit_policy": "set_and_forget_stop_target", "external_pivot_period": 2, "external_role": "context_range", "fib_entry_retracement": 0.55, "fib_range_source": "external_structure", "fib_stop_retracement": 1.0, "fib_target_retracement": 0.0, "fvg_context_source": "external_or_internal", "fvg_enabled": true, "fvg_max_age_bars": 65, "fvg_min_gap_atr": 0.35, "fvg_mitigation_rule": "touch_through_far_edge", "fvg_overlap_required": true, "fvg_overlap_tolerance_atr": 0.35, "higher_context_timeframe": "4h", "initial_capital": 100000.0, "internal_confirmation_event": "bos_or_choch", "internal_confirmation_max_age_bars": 4, "internal_confirmation_required": true, "internal_confirmation_timing": "after_retracement_and_sweep", "internal_must_align_with_external_bias": true, "internal_pivot_period": 1, "internal_role": "entry_confirmation", "liquidity_sweep_required": false, "max_leverage": 0.25, "max_setup_age_bars": 10, "min_displacement_atr": 2.9, "notional_pct": 0.25, "one_position_at_time": true, "premium_discount_midpoint": 0.5, "quantity": 1.0, "range_max_atr": 11.0, "range_min_atr": 4.5, "require_discount_for_longs": true, "require_premium_for_shorts": true, "resample_context_from_execution_bars": true, "risk_pct": 0.001, "same_bar_exit_policy": "stop_first", "setup_after_break": "bos_or_choch", "sizing_mode": "fixed_notional_pct", "slippage_ticks": 2, "stop_buffer_atr_mult": 0.0, "structure_stream": "external_and_internal_intraday", "sweep_close_back_inside": true, "sweep_lookback_bars": 5, "sweep_window_bars": 5, "tick_size": 0.01, "time_risk_block_utc_hours": [], "time_risk_block_weekdays": [], "time_risk_filter_enabled": false, "time_stop_bars": 10, "time_stop_enabled": false, "time_stop_min_mfe_r": 0.25, "timeframe_profiles": {"intraday_15m": {"context_bias_required": true, "context_timeframe": "1h", "execution_timeframe": "15m", "external_pivot_period": 4, "fib_entry_retracement": 0.67, "higher_context_timeframe": "4h", "internal_confirmation_max_age_bars": 24, "internal_confirmation_required": true, "internal_pivot_period": 2, "max_setup_age_bars": 96, "sweep_lookback_bars": 20, "sweep_window_bars": 48}, "intraday_5m": {"context_bias_required": true, "context_timeframe": "15m", "execution_timeframe": "5m", "external_pivot_period": 4, "fib_entry_retracement": 0.67, "higher_context_timeframe": "1h", "internal_confirmation_max_age_bars": 36, "internal_confirmation_required": true, "internal_pivot_period": 2, "max_setup_age_bars": 144, "sweep_lookback_bars": 30, "sweep_window_bars": 72}, "swing_4h": {"context_bias_required": false, "context_timeframe": "1d", "execution_timeframe": "4h", "external_pivot_period": 4, "fib_entry_retracement": 0.71, "higher_context_timeframe": "1d", "internal_confirmation_max_age_bars": 12, "internal_confirmation_required": false, "internal_pivot_period": 2, "max_setup_age_bars": 60, "sweep_lookback_bars": 12, "sweep_window_bars": 24}}, "use_timeframe_profile_overrides": true}`.

## Metrics

- Net PnL: `22310.48`
- Return %: `22.31`
- Profit Factor: `1.3818`
- Max Drawdown %: `3.36`
- Expected Payoff: `55.64`
- Total Trades: `401`
- Win Rate %: `52.12`
- Avg Win / Avg Loss Ratio: `1.2694`
- Approx Breakeven Win Rate: `44.06`
- Trade-Level Sharpe: `2.334`
- Trade-Level Sortino: `2.9857`
- Daily Portfolio Sharpe: `0.7822`
- Daily Portfolio Sortino: `0.3519`
- Daily Volatility %: `3.02`
- Worst Daily Return %: `-1.46`
- Positive Day %: `6.44`
- Calmar: `6.6452`
- Sizing Mode: `fixed_notional_pct`
- Avg Entry Exposure %: `25.0`
- Max Entry Exposure %: `25.0`
- Avg Initial Risk %: `0.391`
- Max Initial Risk %: `2.5922`
- Buy & Hold Net PnL: `1644237.67`
- Buy & Hold Asset Return %: `1644.24`
- Buy & Hold Max Drawdown %: `83.97`
- Buy & Hold Calmar: `19.5815`
- Buy & Hold Start/End: `4300.0` -> `75002.22`
- Outperformance %: `-1621.93`
- Calmar Delta: `-12.9362`

## Performance Interpretation

This report separates the headline result from the mechanics that created it. A low win rate is not automatically a defect when the average win/loss ratio is high; the important question is whether the strategy preserves enough right-tail winners while reducing avoidable churn, weak sides, poor regimes, or expensive stop exits. Use the diagnostics below to decide the next full-whitebox mutation instead of guessing from the headline metrics alone.

## Production Gate

- Core failures: `['low_daily_sortino', 'excess_trade_risk']`
- Portfolio / benchmark failures: `['weak_vs_buy_hold_benchmark']`
- Production sizing modes: `['fixed_notional_pct', 'fixed_risk_pct']`
- Benchmark policy: `outperform_return_or_calmar`

The platform-level rule is deliberately generic: first prove the strategy has enough activity, positive expectancy, bounded drawdown, acceptable daily portfolio Sharpe/Sortino/Calmar, bounded daily loss, and bounded per-trade risk; then judge it under a portfolio sizing model against buy-and-hold. Trade-level Sharpe/Sortino are diagnostic only and may overstate deployable portfolio quality. A strategy does not need to beat buy-and-hold on raw return if it delivers better drawdown-adjusted efficiency, but if it loses on both raw return and Calmar it is not production-comparable yet.

## Capital Model Warning

- fixed_notional_pct compounds position size from current equity; `0.25` means `25.0%` of current equity is deployed as notional on every new trade.

## Single Mutation

- Summary: `context_bias_max_age_bars=12, context_bias_must_align_with_external_bias=False, external_pivot_period=2, fib_entry_retracement=0.55...`
- Rationale: 

## Diagnostics

- Entries: `401`
- Long signals: `210`
- Short signals: `191`
- Short quality gate blocks: `0`
- Breakeven stop moves: `0`
- Time risk filter blocks: `0`
- Stop exits: `243`
- Reverse exits: `0`
- Time-decay exits: `0`
- Time exits: `0`

## Side Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| long | 210 | 6914.17 | 1.2251 | 50.48% | 354.96 | -295.3 | 19.98 |
| short | 191 | 15396.31 | 1.5553 | 53.93% | 418.66 | -315.07 | 17.88 |

## Exit-Reason Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| stop | 243 | -11355.37 | 0.7617 | 35.8% | 417.21 | -305.47 | 12.84 |
| target | 158 | 33665.85 | 4.1216 | 77.22% | 364.35 | -299.58 | 28.42 |

## Period Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 16 | 4854.74 | 2.6563 | 56.25% | 865.09 | -418.73 | 33.19 |
| 2018 | 39 | 789.91 | 1.1085 | 53.85% | 384.2 | -404.35 | 19.69 |
| 2019 | 37 | 5892.81 | 2.8504 | 59.46% | 412.61 | -212.31 | 23.57 |
| 2020 | 42 | 1009.6 | 1.148 | 47.62% | 391.65 | -310.16 | 21.19 |
| 2021 | 49 | 8323.77 | 1.8882 | 55.1% | 655.39 | -425.98 | 26.49 |
| 2022 | 44 | 239.08 | 1.0291 | 52.27% | 368.0 | -391.66 | 24.05 |
| 2023 | 45 | 3074.02 | 1.9893 | 66.67% | 206.04 | -207.15 | 15.11 |
| 2024 | 58 | -2119.77 | 0.7869 | 41.38% | 326.11 | -292.54 | 15.57 |
| 2025 | 57 | 794.49 | 1.1526 | 47.37% | 222.2 | -173.5 | 7.67 |
| 2026 | 14 | -548.17 | 0.7682 | 42.86% | 302.78 | -295.61 | 12.43 |

## Trade Duration

- 25th percentile bars held: `0.0`
- Median bars held: `4.0`
- 75th percentile bars held: `20.0`
- 90th percentile bars held: `51.0`
- 95th percentile bars held: `95.0`

## Excursion Diagnostics

- Average MFE/R: `7.999`
- Average MAE/R: `-8.3169`

MFE/R and MAE/R are decision-time diagnostic fields for full-whitebox research. They help identify whether losses had enough favorable movement for breakeven or trailing-stop logic, and whether winners required wide adverse movement that a tighter stop would have destroyed.

## Full-Whitebox Diagnostic Queue

Before testing a new rule mutation, inspect whether the weakness is side-specific, exit-specific, period-specific, duration-specific, or excursion-specific. Good next mutations should attack one localized defect while preserving the parent contract and the right-tail behavior that funds the strategy.