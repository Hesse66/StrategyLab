# Hybrid-Blackbox Diagnostics - run_2579435b99a9

Source report: `artifacts/reports/run_2579435b99a9.md`

Whitebox diagnostics: `artifacts/diagnostics/full-whitebox-diagnostics-run_2579435b99a9.md`

Hybrid routing contract: `artifacts/diagnostics/hybrid-single-mutation-run_2579435b99a9.md`

Robustness context: `needs_review`; walk-forward `3/4`; cost stress `3/3`. The failed fold is `2022-02-02T11:00:00+00:00` to `2024-03-18T11:00:00+00:00`, with `low_daily_sortino`: Daily Sortino `0.7398` versus an approximate gate of `0.75`.

## 1. Frozen Whitebox Parent Contract

The frozen whitebox parent is `run_2579435b99a9`, family `xauusd_ghl_dc`, version `ver_9a0ca0f8616c`, stage `white_box`, verdict `promotion_candidate`. It trades `XAUUSD` on `IC Markets MT5`, timeframe `30m`, dataset `ds_4e109af56413`, with `100319` bars from `2017-11-02` through `2026-05-01`.

The engine is `ghl_dc_breakout_v1`. The execution style is long-only GHL+DC breakout continuation with ATR-bounded risk, Gann-state continuation exits, and a phase-3 UTC entry-hour filter. Side permissions are `allow_long=true`, `allow_short=false`. Live parameters are `gann_high_period=21`, `gann_low_period=13`, `donchian_length=55`, `max_breakout_bars=12`, `atr_len=34`, `stop_mode=atr`, `stop_mult=2.5`, `time_risk_filter_enabled=true`, `time_risk_block_utc_hours=[1,7,12,14,21]`, `time_risk_block_weekdays=[]`, `breakeven_stop_enabled=false`, `sizing_mode=fixed_risk_pct`, `risk_pct=0.01`, `max_leverage=1.0`, `commission_pct=0.0`, `slippage_ticks=10`, and `tick_size=0.01`.

The parent metrics are strong enough to freeze as the comparison object: net PnL `113504.68`, return `113.50%`, PF `1.5977`, max drawdown `5.17%`, expected payoff `129.57`, `876` trades, win rate `38.24%`, breakeven win rate `27.93%`, daily Sharpe `1.7114`, daily Sortino `1.9770`, worst daily return `-1.35%`, and Calmar `21.9339`. It underperforms buy and hold on raw return by `-150.03%`, but has a strong Calmar delta of `11.7835`.

## 2. Evidence Sufficiency

The evidence is sufficient to justify phase-4 diagnostics. The parent is not sample-starved: `876` trades over more than eight years is enough for an offline hybrid preview. The Markdown report contains the contract, metrics, parent comparison, side decomposition, exit decomposition, period decomposition, duration, MFE/MAE, and diagnostics. JSON is required for implementation-level trade rows and labels, not for deciding whether hybrid work is allowed.

The only caveat is that the current report does not directly export a modeling table. The first implementation step must therefore generate a trade-level feature export before any model is trusted.

## 3. Why Hybrid Is Justified or Not

Hybrid work is justified as a narrow research branch because the whitebox parent is alive and no obvious next hand-written rule remains. Phase 3 already tested or reasoned through the clear candidates: short-side removal happened in phase 2, UTC time-risk filtering survived and became the parent, breakeven stop management was rejected because it damaged Gann-state right-tail capture, and simple failed-entry triage was not supported by reconstructed early-progress evidence.

The parent is also not production-ready. The robustness gate returned `needs_review`: cost stress passed `3/3`, but walk-forward passed only `3/4`. The failed fold remains profitable, but its Daily Sortino is slightly below gate. That is exactly the kind of residual weakness a bounded hybrid quality layer can investigate. The hybrid is not being asked to rescue a dead strategy; it is being asked to sharpen a living parent at one decision point.

## 4. Whitebox Causal Identity

The strategy makes money through long-side breakout continuation with payoff asymmetry. Gann state supplies the trend-state spine. Donchian confirmation filters entries. The UTC time-risk filter avoids historically weak entry hours. ATR stops bound risk. Gann-state exits harvest the continuation tail.

This identity must remain intact. The hybrid model is not the strategy. It is allowed only to score otherwise-valid parent entries and veto a small low-quality slice. It may not create entries, replace Gann/Donchian logic, change stop placement, or alter exits.

## 5. Remaining Weakness to Solve

The remaining weakness is poor downside quality in a specific chronological slice, not full-history expectancy. The fold from `2022-02-02` to `2024-03-18` produced return `6.71%`, PF `1.1920`, `208` trades, max drawdown `5.00%`, daily Sharpe `0.7994`, Daily Sortino `0.7398`, and Calmar `1.3420`. It failed only the `low_daily_sortino` gate.

The entry-quality layer should try to identify entries that are likely to become poor R outcomes or low-quality failed breakouts. The target is not to maximize win rate. The target is to reduce downside clustering and improve Sortino while preserving the Gann-state winners that fund the strategy.

## 6. Ranked Hybrid Mutation Queue

**1. Entry-quality veto overlay.** This is the best first candidate. It acts at one decision point: after a valid whitebox entry signal and before order creation. It attacks low-quality entries without touching exits or stop management. It is also easiest to audit and easiest to translate into live-engine parameters if the offline preview survives.

**2. Entry setup-quality score for conservative sizing.** This would keep all trades but reduce size for weak scored entries. It is lower priority because the current capital model uses fixed risk and the first question is whether low-quality entries are separable at all. Sizing should wait until a score has evidence.

**3. Regime-context admission gate.** This could target 2018/2021/fold-3-like contexts, but the current evidence does not identify a causal regime variable. It should wait until entry-quality diagnostics reveal whether volatility, trend shape, or timing context is the actual driver.

**4. In-trade path triage.** This is a poor first hybrid candidate because simple whitebox early triage and breakeven already showed a dangerous tendency to cut future Gann-state winners. A hybrid path triage may eventually be useful, but it should not be first.

## 7. Chosen First Hybrid Role

Choose the entry-quality veto overlay.

The role is narrow: score a candidate entry and veto only the worst `10%` to `15%` of out-of-sample entries. The parent remains the strategy. The hybrid layer is a small admission gate for entry quality.

## 8. Feature Contract

All features must be known at the entry decision bar. The permitted feature families are:

- **Timing features:** UTC hour, weekday, month, and whether the signal is near a blocked UTC hour. These are known at entry and already matter to the parent.
- **Parent state features:** side, Gann state, breakout age, bars since Gann flip, Donchian breakout distance, and recent cross count. These describe the whitebox setup without using future outcomes.
- **Trend structure features:** Gann high/low SMA slopes, normalized distance to state line, recent return over prior bars, and recent range. These are computed from bars at or before entry.
- **Volatility/risk features:** ATR, ATR percent, stop distance, stop distance as ATR, initial risk percent, and entry exposure. These are known because the parent computes the stop and size at entry.
- **Local market context:** recent 20-bar return, recent 20-bar range, recent 20-bar realized volatility, and distance from recent high/low using only pre-entry bars.

Forbidden inputs are final PnL, exit reason, full-trade duration, future MFE/MAE, post-entry path, future fold performance, or any value computed after the entry decision.

## 9. Label Contract

The first label should be binary and conservative: `bad_entry_quality=true` when the trade later produced a poor realized outcome that the admission gate should have avoided. A defensible first label is:

`bad_entry_quality = net_pnl < 0 and mfe_r < 0.35`

This targets failed entries that both lost money and never achieved meaningful favorable excursion. It avoids labeling every losing trade as bad, because some losses may be acceptable costs of preserving the right tail. Time-exit failures may also be labeled bad, though this parent has only one time exit.

Ambiguous trades should remain in the training set as not-bad unless they meet the strict bad label. The first experiment should prefer false negatives over false positives because vetoing a future Gann-state winner is more expensive than allowing a normal failed attempt.

Outcome diagnostics should still retain continuous `net_pnl`, return on equity, MFE/R, MAE/R, bars held, and exit reason, but these are labels or diagnostics, not features.

## 10. Model Contract

Use the smallest transparent CPU-friendly model available. The first implementation may use the existing vanilla scorecard path, provided the output is interpreted as a diagnostic preview and not as a promoted model. A regularized logistic scorecard would be preferable if added later, but the first pass can use a deterministic scorecard trained on chronological train rows because it is dependency-free and auditable.

No deep learning, no GPU, no high-cardinality opaque model, and no model that predicts the whole market. The model output is only a bad-entry-quality score plus a veto threshold.

## 11. Validation Contract

Validation must be chronological. The parent to beat is frozen `run_2579435b99a9`. The first offline experiment should train on older trades, score later trades, and veto only validation/test trades. A random split is not acceptable.

The current app split is acceptable for a first smoke diagnostic if treated carefully: train through `2022`, validation through `2024`, and test from `2025` onward. Because the known weak fold overlaps `2022-02` to `2024-03`, the diagnostic report must break out validation-period performance and explicitly show whether the veto improved fold-3-like Sortino without damaging the 2025-2026 right tail.

Required comparison metrics are retained trade count, vetoed trade count, PF, net PnL, max drawdown, expected payoff, win rate, daily Sharpe, daily Sortino, worst daily return, Calmar, exit decomposition, period decomposition, and buy-and-hold comparison. The hybrid should also report what fraction of vetoes would have been Gann-state exits versus stops.

## 12. Acceptance Rule

Accept the offline preview only if it improves the parent in out-of-sample chronological evidence without deleting too much activity. Minimum acceptance:

- Retained trades stay at or above `75%` of parent activity, i.e. at least about `657` of `876` trades.
- Full-history or out-of-sample PF, net PnL, expected payoff, daily Sharpe, daily Sortino, and Calmar improve or remain materially comparable.
- Worst daily return does not worsen from `-1.35%`.
- The weak fold's Daily Sortino improves above the robustness gate without causing another fold to fail.
- Gann-state exit PnL is preserved; the veto should remove proportionally more stop/low-MFE failures than Gann-state winners.
- Cost-stress behavior remains acceptable after live-engine promotion.

The offline result is a candidate only. It does not become a promoted strategy until the live engine reproduces the edge.

## 13. Rejection Rule

Reject the preview if it improves PF by deleting too many trades, if it is only in-sample, if validation/test performance deteriorates, if it worsens max drawdown or worst daily return, or if it vetoes many future Gann-state winners. Reject immediately if feature leakage is discovered.

Reject it as a phase-4 branch if it cannot be converted into a small explicit live-engine rule or parameter set. A pretty offline score that cannot be run inside the actual backtest engine is a research artifact, not a mutation.

## 14. Live-Engine Promotion Contract

The offline gate and the live-engine gate are separate. If the offline entry-quality veto survives, the next implementation must add explicit parameters to the live strategy:

- `hybrid_entry_quality_enabled`
- `hybrid_entry_quality_threshold` or `hybrid_entry_quality_veto_fraction`
- a frozen scorecard/coefficient set
- diagnostic counters for `hybrid_entry_quality_vetoes`

The live engine must evaluate the score only at entry decision time, before order creation. It must expose the parameters in `mutation_space`, write diagnostics into reports, and rerun the same frozen dataset comparison against `run_2579435b99a9`. If the live implementation loses the offline edge, keep it disabled or reject it. If it survives, rerun the robustness gate.

## 15. Required Data Export

The first export should be one row per executed parent trade and should be saved as a diagnostic JSON/CSV. Each field must be classified by role:

Decision-time features:

- `entry_ts`, `year`, `month`, `weekday`, `utc_hour`
- `side`
- `entry_price`, `stop_price`, `stop_distance`, `stop_distance_atr`, `initial_risk_pct`, `entry_exposure_pct`
- `gann_state`, `donchian_breakout` or equivalent setup level
- `atr_pct`, `recent_return_20`, `recent_range_20`, `recent_volatility_20`
- `normalized_ma_distance`, available Gann/SMA slope fields, `recent_cross_count`

Labels:

- `bad_entry_quality`
- optional `low_mfe_failure`
- optional `negative_r_outcome`

Outcome diagnostics:

- `net_pnl`, `return_on_equity_pct`, `mfe_r`, `mae_r`, `bars_held`, `exit_reason`

Grouping keys:

- `run_id`, `family_id`, `version_id`, `dataset_id`, `trade_id`, chronological split/fold id

The export must not include future outcome fields as model features.

## 16. First Hybrid Experiment

Run the offline entry-quality veto experiment on `run_2579435b99a9`.

Main experiment:

- Mode: `offline_entry_quality_veto`
- Veto fraction: `0.15`
- Parent: `run_2579435b99a9`
- Dataset: `ds_4e109af56413`
- Label: `bad_entry_quality = net_pnl < 0 and mfe_r < 0.35`
- Model: vanilla scorecard or regularized logistic scorecard
- Split: chronological train/validation/test
- Primary question: does vetoing the worst-scored out-of-sample entries lift weak-fold Sortino while preserving full-history edge and Gann-state right tail?

Sensitivity run:

- Veto fraction: `0.10`

Do not implement a live engine mutation until the offline experiment report shows a real out-of-sample improvement.

## 17. Fallback Candidate If First Test Fails

If entry-quality veto fails, the next candidate is not an immediate live-engine hybrid. The fallback is a regime-context diagnostic focused on fold 3. It should test whether the weak fold can be explained by decision-time regime features such as ATR percentile, recent realized volatility, range compression, trend slope, or choppy cross count.

In-trade path triage remains lower priority because prior hand-rule tests suggest it can damage the right-tail continuation engine.

## 18. Final Routing

Proceed to the first hybrid experiment from the queue: offline entry-quality veto on `run_2579435b99a9`, with veto fractions `0.15` and `0.10`, chronological validation, and explicit reporting of weak-fold Sortino and Gann-state winner preservation.

Do not promote a hybrid branch, do not paper trade, and do not call the current parent production-ready until an offline survivor is converted into live-engine parameters, retested, and passed robustness.
