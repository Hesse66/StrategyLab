# Mutation Lab Run run_11e08e6dcdac

- Family: `intraday_trend_atr`
- Version: `Intraday Trend ATR Baseline | tuned atr_len=12, fast_len=23, max_leverage=0.75, noise_lookback=26... | tuned time_decay_bars=20`
- Stage: `white_box`
- Verdict: `promotion_candidate`
- Dataset: `ds_d14d74e36d0d`

## Frozen Strategy Contract

This run freezes `ma_cross_atr_stop_v1` on `BTCUSDT` at `Binance Spot` / `15m`. The live parameters are `{"allow_long": true, "allow_short": true, "atr_len": 12, "atr_timeframe": "15m", "commission_pct": 0.04, "contract_size": 100.0, "entry_mode": "crossover_only", "execution_model": "mt5_bar_proxy", "fast_len": 23, "initial_capital": 100000.0, "lot_step": 0.01, "ma_kind": "sma", "max_leverage": 0.75, "max_lot": 100.0, "max_no_cross": 5, "min_lot": 0.01, "noise_lookback": 26, "notional_pct": 0.05, "quantity": 1.0, "risk_pct": 0.0025, "sizing_mode": "fixed_risk_pct", "skip_below_min_lot": true, "slippage_ticks": 2, "slow_len": 96, "stop_mult": 3.0, "tick_size": 0.01, "time_decay_bars": 20, "time_decay_exit_enabled": true, "time_decay_min_mfe_r": 0.25}`.

## Metrics

- Net PnL: `448946.25`
- Return %: `448.95`
- Profit Factor: `1.2949`
- Max Drawdown %: `10.58`
- Expected Payoff: `132.24`
- Total Trades: `3395`
- Win Rate %: `27.42`
- Avg Win / Avg Loss Ratio: `3.4272`
- Approx Breakeven Win Rate: `22.59`
- Execution Model: `mt5_bar_proxy`
- Equity Marking: `mark_to_market`
- Trade-Level Sharpe: `4.2973`
- Trade-Level Sortino: `13.7899`
- Daily Portfolio Sharpe: `1.5735`
- Daily Portfolio Sortino: `2.321`
- Daily Volatility %: `12.99`
- Worst Daily Return %: `-2.17`
- Positive Day %: `42.27`
- Calmar: `42.4458`
- Sizing Mode: `fixed_risk_pct`
- Avg Entry Exposure %: `27.53`
- Max Entry Exposure %: `75.0`
- Avg Initial Risk %: `0.247`
- Max Initial Risk %: `0.25`
- Buy & Hold Net PnL: `1663923.89`
- Buy & Hold Asset Return %: `1663.92`
- Buy & Hold Max Drawdown %: `83.97`
- Buy & Hold Calmar: `19.8159`
- Buy & Hold Start/End: `4252.01` -> `75002.22`
- Outperformance %: `-1214.98`
- Calmar Delta: `22.6299`

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

- fixed_risk_pct sizes each trade by stop distance; `0.0025` means `0.25%` of current equity is the intended loss budget before leverage caps.

## Parent Comparison

- Profit Factor Delta: `0.0318`
- Net PnL Delta: `71874.63`
- Drawdown % Delta: `-0.12`
- Trade Count Delta: `14`

## Single Mutation

- Summary: `time_decay_bars=20`
- Rationale: 

## Diagnostics

- Entries: `3395`
- Long signals: `1766`
- Short signals: `1768`
- Short quality gate blocks: `0`
- Entry exposure gate blocks: `0`
- Entry exposure gate long blocks: `0`
- Entry exposure gate short blocks: `0`
- Breakeven stop moves: `0`
- MT5 stop modify rejects: `0`
- Time risk filter blocks: `0`
- Stop exits: `1466`
- Reverse exits: `1642`
- Reverse confirmation candidates: `0`
- Reverse confirmation exits allowed: `0`
- Reverse confirmation adverse escapes allowed: `0`
- Reverse confirmation suppressed: `0`
- Reverse confirmation suppressed Net PnL: `0`
- Time-decay exits: `286`
- Time-decay confirmation candidates: `0`
- Time-decay confirmation exits allowed: `0`
- Time-decay confirmation suppressed: `0`
- Time-decay confirmation suppressed Net PnL: `0`
- Time exits: `1`
- Pending entry orders: `1753`
- Pending order fills: `3395`
- Dropped pending orders at end of data: `0`

## Side Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| long | 1697 | 349437.37 | 1.4506 | 28.23% | 2348.61 | -636.74 | 68.25 |
| short | 1698 | 99508.88 | 1.1333 | 26.62% | 1872.14 | -599.28 | 64.83 |

## Exit-Reason Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| reverse | 1642 | 1756446.14 | 9.2124 | 56.15% | 2137.01 | -297.05 | 107.6 |
| stop | 1466 | -1230693.4 | 0.0 | 0.0% | 0.0 | -839.49 | 29.67 |
| time_decay | 286 | -77397.02 | 0.0035 | 2.8% | 34.43 | -279.4 | 20.0 |
| time_exit | 1 | 590.53 | 590.53 | 100.0% | 590.53 | 0.0 | 10.0 |

## Period Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 137 | 18364.29 | 2.1108 | 34.31% | 742.48 | -183.69 | 77.61 |
| 2018 | 333 | 28524.29 | 1.5175 | 31.83% | 789.07 | -242.81 | 75.19 |
| 2019 | 369 | 63170.14 | 1.7255 | 29.54% | 1378.35 | -334.88 | 72.1 |
| 2020 | 397 | 35446.66 | 1.2761 | 23.68% | 1742.96 | -423.73 | 63.62 |
| 2021 | 412 | 26243.47 | 1.1805 | 31.55% | 1320.01 | -515.45 | 67.24 |
| 2022 | 394 | 58373.11 | 1.3341 | 25.89% | 2284.95 | -598.26 | 66.97 |
| 2023 | 409 | 9458.06 | 1.0407 | 21.27% | 2779.06 | -721.49 | 60.48 |
| 2024 | 404 | 119324.49 | 1.4839 | 28.22% | 3209.79 | -850.31 | 65.99 |
| 2025 | 411 | 40357.6 | 1.1228 | 25.79% | 3479.93 | -1077.1 | 60.89 |
| 2026 | 129 | 49684.14 | 1.4615 | 27.91% | 4370.57 | -1157.6 | 60.92 |

## Trade Duration

- 25th percentile bars held: `15.0`
- Median bars held: `35.0`
- 75th percentile bars held: `93.0`
- 90th percentile bars held: `164.0`
- 95th percentile bars held: `219.0`

## Excursion Diagnostics

- Average MFE/R: `2.1113`
- Average MAE/R: `-0.8637`

MFE/R and MAE/R are decision-time diagnostic fields for full-whitebox research. They help identify whether losses had enough favorable movement for breakeven or trailing-stop logic, and whether winners required wide adverse movement that a tighter stop would have destroyed.

## Full-Whitebox Diagnostic Queue

Before testing a new rule mutation, inspect whether the weakness is side-specific, exit-specific, period-specific, duration-specific, or excursion-specific. Good next mutations should attack one localized defect while preserving the parent contract and the right-tail behavior that funds the strategy.