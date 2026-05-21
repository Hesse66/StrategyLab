# Mutation Lab Run run_70f7b3e4f91a

- Family: `intraday_trend_atr`
- Version: `Intraday Trend ATR Baseline | tuned atr_len=12, fast_len=23, max_leverage=0.75, noise_lookback=26... | tuned time_decay_bars=20 | tuned atr_len=40, max_leverage=0.5, risk_pct=0.003 | tuned reverse_confirm_allow_if_unrealized_r_lte=-0.4, reverse_confirm_max_bars=3 | tuned entry_blackbox_veto_side_months=['long:8', 'short:12'], entry_blackbox_veto_utc_hours=[15, 11]`
- Stage: `white_box`
- Verdict: `promotion_candidate`
- Dataset: `ds_d14d74e36d0d`

## Frozen Strategy Contract

This run freezes `ma_cross_atr_stop_v1` on `BTCUSDT` at `Binance Spot` / `15m`. The live parameters are `{"allow_long": true, "allow_short": true, "atr_len": 40, "atr_timeframe": "15m", "commission_pct": 0.04, "contract_size": 100.0, "entry_blackbox_veto_enabled": true, "entry_blackbox_veto_side_months": ["long:8", "short:12"], "entry_blackbox_veto_utc_hours": [15, 11], "entry_mode": "crossover_only", "execution_model": "mt5_bar_proxy", "fast_len": 23, "initial_capital": 100000.0, "lot_step": 0.01, "ma_kind": "sma", "max_leverage": 0.5, "max_lot": 100.0, "max_no_cross": 5, "min_lot": 0.01, "noise_lookback": 26, "notional_pct": 0.05, "quantity": 1.0, "reverse_confirm_allow_if_unrealized_r_lte": -0.4, "reverse_confirm_max_bars": 3, "reverse_confirm_min_mfe_r": 0.2, "reverse_confirm_require_no_breakeven_move": false, "reverse_confirmation_enabled": true, "risk_pct": 0.003, "short_time_risk_block_utc_hours": [6, 9, 16, 20], "short_time_risk_block_weekdays": [4], "short_time_risk_filter_enabled": true, "sizing_mode": "fixed_risk_pct", "skip_below_min_lot": true, "slippage_ticks": 2, "slow_len": 96, "stop_mult": 3.0, "tick_size": 0.01, "time_decay_bars": 20, "time_decay_exit_enabled": true, "time_decay_min_mfe_r": 0.25}`.

## Metrics

- Net PnL: `937473.59`
- Return %: `937.47`
- Profit Factor: `1.5316`
- Max Drawdown %: `8.03`
- Expected Payoff: `412.26`
- Total Trades: `2274`
- Win Rate %: `27.66`
- Avg Win / Avg Loss Ratio: `4.0057`
- Approx Breakeven Win Rate: `19.98`
- Execution Model: `mt5_bar_proxy`
- Equity Marking: `mark_to_market`
- Trade-Level Sharpe: `5.4979`
- Trade-Level Sortino: `19.3801`
- Daily Portfolio Sharpe: `2.052`
- Daily Portfolio Sortino: `3.0054`
- Daily Volatility %: `13.58`
- Worst Daily Return %: `-2.33`
- Positive Day %: `37.44`
- Calmar: `116.7335`
- Sizing Mode: `fixed_risk_pct`
- Avg Entry Exposure %: `29.63`
- Max Entry Exposure %: `50.0`
- Avg Initial Risk %: `0.286`
- Max Initial Risk %: `0.3`
- Buy & Hold Net PnL: `1663923.89`
- Buy & Hold Asset Return %: `1663.92`
- Buy & Hold Max Drawdown %: `83.97`
- Buy & Hold Calmar: `19.8159`
- Buy & Hold Start/End: `4252.01` -> `75002.22`
- Outperformance %: `-726.45`
- Calmar Delta: `96.9176`

## Performance Interpretation

This report separates the headline result from the mechanics that created it. A low win rate is not automatically a defect when the average win/loss ratio is high; the important question is whether the strategy preserves enough right-tail winners while reducing avoidable churn, weak sides, poor regimes, or expensive stop exits. Use the diagnostics below to decide the next full-whitebox mutation instead of guessing from the headline metrics alone.

## Production Gate

- Core failures: `[]`
- Portfolio / benchmark failures: `[]`
- Production sizing modes: `['fixed_notional_pct', 'fixed_risk_pct', 'mt5_fixed_risk_lot']`
- Benchmark policy: `outperform_return_or_calmar`
- Execution model: `mt5_bar_proxy`

The platform-level rule is deliberately generic: first prove the strategy has enough activity, positive expectancy, bounded mark-to-market drawdown, acceptable daily portfolio Sharpe/Sortino/Calmar, bounded daily loss, and bounded per-trade risk; then judge it under a portfolio sizing model against buy-and-hold. Trade-level Sharpe/Sortino are diagnostic only and may overstate deployable portfolio quality. A strategy does not need to beat buy-and-hold on raw return if it delivers better drawdown-adjusted efficiency, but if it loses on both raw return and Calmar it is not production-comparable yet.

## Capital Model Warning

- fixed_risk_pct sizes each trade by stop distance; `0.003` means `0.3%` of current equity is the intended loss budget before leverage caps.

## Parent Comparison

- Profit Factor Delta: `0.1355`
- Net PnL Delta: `99818.46`
- Drawdown % Delta: `-3.02`
- Trade Count Delta: `-446`

## Single Mutation

- Summary: `entry_blackbox_veto_side_months=['long:8', 'short:12'], entry_blackbox_veto_utc_hours=[15, 11]`
- Rationale: 

## Diagnostics

- Entries: `2274`
- Long signals: `1766`
- Short signals: `1768`
- Short quality gate blocks: `0`
- Entry exposure gate blocks: `0`
- Entry exposure gate long blocks: `0`
- Entry exposure gate short blocks: `0`
- Entry black-box veto blocks: `493`
- Entry black-box veto long blocks: `255`
- Entry black-box veto short blocks: `238`
- Breakeven stop moves: `0`
- MT5 stop modify rejects: `0`
- Time risk filter blocks: `0`
- Stop exits: `1076`
- Reverse exits: `1013`
- Reverse confirmation candidates: `1041`
- Reverse confirmation exits allowed: `1013`
- Reverse confirmation adverse escapes allowed: `178`
- Reverse confirmation suppressed: `28`
- Reverse confirmation suppressed Net PnL: `11069.5`
- Time-decay exits: `184`
- Time-decay confirmation candidates: `0`
- Time-decay confirmation exits allowed: `0`
- Time-decay confirmation suppressed: `0`
- Time-decay confirmation suppressed Net PnL: `0`
- Time exits: `1`
- Pending entry orders: `1754`
- Pending order fills: `2274`
- Dropped pending orders at end of data: `0`

## Side Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| long | 1299 | 613940.04 | 1.5845 | 27.87% | 4597.37 | -1120.93 | 86.52 |
| short | 975 | 323533.55 | 1.4537 | 27.38% | 3882.25 | -1007.1 | 67.26 |

## Exit-Reason Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| reverse | 1013 | 2501909.42 | 13.7213 | 61.3% | 4345.54 | -501.71 | 132.01 |
| stop | 1076 | -1485223.03 | 0.0 | 0.0% | 0.0 | -1380.32 | 37.69 |
| time_decay | 184 | -80861.32 | 0.0071 | 3.8% | 82.88 | -460.12 | 20.0 |
| time_exit | 1 | 1648.52 | 1648.52 | 100.0% | 1648.52 | 0.0 | 10.0 |

## Period Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 72 | 19318.75 | 2.6464 | 33.33% | 1293.86 | -244.46 | 105.54 |
| 2018 | 223 | 21003.6 | 1.4432 | 31.84% | 963.23 | -311.75 | 79.66 |
| 2019 | 261 | 71739.51 | 1.8954 | 26.82% | 2169.42 | -419.48 | 80.34 |
| 2020 | 273 | 76639.35 | 1.6562 | 24.18% | 2930.79 | -564.22 | 82.0 |
| 2021 | 301 | 33824.18 | 1.2041 | 30.56% | 2168.91 | -792.9 | 71.76 |
| 2022 | 274 | 97935.88 | 1.5418 | 27.74% | 3667.11 | -912.95 | 75.09 |
| 2023 | 264 | 209210.65 | 1.8793 | 23.48% | 7211.92 | -1177.86 | 74.55 |
| 2024 | 254 | 201275.95 | 1.6024 | 29.53% | 7138.75 | -1866.65 | 80.26 |
| 2025 | 268 | 122810.4 | 1.2706 | 24.63% | 8736.77 | -2246.61 | 75.62 |
| 2026 | 84 | 83715.32 | 1.6204 | 32.14% | 8098.61 | -2367.49 | 80.25 |

## Trade Duration

- 25th percentile bars held: `17.0`
- Median bars held: `40.0`
- 75th percentile bars held: `104.0`
- 90th percentile bars held: `194.0`
- 95th percentile bars held: `271.0`

## Excursion Diagnostics

- Average MFE/R: `2.4243`
- Average MAE/R: `-0.913`

MFE/R and MAE/R are decision-time diagnostic fields for full-whitebox research. They help identify whether losses had enough favorable movement for breakeven or trailing-stop logic, and whether winners required wide adverse movement that a tighter stop would have destroyed.

## Full-Whitebox Diagnostic Queue

Before testing a new rule mutation, inspect whether the weakness is side-specific, exit-specific, period-specific, duration-specific, or excursion-specific. Good next mutations should attack one localized defect while preserving the parent contract and the right-tail behavior that funds the strategy.