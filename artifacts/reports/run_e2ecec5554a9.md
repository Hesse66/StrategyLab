# Mutation Lab Run run_e2ecec5554a9

- Family: `intraday_trend_atr`
- Version: `Intraday Trend ATR Baseline | tuned atr_len=12, fast_len=23, max_leverage=0.75, noise_lookback=26... | tuned time_decay_bars=20 | tuned atr_len=40, max_leverage=0.5, risk_pct=0.003`
- Stage: `white_box`
- Verdict: `promotion_candidate`
- Dataset: `ds_d14d74e36d0d`

## Frozen Strategy Contract

This run freezes `ma_cross_atr_stop_v1` on `BTCUSDT` at `Binance Spot` / `15m`. The live parameters are `{"allow_long": true, "allow_short": true, "atr_len": 40, "atr_timeframe": "15m", "commission_pct": 0.04, "contract_size": 100.0, "entry_mode": "crossover_only", "execution_model": "mt5_bar_proxy", "fast_len": 23, "initial_capital": 100000.0, "lot_step": 0.01, "ma_kind": "sma", "max_leverage": 0.5, "max_lot": 100.0, "max_no_cross": 5, "min_lot": 0.01, "noise_lookback": 26, "notional_pct": 0.05, "quantity": 1.0, "risk_pct": 0.003, "short_time_risk_block_utc_hours": [6, 9, 16, 20], "short_time_risk_block_weekdays": [4], "short_time_risk_filter_enabled": true, "sizing_mode": "fixed_risk_pct", "skip_below_min_lot": true, "slippage_ticks": 2, "slow_len": 96, "stop_mult": 3.0, "tick_size": 0.01, "time_decay_bars": 20, "time_decay_exit_enabled": true, "time_decay_min_mfe_r": 0.25}`.

## Metrics

- Net PnL: `795045.32`
- Return %: `795.05`
- Profit Factor: `1.3825`
- Max Drawdown %: `11.17`
- Expected Payoff: `287.12`
- Total Trades: `2769`
- Win Rate %: `26.94`
- Avg Win / Avg Loss Ratio: `3.749`
- Approx Breakeven Win Rate: `21.06`
- Execution Model: `mt5_bar_proxy`
- Equity Marking: `mark_to_market`
- Trade-Level Sharpe: `4.9662`
- Trade-Level Sortino: `16.6661`
- Daily Portfolio Sharpe: `1.846`
- Daily Portfolio Sortino: `2.645`
- Daily Volatility %: `14.22`
- Worst Daily Return %: `-2.33`
- Positive Day %: `41.42`
- Calmar: `71.1564`
- Sizing Mode: `fixed_risk_pct`
- Avg Entry Exposure %: `29.74`
- Max Entry Exposure %: `50.0`
- Avg Initial Risk %: `0.2857`
- Max Initial Risk %: `0.3`
- Buy & Hold Net PnL: `1663923.89`
- Buy & Hold Asset Return %: `1663.92`
- Buy & Hold Max Drawdown %: `83.97`
- Buy & Hold Calmar: `19.8159`
- Buy & Hold Start/End: `4252.01` -> `75002.22`
- Outperformance %: `-868.88`
- Calmar Delta: `51.3405`

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

- Profit Factor Delta: `0.0876`
- Net PnL Delta: `346099.07`
- Drawdown % Delta: `0.59`
- Trade Count Delta: `-626`

## Single Mutation

- Summary: `atr_len=40, max_leverage=0.5, risk_pct=0.003`
- Rationale: 

## Diagnostics

- Entries: `2769`
- Long signals: `1766`
- Short signals: `1768`
- Short quality gate blocks: `0`
- Entry exposure gate blocks: `0`
- Entry exposure gate long blocks: `0`
- Entry exposure gate short blocks: `0`
- Breakeven stop moves: `0`
- MT5 stop modify rejects: `0`
- Time risk filter blocks: `0`
- Stop exits: `1306`
- Reverse exits: `1248`
- Reverse confirmation candidates: `0`
- Reverse confirmation exits allowed: `0`
- Reverse confirmation adverse escapes allowed: `0`
- Reverse confirmation suppressed: `0`
- Reverse confirmation suppressed Net PnL: `0`
- Time-decay exits: `214`
- Time-decay confirmation candidates: `0`
- Time-decay confirmation exits allowed: `0`
- Time-decay confirmation suppressed: `0`
- Time-decay confirmation suppressed Net PnL: `0`
- Time exits: `1`
- Pending entry orders: `1521`
- Pending order fills: `2769`
- Dropped pending orders at end of data: `0`

## Side Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| long | 1542 | 555057.02 | 1.4601 | 27.24% | 4193.7 | -1075.13 | 84.54 |
| short | 1227 | 239988.3 | 1.2751 | 26.57% | 3412.08 | -968.2 | 64.5 |

## Exit-Reason Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| reverse | 1248 | 2631187.76 | 11.9415 | 59.05% | 3896.43 | -470.6 | 126.43 |
| stop | 1306 | -1746586.4 | 0.0 | 0.0% | 0.0 | -1337.36 | 36.32 |
| time_decay | 214 | -90978.25 | 0.0066 | 3.74% | 75.65 | -444.58 | 20.0 |
| time_exit | 1 | 1422.21 | 1422.21 | 100.0% | 1422.21 | 0.0 | 10.0 |

## Period Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 102 | 20689.18 | 2.3218 | 31.37% | 1135.67 | -223.61 | 100.68 |
| 2018 | 278 | 38818.72 | 1.6304 | 32.37% | 1115.48 | -327.53 | 83.28 |
| 2019 | 313 | 71352.35 | 1.6868 | 27.16% | 2061.74 | -455.68 | 77.81 |
| 2020 | 323 | 65629.01 | 1.4403 | 22.29% | 2981.62 | -593.82 | 76.87 |
| 2021 | 360 | 31817.78 | 1.1602 | 31.11% | 2057.67 | -800.97 | 72.61 |
| 2022 | 337 | 83015.85 | 1.3745 | 26.71% | 3385.69 | -897.55 | 70.0 |
| 2023 | 334 | 163146.61 | 1.5657 | 22.46% | 6020.3 | -1113.42 | 69.51 |
| 2024 | 303 | 208842.04 | 1.5329 | 28.05% | 7067.63 | -1797.74 | 78.82 |
| 2025 | 319 | 50730.45 | 1.1 | 23.2% | 7543.64 | -2071.43 | 71.3 |
| 2026 | 100 | 61003.33 | 1.4346 | 31.0% | 6495.55 | -2034.18 | 73.22 |

## Trade Duration

- 25th percentile bars held: `16.0`
- Median bars held: `38.0`
- 75th percentile bars held: `100.0`
- 90th percentile bars held: `188.0`
- 95th percentile bars held: `266.0`

## Excursion Diagnostics

- Average MFE/R: `2.2966`
- Average MAE/R: `-0.9119`

MFE/R and MAE/R are decision-time diagnostic fields for full-whitebox research. They help identify whether losses had enough favorable movement for breakeven or trailing-stop logic, and whether winners required wide adverse movement that a tighter stop would have destroyed.

## Full-Whitebox Diagnostic Queue

Before testing a new rule mutation, inspect whether the weakness is side-specific, exit-specific, period-specific, duration-specific, or excursion-specific. Good next mutations should attack one localized defect while preserving the parent contract and the right-tail behavior that funds the strategy.