# StrategyLab XAU M30 run_f723d4f17c39 MT5 Translation Note

## Purpose

This EA/preset is a parity experiment for the StrategyLab parent:

`XAU test | BTC winner run_a871be4f8292 transplanted to XAU M30 | tuned atr_len=52, entry_mode=crossover_plus_pullback, fast_len=1, hybrid_reverse_exit_min_mfe_r=0...`

The StrategyLab run is `run_f723d4f17c39`, version `ver_cfbfb3577dd3`, on dataset `ds_4e109af56413`.

## StrategyLab Contract

- Symbol: `XAUUSD`
- Venue/data: `IC Markets MT5`
- Timeframe: `30m`
- Engine: `ma_cross_atr_stop_v1`
- Sizing mode: `mt5_fixed_risk_lot`
- Initial capital: `5000`
- Risk per trade: `0.01`
- Max leverage: `1.0`
- Contract size: `100`
- Min lot / lot step: `0.01 / 0.01`
- Skip below min lot: `true`
- Commission proxy: `commission_pct=0.0035`
- Slippage proxy: `slippage_ticks=10`, `tick_size=0.01`

The 5k account constraint is already part of the StrategyLab parent through `initial_capital=5000` and `sizing_mode=mt5_fixed_risk_lot`. MT5 still needs matching deposit/account settings in the tester, because live tester equity and broker lot constraints participate in the EA's lot calculation.

## Strategy Parameters

- MA kind: `sma`
- Fast / slow: `1 / 3`
- Entry mode: `crossover_plus_pullback`
- Noise lookback: `25`
- Max no-cross: `4`
- Allow long / short: `true / true`
- ATR length: `52`
- ATR stop multiplier: `3.3`
- Breakeven: enabled, trigger `0.25R`, lock `1.0R`
- Time decay: enabled, `10` bars, minimum `0.05R`
- Hybrid time-decay triage: enabled, checkpoint `30`, max unrealized `-1.0R`, max MFE `0.0R`
- Hybrid reverse-exit triage: enabled, min MFE `0.0R`
- Short quality gate: disabled
- Time-risk filter: disabled

## MT5 Files

- EA source: `StrategyLab-github/MT5/strategy_lab_ma_cross_atr_stop_xau_m30_run_f723d4f17c39.mq5`
- Preset: `StrategyLab-github/MT5/XAUUSD/backtesting/strategy_lab_ma_cross_atr_stop_xau_m30_run_f723d4f17c39.set`

## Expected StrategyLab Metrics

- Net PnL: `1,243,550,863.27`
- Profit factor: `2.9883`
- Max drawdown: `2.55%`
- Trades: `43,747`
- Expected payoff: `28,425.97`

## Parity Caveats

This is expected to be a directional parity candidate, not guaranteed numeric parity. The StrategyLab research engine uses bar-level fills, percentage commission, and synthetic slippage assumptions; MT5 uses broker tick economics, spreads, execution constraints, tester deposit, and real-tick modeling. The largest expected differences are fill price, spread/slippage, commission modeling, stop priority inside a bar, and lot rounding under `mt5_fixed_risk_lot`.

## Practical Test Setup

Use MT5 Strategy Tester with:

- Expert: `strategy_lab_ma_cross_atr_stop_xau_m30_run_f723d4f17c39`
- Symbol: `XAUUSD`
- Timeframe: `M30`
- Range: `2017.11.02` to `2026.05.01`
- Deposit: `5000`
- Leverage: close to `1:1` if the tester allows it, or keep `InpMaxLeverage=1.0` as the strategy cap
- Model: real ticks first, then OHLC/control points only as secondary diagnostics

The first acceptance check is not exact PnL parity. It is whether MT5 preserves side activity, trade frequency order of magnitude, PF direction, drawdown class, and whether deviations can be explained by execution mechanics rather than signal mismatch.
