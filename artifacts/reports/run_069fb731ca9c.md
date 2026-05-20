# Mutation Lab Run run_069fb731ca9c

- Family: `intraday_trend_atr`
- Version: `Intraday Trend ATR Baseline`
- Stage: `white_box`
- Verdict: `graveyard`
- Dataset: `ds_d14d74e36d0d`

## Frozen Strategy Contract

This run freezes `ma_cross_atr_stop_v1` on `BTCUSDT` at `Binance Spot` / `15m`. The live parameters are `{"allow_long": true, "allow_short": true, "atr_len": 23, "atr_timeframe": "15m", "commission_pct": 0.04, "contract_size": 100.0, "entry_mode": "crossover_only", "execution_model": "mt5_bar_proxy", "fast_len": 25, "initial_capital": 100000.0, "lot_step": 0.01, "ma_kind": "sma", "max_leverage": 1.0, "max_lot": 100.0, "max_no_cross": 5, "min_lot": 0.01, "noise_lookback": 25, "notional_pct": 0.25, "quantity": 1.0, "risk_pct": 0.005, "sizing_mode": "fixed_risk_pct", "skip_below_min_lot": true, "slippage_ticks": 2, "slow_len": 96, "stop_mult": 4.6, "tick_size": 0.01}`.

## Metrics

- Net PnL: `346844.95`
- Return %: `346.84`
- Profit Factor: `1.1619`
- Max Drawdown %: `16.39`
- Expected Payoff: `102.77`
- Total Trades: `3375`
- Win Rate %: `31.23`
- Avg Win / Avg Loss Ratio: `2.5586`
- Approx Breakeven Win Rate: `28.1`
- Execution Model: `mt5_bar_proxy`
- Equity Marking: `mark_to_market`
- Trade-Level Sharpe: `3.1332`
- Trade-Level Sortino: `7.3832`
- Daily Portfolio Sharpe: `1.0989`
- Daily Portfolio Sortino: `1.4281`
- Daily Volatility %: `16.99`
- Worst Daily Return %: `-2.87`
- Positive Day %: `45.77`
- Calmar: `21.1648`
- Sizing Mode: `fixed_risk_pct`
- Avg Entry Exposure %: `35.68`
- Max Entry Exposure %: `100.0`
- Avg Initial Risk %: `0.4954`
- Max Initial Risk %: `0.5`
- Buy & Hold Net PnL: `1663923.89`
- Buy & Hold Asset Return %: `1663.92`
- Buy & Hold Max Drawdown %: `83.97`
- Buy & Hold Calmar: `19.8159`
- Buy & Hold Start/End: `4252.01` -> `75002.22`
- Outperformance %: `-1317.08`
- Calmar Delta: `1.3488`

## Performance Interpretation

This report separates the headline result from the mechanics that created it. A low win rate is not automatically a defect when the average win/loss ratio is high; the important question is whether the strategy preserves enough right-tail winners while reducing avoidable churn, weak sides, poor regimes, or expensive stop exits. Use the diagnostics below to decide the next full-whitebox mutation instead of guessing from the headline metrics alone.

## Production Gate

- Core failures: `['low_profit_factor', 'excess_drawdown']`
- Portfolio / benchmark failures: `[]`
- Production sizing modes: `['fixed_notional_pct', 'fixed_risk_pct', 'mt5_fixed_risk_lot']`
- Benchmark policy: `outperform_return_or_calmar`
- Execution model: `mt5_bar_proxy`

The platform-level rule is deliberately generic: first prove the strategy has enough activity, positive expectancy, bounded mark-to-market drawdown, acceptable daily portfolio Sharpe/Sortino/Calmar, bounded daily loss, and bounded per-trade risk; then judge it under a portfolio sizing model against buy-and-hold. Trade-level Sharpe/Sortino are diagnostic only and may overstate deployable portfolio quality. A strategy does not need to beat buy-and-hold on raw return if it delivers better drawdown-adjusted efficiency, but if it loses on both raw return and Calmar it is not production-comparable yet.

## Capital Model Warning

- fixed_risk_pct sizes each trade by stop distance; `0.005` means `0.5%` of current equity is the intended loss budget before leverage caps.

## Diagnostics

- Entries: `3375`
- Long signals: `1774`
- Short signals: `1776`
- Short quality gate blocks: `0`
- Entry exposure gate blocks: `0`
- Entry exposure gate long blocks: `0`
- Entry exposure gate short blocks: `0`
- Breakeven stop moves: `0`
- MT5 stop modify rejects: `0`
- Time risk filter blocks: `0`
- Stop exits: `946`
- Reverse exits: `2428`
- Reverse confirmation candidates: `0`
- Reverse confirmation exits allowed: `0`
- Reverse confirmation adverse escapes allowed: `0`
- Reverse confirmation suppressed: `0`
- Reverse confirmation suppressed Net PnL: `0`
- Time-decay exits: `0`
- Time-decay confirmation candidates: `0`
- Time-decay confirmation exits allowed: `0`
- Time-decay confirmation suppressed: `0`
- Time-decay confirmation suppressed Net PnL: `0`
- Time exits: `1`
- Pending entry orders: `947`
- Pending order fills: `3375`
- Dropped pending orders at end of data: `0`

## Side Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| long | 1693 | 317519.06 | 1.2894 | 31.96% | 2614.88 | -952.37 | 83.66 |
| short | 1682 | 29325.89 | 1.0281 | 30.5% | 2094.62 | -894.11 | 78.75 |

## Exit-Reason Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| reverse | 2428 | 1763450.75 | 3.4322 | 43.37% | 2363.23 | -527.3 | 97.78 |
| stop | 946 | -1417311.42 | 0.0 | 0.0% | 0.0 | -1498.22 | 38.76 |
| time_exit | 1 | 705.62 | 705.62 | 100.0% | 705.62 | 0.0 | 10.0 |

## Period Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 138 | 22845.3 | 1.8915 | 36.23% | 969.4 | -291.19 | 89.49 |
| 2018 | 344 | 28094.6 | 1.2893 | 36.63% | 993.58 | -445.4 | 90.1 |
| 2019 | 376 | 50258.66 | 1.3605 | 29.52% | 1708.88 | -526.14 | 84.97 |
| 2020 | 377 | 38526.18 | 1.2108 | 28.65% | 2048.76 | -679.33 | 81.67 |
| 2021 | 393 | 27685.79 | 1.131 | 34.61% | 1757.22 | -822.16 | 82.95 |
| 2022 | 387 | 2859.69 | 1.0114 | 28.17% | 2318.2 | -898.65 | 82.11 |
| 2023 | 404 | 42099.29 | 1.1384 | 28.47% | 3011.96 | -1052.86 | 77.38 |
| 2024 | 402 | 98245.16 | 1.2931 | 32.59% | 3308.28 | -1236.68 | 77.71 |
| 2025 | 420 | -23550.56 | 0.9505 | 29.52% | 3647.54 | -1607.59 | 74.35 |
| 2026 | 134 | 59780.84 | 1.4938 | 32.84% | 4110.36 | -1345.28 | 73.93 |

## Trade Duration

- 25th percentile bars held: `25.0`
- Median bars held: `65.0`
- 75th percentile bars held: `110.0`
- 90th percentile bars held: `177.0`
- 95th percentile bars held: `233.0`

## Excursion Diagnostics

- Average MFE/R: `1.5042`
- Average MAE/R: `-0.7057`

MFE/R and MAE/R are decision-time diagnostic fields for full-whitebox research. They help identify whether losses had enough favorable movement for breakeven or trailing-stop logic, and whether winners required wide adverse movement that a tighter stop would have destroyed.

## Full-Whitebox Diagnostic Queue

Before testing a new rule mutation, inspect whether the weakness is side-specific, exit-specific, period-specific, duration-specific, or excursion-specific. Good next mutations should attack one localized defect while preserving the parent contract and the right-tail behavior that funds the strategy.