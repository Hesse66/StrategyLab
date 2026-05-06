# Full-Whitebox Single-Mutation Brief - run_0ce8106fd006

Source report: `artifacts/reports/run_0ce8106fd006.md`

Raw JSON was used only for exit-specific MFE/MAE evidence that the Markdown report did not include.

## 1. Frozen Parent Contract

The frozen parent is `run_0ce8106fd006`, family `xauusd_ghl_dc`, version `ver_8557b530000c`, stage `white_box`, verdict `promotion_candidate`.

Contract:

- Asset: `XAUUSD`
- Venue: `IC Markets MT5`
- Timeframe: `30m`
- Dataset: `ds_4e109af56413`
- Engine: `ghl_dc_breakout_v1`
- Entry style: GHL+DC breakout continuation, long-only after optimization
- Side permissions: `allow_long=true`, `allow_short=false`
- Costs: `commission_pct=0.0`, `slippage_ticks=10`, `tick_size=0.01`
- Sizing: `fixed_risk_pct`, `risk_pct=0.01`, `max_leverage=1.0`, `initial_capital=100000.0`
- Live parameters: `gann_high_period=21`, `gann_low_period=13`, `donchian_length=55`, `max_breakout_bars=12`, `atr_len=34`, `stop_mode=atr`, `stop_mult=2.5`

Parent metrics:

- Net PnL: `90923.34`
- Return: `90.92%`
- Profit Factor: `1.4079`
- Max Drawdown: `5.39%`
- Expected Payoff: `90.02`
- Total Trades: `1010`
- Win Rate: `37.33%`
- Breakeven Win Rate: `29.73%`
- Daily Sharpe: `1.4130`
- Daily Sortino: `1.6192`
- Worst Daily Return: `-1.35%`
- Calmar: `16.8553`
- Buy and Hold Net PnL: `263532.97`
- Buy and Hold Return: `263.53%`
- Buy and Hold Max Drawdown: `25.96%`
- Buy and Hold Calmar: `10.1504`
- Outperformance: `-172.61%`
- Calmar Delta: `6.7048`

The parent beats buy and hold on drawdown-adjusted evidence, but not on absolute return.

## 2. Current Causal Identity

The parent is no longer a generic translated GHL+DC strategy. After phase-2 tuning it is a long-only, controlled-risk breakout continuation system on XAUUSD M30. It appears to make money by taking many long breakout attempts, letting the Gann-state exit harvest continuation winners, and using ATR stops to cap failed breakouts.

The identity is not high win-rate mean reversion. It is a positive payoff-asymmetry system: win rate is only `37.33%`, but average win/loss ratio is `2.3639`, above the breakeven requirement. The engine depends on preserving right-tail capture from Gann-state exits.

## 3. Evidence Behind the Mutation

The clearest weakness is not entry frequency, side selection, or a missing ordinary parameter. It is failed-breakout stop handling.

From the report:

- `gann_state_exit`: `734` trades, net PnL `230713.98`, PF `3.7757`, win rate `51.36%`, avg bars `20.43`
- `stop`: `275` trades, net PnL `-139507.01`, PF `0.0`, avg loss `-507.30`, avg bars `4.83`
- `time_exit`: `1` trade, net PnL `-283.63`

The profitable engine is concentrated in Gann-state exits. The loss bucket is concentrated in stop exits, and stop exits happen quickly.

JSON evidence adds the missing excursion detail:

- Stop exits had avg `mfe_r=0.4844`, median `mfe_r=0.3096`
- `57.1%` of stop exits reached at least `0.25R` MFE
- `33.8%` reached at least `0.50R` MFE
- `21.1%` reached at least `0.75R` MFE
- only `12.4%` reached at least `1.00R` MFE
- `67.3%` of stop exits closed within `5` bars; `86.2%` within `8` bars

This supports a conservative MFE-activated stop-management mutation. It does not support a broad time-decay rule as the first mutation, because the main loss bucket often fails too quickly for a late time rule.

## 4. Chosen Single Mutation

Implement a long-only MFE-activated breakeven/profit-lock stop for `ghl_dc_breakout_v1`.

The rule family is stop management, not parameter retuning. Once a trade reaches a configurable favorable excursion in R units, move the active stop from its original ATR stop to at least entry plus a configurable locked-R amount. For long trades:

`new_stop = max(current_stop, entry_price + initial_risk_per_unit * breakeven_lock_r)`

The first candidate should be active, conservative, and designed to test whether protecting partial favorable excursion improves stop-exit damage without cutting the Gann-state right tail.

## 5. Why Competing Mutations Wait

Time-decay exits wait because stop losers are usually early failures: `67.3%` of stop exits are done within `5` bars and `86.2%` within `8` bars.

Regime or session filters wait because the report does not provide enough hour/day/regime decomposition to prove the smallest useful filter.

Re-enabling shorts waits because phase-2 already selected `allow_short=false`, and the frozen parent has zero short trades.

Gann, Donchian, ATR length, and stop multiplier retuning waits because phase 3 is not another ordinary parameter sweep.

Aggressive trailing stop waits because the parent's strongest evidence comes from right-tail Gann-state exits, and a broad trail could harvest cosmetic win-rate improvements while damaging payoff asymmetry.

## 6. Implementation Brief

Add breakeven/profit-lock stop management to `ghl_dc_breakout_v1`.

Rule state:

- `breakeven_stop_enabled`
- `breakeven_trigger_r`
- `breakeven_lock_r`
- per-position state: whether the breakeven stop has been armed/moved

Evaluation timing:

- Evaluate only after entry, on each subsequent bar, using data available up to that bar.
- For long trades, compute current favorable excursion from bar high versus entry price.
- Convert favorable excursion to R using the initial per-unit risk from entry to original stop.
- If `mfe_r >= breakeven_trigger_r`, move the active stop to at least entry plus `breakeven_lock_r * initial_risk_per_unit`.
- Never loosen the stop.
- Preserve existing Gann-state exit behavior; the breakeven stop only changes the stop floor.

Reporting requirements:

- Count `breakeven_stop_moves`.
- Distinguish exits hit after breakeven movement, either as `breakeven_stop` or by recording `stop_was_breakeven=true`.
- Include exit decomposition for normal ATR stops versus breakeven/profit-lock stops.
- Include MFE/MAE by exit reason in future diagnostics.
- Existing saved child versions must inherit defaults without breaking previews.

## 7. New Parameters and Mutation Space

First candidate defaults should make the rule active:

```json
{
  "breakeven_stop_enabled": true,
  "breakeven_trigger_r": 0.75,
  "breakeven_lock_r": 0.0
}
```

Mutation space:

```json
{
  "breakeven_stop_enabled": {
    "type": "bool",
    "values_only": [true, false],
    "default": true,
    "first_candidate": true
  },
  "breakeven_trigger_r": {
    "type": "float",
    "search_min": 0.50,
    "search_max": 1.50,
    "search_step": 0.25,
    "default": 0.75
  },
  "breakeven_lock_r": {
    "type": "float",
    "search_min": 0.0,
    "search_max": 0.50,
    "search_step": 0.10,
    "default": 0.0
  }
}
```

The optimizer may later test disabled state only after the active rule candidate has produced evidence.

## 8. First Unsaved Preview

Run an unsaved preview against the exact frozen parent and dataset:

- Parent: `run_0ce8106fd006`
- Dataset: `ds_4e109af56413`
- Active candidate: `breakeven_stop_enabled=true`, `breakeven_trigger_r=0.75`, `breakeven_lock_r=0.0`

This is intentionally not a broad search. It tests whether the rule itself has a defensible effect before tuning.

## 9. Post-Survival Optimization Plan

If the first preview survives, run one evidence-aware optimization pass over only the new rule parameters:

- `breakeven_trigger_r`: `0.50`, `0.75`, `1.00`, `1.25`, `1.50`
- `breakeven_lock_r`: `0.0`, `0.10`, `0.20`, `0.30`, `0.40`, `0.50`
- `breakeven_stop_enabled`: include `false` only as a post-survival ablation

Judge candidates on full-history comparison, not isolated trade-level cosmetics.

## 10. Acceptance Rule

Accept the mutation only if it improves the frozen parent without degrading evidence quality.

Minimum acceptance:

- Net PnL improves or remains close while max drawdown improves meaningfully.
- Profit Factor improves above `1.4079` without collapsing trade count.
- Max drawdown stays below or improves from `5.39%`.
- Expected payoff does not materially degrade from `90.02`.
- Trade count remains high enough for evidence quality; do not accept a result that wins by deleting most trades.
- Gann-state exit profitability is not materially damaged.
- The stop-exit loss bucket shrinks in net loss or average loss.
- Daily Sharpe, Daily Sortino, worst daily return, and Calmar remain at least comparable to the parent.
- Buy-and-hold drawdown advantage is preserved.
- No future data is used.

Production-grade routing still requires chronological walk-forward folds and cost stress: doubled commission, doubled slippage, and combined doubled execution costs.

## 11. Rejection Rule

Reject the mutation if it improves one headline metric while damaging the causal engine.

Kill conditions:

- Trade count collapses or evidence becomes low-sample.
- Gann-state exit net PnL or right-tail capture is materially reduced.
- Profit Factor rises only because the strategy exits too early and sacrifices payoff asymmetry.
- The stop-loss bucket improves but yearly/period decomposition hides shifted losses.
- Daily portfolio metrics worsen materially.
- Worst daily return worsens beyond the parent.
- The rule depends on intrabar knowledge unavailable to MT5 backtest execution assumptions.
- Disabled breakeven beats every active candidate in a fair post-survival ablation.

## 12. Final Routing

Route: implement this one mutation as an unsaved preview.

The parent is a credible promotion candidate, but not production-ready. Before any production-readiness language, it must pass the Mutation Lab robustness gate: chronological walk-forward folds and execution-cost stress scenarios.
