# Full-Whitebox Single-Mutation Brief 2 - run_0ce8106fd006

Source report: `artifacts/reports/run_0ce8106fd006.md`

Diagnostics memo: `artifacts/diagnostics/full-whitebox-diagnostics-run_0ce8106fd006.md`

Rejected prior preview: `artifacts/diagnostics/preview-breakeven-stop-run_0ce8106fd006.md`

Raw JSON was used only after the breakeven rejection to recover two missing diagnostic views: early in-trade progress at fixed bar checkpoints and entry-hour decomposition.

## 1. Frozen Parent Contract

The frozen parent remains `run_0ce8106fd006`, family `xauusd_ghl_dc`, version `ver_8557b530000c`, stage `white_box`, verdict `promotion_candidate`. It trades `XAUUSD` on `IC Markets MT5`, timeframe `30m`, dataset `ds_4e109af56413`, using `ghl_dc_breakout_v1`.

The parent is long-only after phase-2 optimization: `allow_long=true`, `allow_short=false`. Live parameters are `gann_high_period=21`, `gann_low_period=13`, `donchian_length=55`, `max_breakout_bars=12`, `atr_len=34`, `stop_mode=atr`, `stop_mult=2.5`, `sizing_mode=fixed_risk_pct`, `risk_pct=0.01`, `max_leverage=1.0`, `initial_capital=100000.0`, `commission_pct=0.0`, `slippage_ticks=10`, and `tick_size=0.01`.

The parent metrics are the comparison object: net PnL `90923.34`, return `90.92%`, profit factor `1.4079`, max drawdown `5.39%`, expected payoff `90.02`, total trades `1010`, win rate `37.33%`, breakeven win rate `29.73%`, daily Sharpe `1.4130`, daily Sortino `1.6192`, worst daily return `-1.35%`, Calmar `16.8553`, buy-and-hold outperformance `-172.61%`, and Calmar delta `6.7048`.

## 2. Current Causal Identity

The parent is a long-only XAUUSD M30 breakout continuation strategy. It makes money through payoff asymmetry, not hit rate. Gann-state exits harvest the right tail: `734` Gann-state exits earn `230713.98` with PF `3.7757`. ATR stops define failed breakout risk: `275` stop exits lose `-139507.01`.

The rejected breakeven preview clarified the identity further. The system cannot be treated as a generic stop-cleanup strategy. The first breakeven candidate converted many losses to near-flat exits, but reduced Gann-state exits from `734` to `565` and Gann-state PnL from `230713.98` to `189084.56`. The economic engine is right-tail continuation, and phase-3 mutations must avoid cutting trades merely because they look weak early.

## 3. Evidence Behind the Mutation

Breakeven was rejected because it damaged the engine: net PnL fell from `90923.34` to `78008.06`, expected payoff from `90.02` to `77.01`, daily Sharpe from `1.4130` to `1.3616`, and Calmar from `16.8553` to `15.3147`. Profit factor rose slightly, but that was not enough because the strategy lost right-tail value.

Failed-entry triage was checked next because the original diagnostics suggested it as the second queue item. Reconstructing checkpoints from JSON showed that simple no-progress rules are not justified. At checkpoints from 2 to 8 bars, rules like `mfe_r < 0.25` and unrealized `<= -0.25R` consistently saved some future stop damage but cut too many future Gann-state trades. For example, at 4 bars with `mfe_r < 0.25` and unrealized `<= -0.25R`, the rule would affect `96` trades: `23` future stops and `73` future Gann-state exits. The estimated net delta was `-8794.58`, not positive. At 8 bars with `mfe_r < 0.50` and unrealized `<= -0.25R`, the estimated delta was still negative at `-555.28`. This is not enough to justify coding failed-entry triage as the next active mutation.

Entry-hour decomposition provides a cleaner whitebox weakness. The worst UTC entry hours with at least 25 trades are:

| UTC Hour | Trades | Net PnL | PF | Win Rate |
|---:|---:|---:|---:|---:|
| 1 | 28 | -4431.00 | 0.5187 | 39.29% |
| 21 | 40 | -2625.38 | 0.7720 | 37.50% |
| 7 | 26 | -2166.98 | 0.5816 | 30.77% |
| 14 | 40 | -1578.51 | 0.8557 | 30.00% |
| 12 | 30 | -846.38 | 0.8804 | 33.33% |

Blocking only `[1, 7, 21]` would remove `94` trades and, before full re-simulation, leaves a retained subset of `916` trades, net PnL `100146.70`, and PF `1.5083`. Blocking `[1, 7, 14, 21]` removes `134` trades and leaves `876` trades, net PnL `101725.21`, and PF `1.5467`. Blocking `[1, 7, 12, 14, 21]` leaves `846` trades, net PnL `102571.59`, and PF `1.5731`, but that is more aggressive and should not be the first candidate.

The smallest defensible rule-family change is therefore an entry-time risk filter, not failed-entry triage.

## 4. Chosen Single Mutation

Implement a UTC entry-hour risk filter for `ghl_dc_breakout_v1`.

This is one rule family: before opening a new position, block entries whose signal occurs during configured UTC hours. It does not alter Gann/Donchian logic, stop mechanics, sizing, or exits. It targets evidenced weak entry contexts while preserving the continuation engine for all other hours.

The first candidate should block UTC hours `[1, 7, 21]`. This is conservative enough to avoid deleting too much evidence, but meaningful enough to test whether the hour weakness is structural. Hour `14` should be available in mutation space but not included in the first active candidate, because adding it increases aggressiveness from `94` blocked historical trades to `134`.

## 5. Why Competing Mutations Wait

Failed-entry triage waits because reconstructed checkpoint tests are negative. It saves some stop losses, but the future Gann-state trades it cuts cost more than the stops it avoids.

Further breakeven optimization waits because the first active breakeven rule failed the causal test. A later or higher-threshold breakeven ablation can be revisited only if new evidence shows it will not damage the Gann-state right tail.

A broad regime gate waits because the report still lacks a clean regime variable. Annual evidence is uneven, but not enough to define a volatility or trend filter without overfitting.

Phase 4 waits because there remains a simple explainable whitebox rule to test: entry-hour risk.

## 6. Implementation Brief

Add time-risk entry filtering to `ghl_dc_breakout_v1`.

Rule state:

- `time_risk_filter_enabled`
- `time_risk_block_utc_hours`
- optionally reuse existing `time_risk_block_weekdays` if already supported by shared UI/schema, but the first GHL+DC test should only use hours.

Evaluation timing:

- Evaluate only at entry decision time, after a valid Gann+Donchian long or short signal has formed and after side permission is checked.
- Use `bar.ts.hour` in UTC from the signal bar.
- If `time_risk_filter_enabled=true` and `bar.ts.hour` is in `time_risk_block_utc_hours`, cancel the entry signal for that bar.
- Do not close existing positions.
- Do not alter pending Gann/Donchian setup state beyond blocking that specific entry signal. The next independent signal may still enter if it occurs outside blocked hours.
- Apply the rule symmetrically in implementation, but the current parent is long-only.

Diagnostics/reporting:

- Increment `time_risk_filter_blocks` when a valid signal is blocked.
- Record blocked side counts if easy: `time_risk_filter_long_blocks`, `time_risk_filter_short_blocks`.
- Future reports should include entry-hour decomposition, because this mutation is now evidence-relevant.
- Existing saved child versions must inherit the new parameters without breaking previews.

## 7. New Parameters and Mutation Space

First active candidate:

```json
{
  "time_risk_filter_enabled": true,
  "time_risk_block_utc_hours": [1, 7, 21],
  "time_risk_block_weekdays": []
}
```

Mutation space:

```json
{
  "time_risk_filter_enabled": {
    "type": "bool",
    "values_only": [true, false],
    "default": true,
    "first_candidate": true
  },
  "time_risk_block_utc_hours": {
    "type": "list[int]",
    "values_only": [
      [],
      [1],
      [7],
      [21],
      [14],
      [1, 7],
      [1, 21],
      [7, 21],
      [1, 7, 21],
      [1, 7, 14, 21],
      [1, 7, 12, 14, 21]
    ],
    "default": [1, 7, 21],
    "first_candidate": [1, 7, 21]
  },
  "time_risk_block_weekdays": {
    "type": "list[int]",
    "values_only": [[]],
    "default": []
  }
}
```

## 8. First Unsaved Preview

Run an unsaved preview against the same frozen parent and dataset:

- Parent: `run_0ce8106fd006`
- Version: `ver_8557b530000c`
- Dataset: `ds_4e109af56413`
- Candidate: `time_risk_filter_enabled=true`, `time_risk_block_utc_hours=[1,7,21]`, `time_risk_block_weekdays=[]`

This first preview tests the rule itself. It should not include additional stop, Gann, Donchian, sizing, or side changes.

## 9. Post-Survival Optimization Plan

If `[1,7,21]` survives the full backtest comparison, run one evidence-aware optimization pass over only the new time-risk parameters. Test curated hour sets rather than arbitrary combinations, because unconstrained hour mining is overfit-prone.

Candidate hour sets should include `[]`, `[1]`, `[7]`, `[21]`, `[14]`, `[1,7]`, `[1,21]`, `[7,21]`, `[1,7,21]`, `[1,7,14,21]`, and `[1,7,12,14,21]`. The disabled state is allowed only as an ablation after the active candidate survives.

## 10. Acceptance Rule

Accept the mutation only if the full re-simulated child beats the frozen parent without collapsing evidence quality.

Minimum acceptance:

- Net PnL improves above `90923.34`.
- Profit Factor improves above `1.4079`.
- Max drawdown stays at or below `5.39%`, or any increase is very small and compensated by clear portfolio evidence.
- Expected payoff stays at or above `90.02`.
- Trade count remains high, preferably above `900` for the first candidate.
- Gann-state exit PnL and right-tail capture are preserved or improved.
- Daily Sharpe, Daily Sortino, worst daily return, and Calmar remain comparable or improve.
- Buy-and-hold Calmar advantage remains intact.
- Weak-hour removal does not simply shift losses into the remaining sessions or concentrate performance in one recent year.

## 11. Rejection Rule

Reject the mutation if it only wins by deleting too many trades, if trade count falls below acceptable evidence quality, if retained trades lose the right-tail Gann-state engine, if period decomposition worsens, or if the improvement exists only in the static trade filter estimate but disappears in full chronological re-simulation.

Reject it if the first candidate improves PF but reduces net PnL, expected payoff, daily Sharpe, or Calmar in the same pattern as the rejected breakeven rule.

## 12. Final Routing

Route: implement this one mutation as an unsaved preview.

Do not route to phase 4 yet. The breakeven mutation was rejected, failed-entry triage is not justified by reconstructed evidence, and the next auditable whitebox test is a UTC entry-hour risk filter.
