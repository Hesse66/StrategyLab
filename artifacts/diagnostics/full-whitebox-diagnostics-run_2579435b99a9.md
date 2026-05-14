# Full-Whitebox Diagnostics - run_2579435b99a9

Source report: `artifacts/reports/run_2579435b99a9.md`

Raw JSON was used only to recover row count, exact date coverage, first/last trade timestamps, exit-specific MFE/MAE, and the remaining entry-hour/weekday decompositions after the time-risk filter. The Markdown report contains the research contract and is sufficient for the main diagnosis.

## 1. Frozen Parent Contract

The frozen parent is `run_2579435b99a9`, family `xauusd_ghl_dc`, version `ver_9a0ca0f8616c`, stage `white_box`, verdict `promotion_candidate`. It trades `XAUUSD` on `IC Markets MT5`, timeframe `30m`, using dataset `ds_4e109af56413`. The equity curve contains `100319` bars from `2017-11-02T07:00:00+00:00` through `2026-05-01T19:00:00+00:00`. The first recorded trade opens at `2017-11-09T22:00:00+00:00`; the last closes at `2026-05-01T19:00:00+00:00`.

The engine is `ghl_dc_breakout_v1`, now a long-only GHL+DC breakout continuation system with an explicit phase-3 UTC entry-hour risk filter. Live parameters are `allow_long=true`, `allow_short=false`, `gann_high_period=21`, `gann_low_period=13`, `donchian_length=55`, `max_breakout_bars=12`, `atr_len=34`, `stop_mode=atr`, `stop_mult=2.5`, `breakeven_stop_enabled=false`, `time_risk_filter_enabled=true`, `time_risk_block_utc_hours=[1,7,12,14,21]`, `time_risk_block_weekdays=[]`, `sizing_mode=fixed_risk_pct`, `risk_pct=0.01`, `max_leverage=1.0`, `initial_capital=100000.0`, `commission_pct=0.0`, `slippage_ticks=10`, and `tick_size=0.01`.

This parent defines its evidence with `876` trades, net PnL `113504.68`, return `113.50%`, profit factor `1.5977`, max drawdown `5.17%`, expected payoff `129.57`, win rate `38.24%`, breakeven win rate `27.93%`, daily Sharpe `1.7114`, daily Sortino `1.9770`, worst daily return `-1.35%`, Calmar `21.9339`, average entry exposure `99.64%`, and max initial risk `1.0%`.

Against buy and hold, the strategy still does not win on raw return: buy and hold earns `263532.97`, return `263.53%`, max drawdown `25.96%`, and Calmar `10.1504`. The strategy underperforms buy and hold by `-150.03%` on raw return but beats it decisively on drawdown-adjusted efficiency, with Calmar delta `11.7835`.

## 2. Evidence Sufficiency

The report is sufficient for phase-3 diagnosis. It includes the frozen contract, parent comparison, headline metrics, buy-and-hold comparison, side decomposition, exit-reason decomposition, period decomposition, duration statistics, and aggregate MFE/MAE. The sample remains large enough for full-whitebox reasoning: `876` trades across more than eight years of M30 data. This is not a fragile tiny-sample result.

JSON was useful for missing decompositions, not for replacing the report. The report should be upgraded later to include entry-hour decomposition and exit-specific MFE/MAE directly, because both were important in this phase-3 sequence.

## 3. Edge Statement

The edge is still payoff asymmetry and right-tail continuation, now improved by timing selectivity. The strategy does not win because it predicts most trades correctly. Its win rate is `38.24%`, but that is comfortably above the `27.93%` breakeven win rate implied by the average win/loss ratio of `2.5802`.

The money comes from long breakout attempts that survive into Gann-state exits. `gann_state_exit` now contributes `647` trades, net PnL `230247.99`, PF `4.1476`, and win rate `51.78%`. Stops remain the cost of failed breakouts: `228` stop exits lose `-116426.13`. The time-risk filter improved the parent by refusing entry during historically weak UTC hours, not by changing the continuation engine after entry.

## 4. Identity Drift Check

The strategy has drifted in a controlled and explainable way. It began as a translated GHL+DC long/short breakout concept, then became a long-only optimized XAUUSD breakout continuation parent, and now has a phase-3 entry-time risk layer. This drift is acceptable because every change preserved the causal spine: Gann state, Donchian confirmation, ATR-bounded risk, and Gann-state continuation exits.

The current identity is best described as a long-only, timing-filtered XAUUSD M30 breakout continuation strategy. It is not a mean-reversion strategy, not a high-hit-rate scalper, and not a generic ML veto system.

## 5. Diagnostic Evidence

Parent comparison is favorable. Relative to `run_0ce8106fd006`, the saved child improves profit factor by `0.1898`, net PnL by `22581.34`, drawdown by `-0.22` percentage points, and reduces trade count by `134`. This is not merely a cosmetic PF improvement: net profit, payoff, daily Sharpe, daily Sortino, and Calmar all improved in the preview and are reflected in the saved run.

Side decomposition is clean. The parent is entirely long-side: `876` long trades, net PnL `113504.68`, PF `1.5977`, win rate `38.24%`, average win `905.67`, average loss `-351.00`, and average duration `16.47` bars. There are zero short trades because phase-2 already rejected short participation.

Exit decomposition shows the economic engine and the remaining cost. Gann-state exits make almost all the money: `647` exits, net PnL `230247.99`, PF `4.1476`, average bars `20.63`. Stops are still a large negative bucket: `228` exits, net PnL `-116426.13`, average loss `-510.64`, average bars `4.73`. Time exit is irrelevant structurally: one trade, `-317.18`.

JSON exit-specific excursion confirms why stop repair remains tricky. Gann-state exits have average `mfe_r=1.7215`, median `mfe_r=1.1481`, average `mae_r=-0.4560`, and median `mae_r=-0.4326`. Stop exits have average `mfe_r=0.4497`, median `mfe_r=0.3080`, average `mae_r=-1.4021`, and median `mae_r=-1.2260`. Stops are still expensive, but prior breakeven and early-triage evidence showed that simple stop cleanup can damage the Gann-state right tail.

Period decomposition is much healthier than the earlier parent. 2018 remains negative at `-2259.07`, and 2021 is only slightly positive at `590.83`, but every other year is positive. The strongest periods are 2025 at `45101.34` and 2026 at `27527.63`, yet the strategy is not a one-year artifact: 2017, 2019, 2020, 2022, 2023, and 2024 are also positive.

Remaining timing decomposition no longer presents an obvious single-rule weakness. After blocking UTC hours `[1,7,12,14,21]`, all active weekdays are positive. The weakest active weekday is Wednesday with `181` trades, net PnL `6691.92`, PF `1.1646`. Remaining entry hours with at least `20` trades are also positive. Some have modest PF, such as hour `17` with `97` trades, net PnL `3165.50`, PF `1.1330`, and hour `11` with `48` trades, net PnL `2474.52`, PF `1.2559`, but they are not clear loss pockets.

Duration remains consistent with the stated identity. Median bars held is `13`, 75th percentile `22`, 90th percentile `34`, and 95th percentile `43`. The strategy is still a short-to-medium continuation system.

## 6. Failure Localization

The remaining obvious failure is not side selection or time-of-day selection. Shorts are already absent, and the weak UTC hours have been filtered. The remaining stop bucket is still large, but it is no longer an obvious whitebox mutation target because the first breakeven mutation already failed and reconstructed early-progress triage was negative. Those experiments showed that the system's future winners often look fragile early enough that aggressive trade management can remove the trades that fund the strategy.

The main unresolved weakness is robustness, not another simple rule. The parent still underperforms buy and hold on raw return, depends materially on 2025-2026 for its strongest compounding, and has not yet been subjected to walk-forward folds or execution cost stress after the time-risk mutation. Those are validation problems before they are strategy-logic problems.

## 7. Rival Explanations

One rival explanation is that the time-risk filter overfit entry hours in this dataset. This is plausible and must be tested with chronological walk-forward and cost stress. It is not resolved by adding another whitebox rule.

Another rival explanation is that the remaining stop bucket can still be repaired by a more subtle stop-management rule. That may eventually be true, but the evidence does not justify the next full-whitebox mutation now. The rejected breakeven preview improved stop optics while reducing net PnL, expected payoff, daily Sharpe, and Calmar. The reconstructed failed-entry triage checks also produced negative estimated deltas. A more subtle version would need richer path diagnostics or hybrid scoring rather than another simple hand rule.

A third rival explanation is that 2018 and 2021 reveal a regime weakness. The report only gives calendar-year evidence, not a causal regime variable. Turning that into a volatility or trend filter now would be guesswork.

## 8. Mutation Queue

There is no high-confidence next whitebox mutation to implement immediately.

The first queued idea is not an implementation but a validation step: run the Mutation Lab robustness gate on `ver_9a0ca0f8616c`. The hypothesis is that the time-risk filtered parent is genuinely stronger, not just a full-history hour overfit. It must preserve acceptable performance across chronological folds and under doubled commission, doubled slippage, and combined execution cost stress.

The second queued idea is a phase-4 hybrid overlay, not another whitebox rule. The target would be a narrow decision-time-safe filter for the remaining difficult cases: low-quality entries or early path states that a simple rule cannot separate without damaging Gann-state winners. The prior breakeven and early-triage failures are exactly the kind of evidence that supports a careful hybrid layer later.

The third queued idea is a regime diagnostic, not a mutation. If robustness or phase-4 diagnostics show that 2018/2021/2024-like conditions are systematically different, then a single regime gate could be reconsidered. The current report does not prove that variable.

## 9. Recommended First Test

The next test should be the robustness gate, not another whitebox mutation.

Run the saved parent `ver_9a0ca0f8616c` / `run_2579435b99a9` against `ds_4e109af56413` using chronological walk-forward folds and cost stress. The exact checks should include baseline full-history reproduction, walk-forward slices, doubled commission, doubled slippage, and combined doubled execution costs. The test should record net PnL, PF, max drawdown, expected payoff, trade count, daily Sharpe, daily Sortino, worst daily return, and Calmar for each scenario.

If robustness passes, route to phase 4 diagnostics. If robustness fails, route to robustness repair before phase 4.

## 10. Acceptance Rule

Accept this parent as phase-4-ready only if robustness confirms that the time-risk filter is not brittle. The parent should maintain positive net PnL, adequate trade count, bounded drawdown, acceptable daily Sharpe/Sortino, and Calmar advantage under chronological folds and cost stress. Small degradation is expected under cost stress; collapse is not acceptable.

The acceptance standard is not raw buy-and-hold outperformance. This parent's claim is drawdown-adjusted efficiency. It must preserve that claim under more realistic validation.

## 11. Rejection Rule

Reject immediate phase-4 routing if the robustness gate shows that the time-risk filter only works in the full-history aggregate. Specific kill conditions are fold-level collapse, concentrated losses in older periods, cost-stress failure under doubled slippage or combined doubled execution costs, drawdown expansion that destroys Calmar advantage, or trade count falling into a low-evidence regime in key folds.

Reject another simple whitebox mutation unless new diagnostics identify a localized, causal weakness that does not repeat the failed breakeven or early-triage pattern.

## 12. Phase-4 Readiness

The parent is close to phase-4 readiness but not production-ready. It has enough trades, positive net PnL, strong drawdown control, improved profit factor, strong daily portfolio Sharpe/Sortino, meaningful Calmar advantage over buy and hold, and no obvious remaining single-rule whitebox weakness. That is the correct kind of parent for phase 4: the next plausible improvement is a narrow decision-time-safe overlay, not another broad hand rule.

However, phase 4 should follow the robustness gate, not precede it. Paper trading is not appropriate yet. Paper trading belongs only after phase 4 is completed or explicitly skipped and the final parent survives robustness.

## 13. Final Routing

Route to robustness gate first. If `ver_9a0ca0f8616c` passes chronological walk-forward and cost-stress checks, route to phase 4 hybrid diagnostics. Do not implement another phase-3 whitebox mutation now, and do not route to paper trading.
