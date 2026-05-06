# StrategyLab MA Cross ATR Port: XAUUSD Probe

## Source Run

- StrategyLab run: `run_a871be4f8292`
- Source engine: `ma_cross_atr_stop_v1`
- Source asset/timeframe: `BTCUSDT`, Binance Spot, `15m`
- MT5 first target: `XAUUSD`, `M15`
- Status: port probe, not paper-trading candidate

## Frozen Parameters

- SMA fast/slow: `30 / 104`
- ATR: simple SMA of True Range, length `70`
- Stop: `ATR * 5.1`
- Entry: closed-bar SMA crossover only
- Anti-chop: price/fast-SMA crosses in `25` bars must be `<= 1`
- Longs: enabled
- Shorts: enabled
- Short quality gate: block shorts when close is below SMA `24960`
- Breakeven: enabled, trigger `0.25R`, lock `1.0R`
- Hybrid reverse triage: enabled, block reverse exit below `0.1R` MFE
- Hybrid time-decay triage: enabled at bar `30`; exit if unrealized `<= -0.45R` and MFE `<= 0.15R`
- Time decay: enabled at `40` bars if MFE `< 0.35R`
- Time risk filter: block UTC hours `13,15,21` and Python weekday `6` / Sunday
- Sizing: fixed risk, `1%` equity risk, max leverage `1.0`

## Files

- EA: `MT5/strategy_lab_ma_cross_atr_stop.mq5`
- Runner: `MT5/run_mt5_backtests_strategy_lab.ps1`
- Seed preset: `MT5/automation/strategy_lab_xauusd_m15_seed.set`

## First Backtest

Dry-run config generation:

```powershell
.\MT5\run_mt5_backtests_strategy_lab.ps1 -Symbol XAUUSD -Timeframe M15 -Window 1m -DryRun
```

Run first monthly window only:

```powershell
.\MT5\run_mt5_backtests_strategy_lab.ps1 -Symbol XAUUSD -Timeframe M15 -Window 1m -OnlyTag t01
```

Run the initial six monthly windows:

```powershell
.\MT5\run_mt5_backtests_strategy_lab.ps1 -Symbol XAUUSD -Timeframe M15 -Window 1m
```

Run four quarterly windows:

```powershell
.\MT5\run_mt5_backtests_strategy_lab.ps1 -Symbol XAUUSD -Timeframe M15 -Window 3m
```

## Interpretation Rules

This is an asset transfer probe. Do not compare raw XAU results to BTC headline PnL. Judge first by trade count, profit factor, drawdown, period distribution, and whether exits behave plausibly.

If M15 is too sparse or noisy, test `M30` and `H1` with the same frozen parameters before optimizing. Only open parameter mutation after a fixed-parameter run shows a survivable edge.

## Known Translation Difference

StrategyLab fills entries and close-based exits at the signal bar close. MT5 EAs can only place market orders when the EA receives ticks, so this port evaluates closed bars and acts on the next available tick. Treat this as expected execution-model drift during MT5 validation.

## First Smoke Result

- Date: `2026-05-01`
- Command: `.\MT5\run_mt5_backtests_strategy_lab.ps1 -Symbol XAUUSD -Timeframe M15 -Window 1m -OnlyTag t01`
- MT5 terminal result: tester started and finished successfully with exit code `0`.
- MetaEditor compile: `0 errors, 0 warnings`.
- Export note: the command-line tester did not leave an HTML report in `MT5/XAUUSD/reports/M15/PortProbe`; if HTML evidence is required, add the same UI export phase used in the GHL+DC/EMA Sniper runners.
