# Full-Whitebox Single-Mutation Handoff for run_a871be4f8292

## 1. Frozen Parent Contract

The frozen parent is `run_a871be4f8292`, family `btc_intraday`, dataset `ds_d14d74e36d0d`, engine `ma_cross_atr_stop_v1`, asset `BTCUSDT`, venue `Binance Spot`, timeframe `15m`, stage `white_box`, verdict `promotion_candidate`. The report and raw artifact establish coverage from `2017-08-17 04:00 UTC` through `2026-04-21 19:45 UTC`, with `303723` bars in the equity/risk artifact and `764` executed trades.

The entry engine is SMA crossover-only with `fast_len=30`, `slow_len=104`, `noise_lookback=25`, and `max_no_cross=1`. Both sides are allowed. Risk uses `atr_len=70`, `stop_mult=5.1`, `sizing_mode=fixed_risk_pct`, `risk_pct=0.01`, `max_leverage=1.0`, `initial_capital=100000`, `commission_pct=0.04`, `slippage_ticks=2`, and `tick_size=0.01`.

The parent is already managed by several whitebox/hybrid layers: breakeven stop at `0.25R` with `1.0R` lock, time-decay exit at `40` bars with minimum MFE/R `0.35`, short quality gate `block_below_sma`, time-risk filter blocking UTC hours `[13,15,21]` and weekday `[6]`, hybrid time-decay triage at checkpoint `[30]`, and hybrid reverse-exit triage.

The metrics to beat are strong: net PnL `5902450.78`, return `5902.45%`, profit factor `4.4681`, max drawdown `3.87%`, expected payoff `7725.72`, total trades `764`, win rate `75.65%`, daily Sharpe `5.9811`, daily Sortino `3.6352`, worst daily return `-2.06%`, Calmar `1525.0041`, buy-and-hold return `1637.47%`, and outperformance `4264.98%`.

## 2. Current Causal Identity

The parent has drifted from a plain moving-average trend strategy into a short-cycle managed-trade system. The SMA cross remains the admission engine, but the realized edge comes from trade management: breakeven movement, locked stop behavior, time-risk filtering, side gating, and failed-entry triage. This identity drift is acceptable because it is causal and explainable, but it must be protected.

The key identity point is that `stop` exits are not a damage bucket here. They are the profit engine: `626` stop exits generated `6430190.44` net PnL, PF `6.9995`, and win rate `89.62%`. A mutation that weakens this stop-managed engine would be attacking the strategy's core.

## 3. Evidence Behind the Mutation

The `03-1` diagnostics artifact for this run localizes the obvious remaining whitebox weakness in failed-entry time management. The two time-failure exit buckets lose money in isolation: `time_decay` has `99` trades, `-311480.01` net PnL, PF `0.041`, and win rate `16.16%`; `hybrid_time_decay_triage` has `28` trades, `-273937.97` net PnL, PF `0.0`, and win rate `0.0%`. Together they lose about `585417.98`.

The evidence does not justify deleting time-decay exits outright. These exits may be protective, closing trades that would have become larger losses. The smallest useful mutation is therefore not removal; it is a confirmation gate that makes failed-entry closure more selective using decision-time state.

## 4. Chosen Single Mutation

Implement one rule-family mutation: **failed-entry time-decay confirmation gate**.

The new rule should activate only when an existing time-decay or hybrid time-decay exit is about to close a trade. It should confirm the exit only if the trade is still weak at decision time, using available state such as unrealized R, MFE/R so far, bars held, side, current fast/slow MA relationship, recent cross count, and breakeven-stop state. The first test should be active, conservative, and easy to reject: confirm failed-entry closure only when unrealized R remains at or below `0R` and MFE/R has not exceeded roughly the parent `time_decay_min_mfe_r=0.35`.

## 5. Why Competing Mutations Wait

Side removal waits because both sides are strong. Longs produced `3748632.6` net PnL with PF `4.478`; shorts produced `2153818.18` with PF `4.4511`. The short quality gate already removes many weak short contexts and the surviving short side is useful.

Stop changes wait because stop exits are the dominant profit engine. Tightening, loosening, or relabeling the stop logic before failed-entry exits are understood would risk damaging the strongest behavior in the parent.

Additional time-risk filters wait because the report does not expose remaining hour expectancy. The current filter already blocks `244` entries. More blocked hours without hour-level evidence would be guesswork.

Phase-4 hybrid work waits because there is still an obvious explainable whitebox weakness in time-failure exits, and the parent already includes hybrid-named overlays. The next improvement should cleanly test the whitebox exit-management question first.

## 6. Implementation Brief

Add a rule state named `time_decay_triage_confirmation_enabled`. It is evaluated inside the exit-management path, after the existing time-decay or hybrid time-decay logic has identified a candidate time-failure exit, but before the trade is actually closed. It must not affect normal stop exits, reverse exits, entries, side permissions, sizing, ATR stop placement, breakeven movement, or time-risk entry filtering.

At decision time, the rule may read current bar timestamp, side, bars held, entry price, current close, current stop, current unrealized R, MFE/R so far, MAE/R so far, fast SMA, slow SMA, fast-minus-slow, normalized MA distance, recent cross count, and whether a breakeven stop move has already occurred. It may not read final trade PnL, final exit reason, future MFE/MAE, future bars, or post-exit labels.

If `time_decay_triage_confirmation_enabled=false`, behavior must remain exactly the same as the frozen parent. If enabled, candidate time-decay exits are confirmed only when the confirmation conditions pass. If they do not pass, the position remains open and exits later through the existing stop/reverse/time-decay logic.

Reports should add diagnostics for:

| Counter | Meaning |
|---|---|
| `time_decay_confirmation_candidates` | Existing time-decay/hybrid candidates inspected by the confirmation gate. |
| `time_decay_confirmation_exits` | Candidate exits confirmed and executed. |
| `time_decay_confirmation_suppressed` | Candidate exits suppressed because confirmation failed. |
| `time_decay_confirmation_suppressed_net_pnl` | Later net PnL of trades whose candidate exit was suppressed. |

Future reports should decompose these counters by side, year, and original candidate reason.

## 7. New Parameters and Mutation Space

Expose the new controls as active first-test candidates:

| Lever | Path | First Value | Search Metadata | Rationale |
|---|---|---:|---|---|
| `time_decay_triage_confirmation_enabled` | `parameters.time_decay_triage_confirmation_enabled` | `true` | `values_only: [true,false]` | Enable the rule family for the first preview. |
| `time_decay_confirm_max_unrealized_r` | `parameters.time_decay_confirm_max_unrealized_r` | `0.0` | `search_min=-1.0`, `search_max=0.5`, `search_step=0.05` | Candidate exit is confirmed only if the trade is still weak in unrealized R. |
| `time_decay_confirm_max_mfe_r` | `parameters.time_decay_confirm_max_mfe_r` | `0.35` | `search_min=0.0`, `search_max=1.0`, `search_step=0.05` | Avoid closing trades that already proved favorable excursion. |
| `time_decay_confirm_require_no_breakeven_move` | `parameters.time_decay_confirm_require_no_breakeven_move` | `false` | `values_only: [false,true]` | Optional guard for trades already managed by breakeven. |

Existing saved versions must inherit defaults without breaking previews. Defaults should preserve old behavior only when the rule is disabled; the first candidate in this research path should explicitly enable the rule.

## 8. First Unsaved Preview

Run an unsaved preview against the same frozen parent and dataset `ds_d14d74e36d0d` with only this rule family changed:

```json
{
  "time_decay_triage_confirmation_enabled": true,
  "time_decay_confirm_max_unrealized_r": 0.0,
  "time_decay_confirm_max_mfe_r": 0.35,
  "time_decay_confirm_require_no_breakeven_move": false
}
```

The preview should compare directly against `run_a871be4f8292`. It should not re-optimize MA lengths, ATR length, stop multiplier, time-risk hours, side permissions, or sizing. The goal is to test whether the rule itself deserves to exist.

## 9. Post-Survival Optimization Plan

If the first preview survives, optimize only the new rule parameters for one or two passes. Candidate search should prioritize enough trades, net PnL, profit factor, max drawdown, expected payoff, daily Sharpe/Sortino, worst daily return, Calmar, annual breadth, side balance, exit decomposition, duration behavior, MFE/MAE behavior, and buy-and-hold comparison.

After survival, allowing the optimizer to disable `time_decay_triage_confirmation_enabled` is valid only if the disabled state wins under the same evidence comparison. Do not use a broad `Optimize all` pass until the rule family has either survived or been rejected.

## 10. Acceptance Rule

Accept the mutation only if it improves the frozen parent without damaging evidence quality. It should preserve roughly the `764`-trade evidence base, keep max drawdown near or below `3.87%`, avoid worsening worst daily return beyond `-2.06%`, preserve both long and short strength, and not materially reduce the profitable stop-exit engine.

The best evidence of survival would be improved net PnL or daily Sortino/Calmar, reduced losses in `time_decay` and `hybrid_time_decay_triage`, positive or improved later outcomes for suppressed time-failure exits, and no annual-period concentration. Because the parent is already extremely strong, modest portfolio-quality improvement is enough; raw PF improvement alone is not enough.

## 11. Rejection Rule

Reject the mutation if it only wins by deleting or delaying trades, if suppressed exits become larger later losses, if max drawdown or worst daily return worsens materially, if the stop-exit bucket loses its role as the profit engine, if either side is damaged, if gains concentrate in one or two recent years, or if the implementation uses unavailable future information.

Also reject it if the rule merely relabels losing `time_decay` exits into later `stop` exits while total portfolio metrics do not improve.

## 12. Final Routing

Implement this one mutation as an unsaved preview. Do not promote the child, do not run broad parameter optimization, and do not route to phase 4 until the active failed-entry time-decay confirmation gate is tested against the frozen parent and either survives or is rejected.
