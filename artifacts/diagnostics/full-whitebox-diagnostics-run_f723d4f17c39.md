# Full-Whitebox Diagnostics - run_f723d4f17c39

## 1. Frozen Parent Contract

`run_f723d4f17c39` freezes the XAU transplant of the BTC winner inside family `xauusd_ghl_dc`. The saved version is `ver_cfbfb3577dd3`, named `XAU test | BTC winner run_a871be4f8292 transplanted to XAU M30 | tuned atr_len=52, entry_mode=crossover_plus_pullback, fast_len=1...`. The asset is `XAUUSD`, venue is `IC Markets MT5`, timeframe is `30m`, dataset is `ds_4e109af56413`, and the report covers `100319` bars from the IC Markets XAUUSD 30m dataset.

The engine is `ma_cross_atr_stop_v1`, using SMA logic with `fast_len=1`, `slow_len=3`, `entry_mode=crossover_plus_pullback`, both long and short enabled, ATR stop `atr_len=52` and `stop_mult=3.3`, breakeven enabled at `0.25R` with `1.0R` lock, `sizing_mode=mt5_fixed_risk_lot`, `initial_capital=5000`, `risk_pct=0.01`, `max_leverage=1.0`, `min_lot=0.01`, `lot_step=0.01`, `commission_pct=0.0035`, and `slippage_ticks=10`. Time-risk filtering is disabled, short quality gate is disabled, time-decay logic is enabled in parameters but produced no exits in this run, and hybrid reverse triage is enabled with `hybrid_reverse_exit_min_mfe_r=0.0`, which effectively blocks nothing.

The frozen headline metrics are unusually strong: Net PnL `1243550863.27`, return `24871017.27%`, PF `2.9883`, max equity drawdown `2.55%`, expected payoff `28425.97`, total trades `43747`, win rate `36.86%`, average win/loss ratio `5.1196`, daily Sharpe `12.4154`, daily Sortino `33.0676`, worst daily return `-1.58%`, Calmar `9757142.0151`, and buy-and-hold outperformance `24870753.6%`. The production gate reports no core or portfolio failures, but this is not production-ready without robustness review and MT5 parity skepticism because the return scale is extreme.

## 2. Evidence Sufficiency

The Markdown report is sufficient for phase-3 diagnosis because it includes the frozen contract, headline metrics, buy-and-hold comparison, side decomposition, exit-reason decomposition, period decomposition, duration statistics, MFE/MAE evidence, and diagnostic counters. Raw JSON was used only to recover narrower reverse-exit details: reverse exits by side/year, MFE/R thresholds, and duration thresholds.

The run is mature enough for diagnosis on sample size alone: `43747` trades over a broad 2017-2026 dataset is not sample-starved. The bigger concern is not insufficient data, but whether the transplanted BTC engine has drifted into a hyperactive XAU micro-cycle identity whose economics must be validated against MT5 constraints and robustness gates.

## 3. Edge Statement

The parent does not make money through high hit rate. It wins through extreme payoff asymmetry and a stop-management engine that converts a minority of trades into very large winners. The win rate is `36.86%`, but the approximate breakeven win rate implied by the average win/loss ratio is only `16.34%`, so the low hit rate is not the defect.

The edge lives in the stop-managed exits. `stop` exits account for `14351` trades, net PnL `1814299859.62`, PF `67.0953`, win rate `98.1%`, and average bars held `2.76`. This is not a normal "stop loses money" profile; in this parent, the stop label is effectively the profitable managed-exit bucket after breakeven/lock behavior. The obvious failure bucket is `reverse`, with `29395` trades, net PnL `-570743749.76`, PF `0.0455`, win rate `6.95%`, and average bars held `1.75`.

## 4. Identity Drift Check

The BTC parent has drifted heavily after transplantation and optimization. It is no longer behaving like a medium-horizon BTC intraday trend continuation system. On XAU M30 it is a very short-cycle, high-frequency managed-trade system: median hold is `2` bars, 75th percentile is `3` bars, fast SMA length is `1`, slow SMA length is `3`, and the system enters `43747` trades. The causal identity is still whitebox because the engine is explicit, but the economic behavior is now "rapid micro-cycle entries funded by breakeven/ATR stop management, harmed by immediate opposite-signal churn."

That identity drift is acceptable only if future validation treats it as a new XAU strategy, not as BTC logic merely transferred intact.

## 5. Diagnostic Evidence

Both sides contribute strongly. Long trades produce `720822865.01` net PnL over `24742` trades with PF `3.06`; shorts produce `522727998.26` over `19005` trades with PF `2.8973`. Side removal is not justified.

The exit split is decisive. Reverse exits are structurally destructive: long reverse exits lose `-318334232.32`, short reverse exits lose `-252409517.44`. Stop exits are structurally constructive: long stop exits make `1039157097.33`, short stop exits make `775142762.29`.

The reverse problem is broad across time, not a one-year artifact. Reverse exits are negative every year in the inspected JSON: `-1906.55` in 2017, `-221778.12` in 2018, `-12121751.79` in 2019, `-76485605.67` in 2020, `-57013465.11` in 2021, `-61135768.12` in 2022, `-52719002.22` in 2023, `-73707942.90` in 2024, `-134995898.66` in 2025, and `-102340630.62` in 2026. Stop exits are positive every year.

Duration and excursion also localize the issue. Reverse exits are short-lived: `14490` reverse trades close within one bar for `-370435161.62`, and `24557` close within two bars for `-551420719.20`. Reverse exits with MFE/R below `0.20` account for `25430` trades and `-545324330.88` net PnL. This says the failing reverse bucket is mostly early opposite-signal churn with limited favorable excursion, not a few mature trades that clearly needed reversal exit.

## 6. Failure Localization

The failure is not side-specific. Both long and short reverse exits lose badly, while both long and short stop exits make money.

The failure is exit-specific. Time-decay produced `0` exits and hybrid time-decay triage produced `0` exits, so any mutation around time-decay confirmation is irrelevant for this run. The current hybrid reverse triage is technically enabled but inert because `hybrid_reverse_exit_min_mfe_r=0.0`; since reverse trades have nonnegative MFE/R by construction, this threshold blocks nothing.

The failure is also duration-specific. The most damaging reverse trades are very young positions, usually held one or two bars. The strategy is being paid when it lets stop/breakeven management handle the path, and punished when it obeys immediate opposite MA signals too readily.

## 7. Rival Explanations

One rival explanation is that reverse exits are the necessary cost of re-entering the other side quickly. That is possible, but the evidence is hostile to it: reverse exits have PF `0.0455`, while both sides still make money overall through stop-managed exits. A first mutation should not remove the ability to reverse forever, but it should force early reversals to prove they are real instead of noisy.

Another rival explanation is that the headline performance is a sizing artifact. This remains a real concern because the PnL scale is extreme on `5000` initial capital. But sizing artifacts do not explain why reverse exits lose across every year while stop exits win across every year. Execution and robustness checks must follow, but the next whitebox mutation can still target the exit-specific defect.

## 8. Mutation Queue

1. **Early reverse-exit confirmation gate.** Hypothesis: many immediate opposite-signal exits are churn that should not close a young trade unless the trade is already sufficiently adverse or has enough context to justify reversal. First test should activate the rule and suppress reverse exits only when the position is young, has weak favorable excursion, and is not beyond an adverse-risk escape threshold. This is the highest-priority mutation because the reverse bucket is the largest evidenced defect.

2. **Reverse-to-entry cooldown after suppressed reversal.** Hypothesis: when a reverse signal is suppressed, the opposite entry should also be delayed for a small number of bars. This waits because it is closely related to the first mutation and should not be stacked into the first test.

3. **Time-of-day risk filter for reverse-heavy pockets.** Hypothesis: some UTC hours may overproduce reverse churn. This waits because the report does not yet expose hour decomposition for reverse exits, and the current parent has no time-risk blocks.

4. **Side-specific reverse confirmation.** Hypothesis: long and short reversals may need different thresholds. This waits because both sides show the same failure family, so a symmetric first rule is cleaner.

## 9. Recommended First Test

Implement one active full-whitebox mutation: an early reverse-exit confirmation gate.

At the moment an opposite signal appears while a position is open, before closing the position for `reason="reverse"`, compute decision-time-safe fields: `bars_held`, `mfe_r`, `unrealized_r`, `position.direction`, and whether the breakeven stop has already moved. If the position is young and has not earned enough favorable excursion, suppress the reverse exit unless the trade is already sufficiently adverse. When suppressing the reverse exit, also suppress the immediate opposite entry on that same bar, matching the existing `hybrid_reverse_exit_triage` behavior.

First active preview values:

```json
{
  "reverse_confirmation_enabled": true,
  "reverse_confirm_max_bars": 2,
  "reverse_confirm_min_mfe_r": 0.20,
  "reverse_confirm_allow_if_unrealized_r_lte": -0.35,
  "reverse_confirm_require_no_breakeven_move": false
}
```

This first test is intentionally narrow. It attacks the cluster evidenced by `bars_held <= 2` and `mfe_r < 0.20`, but it keeps an adverse escape valve so the rule does not trap obvious failures.

## 10. Acceptance Rule

Accept the mutation only if, on the same `ds_4e109af56413` dataset and against frozen `run_f723d4f17c39`, it improves reverse-exit damage without deleting the evidence base. A survivor should improve net PnL or max drawdown meaningfully, keep PF at or above the parent neighborhood, retain at least `80%` of parent trade count unless the removed trades are specifically reverse churn, avoid damaging both long and short net PnL, keep stop exits as the profit engine, and improve or preserve daily Sharpe, daily Sortino, worst daily return, Calmar, and initial-risk/exposure diagnostics.

The best sign of survival is not a cosmetic win-rate lift. The useful evidence would be fewer reverse exits, less negative reverse net PnL, no collapse in stop-exit net PnL, and no concentration of gains in only 2025-2026.

## 11. Rejection Rule

Reject the mutation if it only improves headline metrics by deleting most trades, if it blocks profitable stop-managed trades before they can develop, if it damages one side materially, if it increases drawdown, if suppressed reversals become larger stop losses, if gains concentrate in one or two years, or if the rule depends on future MFE/MAE rather than values available at the reverse decision bar.

Also reject or revise it if the first preview shows that the adverse escape threshold is too loose or too strict: a rule that never suppresses reversals is inert, and a rule that suppresses nearly all reversals is not a narrow mutation.

## 12. Phase-4 Readiness

Do not route to phase 4 yet. The parent has strong full-history evidence and a huge sample, but it still has an obvious whitebox failure: reverse exits lose `-570743749.76` with PF `0.0455` while stop exits produce `1814299859.62` with PF `67.0953`. This is exactly the kind of explainable rule defect phase 3 should test before adding a hybrid or blackbox layer.

## 13. Final Routing

Route: implement the early reverse-exit confirmation gate as one active unsaved preview against `run_f723d4f17c39` / `ver_cfbfb3577dd3` on dataset `ds_4e109af56413`. Do not optimize time-decay confirmation levers for this run; they are irrelevant because this XAU transplant produced zero time-decay exits.
