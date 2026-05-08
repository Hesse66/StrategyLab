# MT5 Gap Review for run_f723d4f17c39

## MT5 Full-Period Result Reviewed

- Report: `C:\Users\G3_Mb\OneDrive\Documentos\Trading\AutoXAU\MT5\XAUUSD\reports\M30\StrategyLab_MA_XAU_run_f723d4f17c39\xauusd_m30_full_2017-11-02_2026-05-01_t01.html`
- Expert: `strategy_lab_ma_cross_atr_stop_xau_m30_run_f723d4f17c39`
- Symbol/timeframe: `XAUUSD` / `M30`
- Initial deposit: `5000`
- Loaded inputs: matched the StrategyLab parent defaults for `run_f723d4f17c39`.

## MT5 Result

- Net profit: `-3,375.02`
- Profit factor: `0.88`
- Equity drawdown maximal: `3,513.59 (68.50%)`
- Total trades: `16,732`
- Short trades: `8,379`
- Long trades: `8,353`

## StrategyLab Reference

- Net PnL: `1,243,550,863.27`
- Profit factor: `2.9883`
- Max drawdown: `2.55%`
- Total trades: `43,747`
- Stop exits: `14,351`
- Reverse exits: `29,395`
- Breakeven stop moves: `15,229`

## Root-Cause Reading

The MT5 run did not fail because the preset failed to load. The inputs did load. The gap is mainly a simulation-model gap.

The StrategyLab parent is extremely dependent on bar-level stop management. In the StrategyLab report, stop exits are the main profit source: `1,814,299,859.62` net PnL with PF `67.0953` and win rate `98.1%`. That is not normal behavior for an initial ATR stop; it means most profitable stop exits are stop-managed exits after breakeven/lock movement.

The MT5 EA uses real broker-side stop loss behavior. The initial stop is live immediately after entry, and breakeven can only be modified when the EA processes ticks/new bars. The StrategyLab engine, by contrast, evaluates positions at bar level, tracks MFE/MAE from completed bars, and applies its own stop logic using synthetic fills and slippage. That bar-level accounting can be directionally useful for research, but it is not equivalent to an MT5 real-tick EA with live stops.

The drop from `43,747` StrategyLab trades to `16,732` MT5 trades is consistent with the same issue. Once MT5 takes real stop losses and equity falls, the 5k `mt5_fixed_risk_lot` model produces more skipped or reduced activity, so the later trade population no longer resembles the StrategyLab run.

## Practical Conclusion

This high-PnL parent should not be treated as live-translated by the current MT5 EA. The StrategyLab result is a useful case study, but the MT5 result says the edge does not survive a live-like stop execution model in its current form.

Two different next experiments are possible:

1. `research_parity_proxy`: build an MT5 EA mode with virtual, closed-bar-managed stops to approximate StrategyLab's bar-level accounting. This can help audit signal parity, but it is not a live-trading candidate by itself.
2. `live_like_repair`: keep MT5 real stops and return to StrategyLab/Mutation Lab with a tick-safe/live-stop constraint, then search for a parent whose edge survives actual broker stop behavior.

For production relevance, prefer `live_like_repair`. For debugging the research engine gap, use `research_parity_proxy`.
