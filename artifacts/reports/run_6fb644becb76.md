# Mutation Lab Run run_6fb644becb76

- Family: `xauusd_ghl_dc`
- Version: `XAUUSD GHL+DC Parent`
- Stage: `white_box`
- Verdict: `graveyard`
- Dataset: `ds_4e109af56413`

## Frozen Strategy Contract

This run freezes `ghl_dc_breakout_v1` on `XAUUSD` at `IC Markets MT5` / `30m`. The live parameters are `{"allow_long": true, "allow_short": true, "atr_len": 14, "commission_pct": 0.0, "donchian_length": 55, "gann_high_period": 13, "gann_low_period": 21, "initial_capital": 100000.0, "max_breakout_bars": 7, "max_leverage": 1.0, "notional_pct": 0.25, "quantity": 1.0, "risk_pct": 0.005, "sizing_mode": "fixed_risk_pct", "slippage_ticks": 10, "stop_mode": "atr", "stop_mult": 2.5, "tick_size": 0.01}`.

## Metrics

- Net PnL: `23091.53`
- Return %: `23.09`
- Profit Factor: `1.1001`
- Max Drawdown %: `12.91`
- Expected Payoff: `17.35`
- Total Trades: `1331`
- Win Rate %: `36.74`
- Avg Win / Avg Loss Ratio: `1.8943`
- Approx Breakeven Win Rate: `34.55`
- Trade-Level Sharpe: `1.1537`
- Trade-Level Sortino: `2.0006`
- Daily Portfolio Sharpe: `0.4697`
- Daily Portfolio Sortino: `0.5464`
- Daily Volatility %: `8.05`
- Worst Daily Return %: `-1.01`
- Positive Day %: `19.35`
- Calmar: `1.7885`
- Sizing Mode: `fixed_risk_pct`
- Avg Entry Exposure %: `90.62`
- Max Entry Exposure %: `100.0`
- Avg Initial Risk %: `0.4064`
- Max Initial Risk %: `0.5`
- Buy & Hold Net PnL: `263532.97`
- Buy & Hold Asset Return %: `263.53`
- Buy & Hold Max Drawdown %: `25.96`
- Buy & Hold Calmar: `10.1504`
- Buy & Hold Start/End: `1275.81` -> `4637.99`
- Outperformance %: `-240.44`
- Calmar Delta: `-8.362`

## Performance Interpretation

This report separates the headline result from the mechanics that created it. A low win rate is not automatically a defect when the average win/loss ratio is high; the important question is whether the strategy preserves enough right-tail winners while reducing avoidable churn, weak sides, poor regimes, or expensive stop exits. Use the diagnostics below to decide the next full-whitebox mutation instead of guessing from the headline metrics alone.

## Production Gate

- Core failures: `['low_profit_factor', 'low_daily_sharpe', 'low_daily_sortino']`
- Portfolio / benchmark failures: `['weak_vs_buy_hold_benchmark']`
- Production sizing modes: `['fixed_notional_pct', 'fixed_risk_pct']`
- Benchmark policy: `outperform_return_or_calmar`

The platform-level rule is deliberately generic: first prove the strategy has enough activity, positive expectancy, bounded drawdown, acceptable daily portfolio Sharpe/Sortino/Calmar, bounded daily loss, and bounded per-trade risk; then judge it under a portfolio sizing model against buy-and-hold. Trade-level Sharpe/Sortino are diagnostic only and may overstate deployable portfolio quality. A strategy does not need to beat buy-and-hold on raw return if it delivers better drawdown-adjusted efficiency, but if it loses on both raw return and Calmar it is not production-comparable yet.

## Capital Model Warning

- fixed_risk_pct sizes each trade by stop distance; `0.005` means `0.5%` of current equity is the intended loss budget before leverage caps.

## Diagnostics

- Entries: `1331`
- Long signals: `638`
- Short signals: `707`
- Short quality gate blocks: `0`
- Breakeven stop moves: `0`
- Time risk filter blocks: `0`
- Stop exits: `362`
- Reverse exits: `0`
- Time-decay exits: `0`
- Time exits: `1`

## Side Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| long | 632 | 33968.09 | 1.316 | 39.4% | 568.08 | -280.64 | 21.12 |
| short | 699 | -10876.56 | 0.9117 | 34.33% | 467.76 | -268.28 | 14.82 |

## Exit-Reason Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| gann_state_exit | 968 | 162957.78 | 2.7955 | 50.52% | 518.85 | -189.47 | 22.36 |
| stop | 362 | -139767.2 | 0.0 | 0.0% | 0.0 | -386.1 | 5.7 |
| time_exit | 1 | -99.05 | 0.0 | 0.0% | 0.0 | -99.05 | 4.0 |

## Period Decomposition

| Segment | Trades | Net PnL | PF | Win Rate | Avg Win | Avg Loss | Avg Bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 20 | 2695.36 | 2.7356 | 55.0% | 386.21 | -172.55 | 24.35 |
| 2018 | 147 | -7698.29 | 0.6869 | 31.97% | 359.35 | -245.88 | 16.76 |
| 2019 | 154 | 60.41 | 1.0027 | 35.06% | 415.89 | -223.97 | 18.05 |
| 2020 | 162 | 1209.93 | 1.04 | 36.42% | 533.21 | -293.69 | 17.87 |
| 2021 | 161 | 2710.7 | 1.0907 | 34.16% | 592.44 | -281.82 | 17.28 |
| 2022 | 163 | 516.87 | 1.0185 | 39.88% | 437.9 | -285.17 | 18.39 |
| 2023 | 165 | 267.77 | 1.0101 | 36.97% | 439.42 | -255.16 | 16.31 |
| 2024 | 173 | 458.04 | 1.0144 | 34.1% | 548.27 | -279.74 | 16.62 |
| 2025 | 137 | 9968.85 | 1.4061 | 41.61% | 605.53 | -306.83 | 20.12 |
| 2026 | 49 | 12901.89 | 2.1684 | 42.86% | 1140.2 | -394.37 | 20.02 |

## Trade Duration

- 25th percentile bars held: `7.0`
- Median bars held: `15.0`
- 75th percentile bars held: `24.0`
- 90th percentile bars held: `37.0`
- 95th percentile bars held: `46.0`

## Excursion Diagnostics

- Average MFE/R: `1.2544`
- Average MAE/R: `-0.7`

MFE/R and MAE/R are decision-time diagnostic fields for full-whitebox research. They help identify whether losses had enough favorable movement for breakeven or trailing-stop logic, and whether winners required wide adverse movement that a tighter stop would have destroyed.

## Full-Whitebox Diagnostic Queue

Before testing a new rule mutation, inspect whether the weakness is side-specific, exit-specific, period-specific, duration-specific, or excursion-specific. Good next mutations should attack one localized defect while preserving the parent contract and the right-tail behavior that funds the strategy.