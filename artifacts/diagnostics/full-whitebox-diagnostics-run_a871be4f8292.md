# Full-Whitebox Diagnostics for run_a871be4f8292

## 1. Frozen Parent Contract

The frozen parent is `run_a871be4f8292`, family `btc_intraday`, dataset `ds_d14d74e36d0d`, engine `ma_cross_atr_stop_v1`, asset `BTCUSDT`, venue `Binance Spot`, timeframe `15m`, stage `white_box`, verdict `promotion_candidate`. Raw JSON confirms `303723` bars in the equity/risk artifact, with equity coverage from `2017-08-17 04:00 UTC` through `2026-04-21 19:45 UTC`; the first recorded trade runs from `2017-08-19 22:45 UTC` to `2017-08-20 08:45 UTC`, and the last recorded trade runs from `2026-04-20 12:45 UTC` to `2026-04-20 14:30 UTC`.

The execution style is SMA crossover-only with both long and short enabled. The live parameters are `ma_kind=sma`, `fast_len=30`, `slow_len=104`, `noise_lookback=25`, `max_no_cross=1`, `entry_mode=crossover_only`, `allow_long=true`, `allow_short=true`, `atr_len=70`, `atr_timeframe=15m`, `stop_mult=5.1`, `initial_capital=100000`, `sizing_mode=fixed_risk_pct`, `risk_pct=0.01`, `max_leverage=1.0`, `commission_pct=0.04`, `slippage_ticks=2`, and `tick_size=0.01`.

The current parent already includes several whitebox and hybrid-style controls: breakeven stop enabled at `0.25R` with `1.0R` lock, failed-entry time-decay enabled at `40` bars and `0.35R`, short quality gate enabled with `block_below_sma` over `24960` bars, time-risk filter enabled with blocked UTC hours `[13,15,21]` and blocked weekday `[6]`, hybrid time-decay triage enabled at checkpoint `[30]` with max unrealized R `-0.45` and max MFE/R `0.15`, and hybrid reverse-exit triage enabled with minimum MFE/R `0.1`.

The headline metrics define a very strong frozen reference: net PnL `5902450.78`, return `5902.45%`, profit factor `4.4681`, max drawdown `3.87%`, expected payoff `7725.72`, total trades `764`, win rate `75.65%`, average win/loss ratio `1.4378`, approximate breakeven win rate `41.02%`, daily portfolio Sharpe `5.9811`, daily portfolio Sortino `3.6352`, worst daily return `-2.06%`, Calmar `1525.0041`, buy-and-hold return `1637.47%`, buy-and-hold max drawdown `83.97%`, outperformance `4264.98%`, and Calmar delta `1505.5033`.

## 2. Evidence Sufficiency

The Markdown report is sufficient for a phase-3 diagnostic memo because it contains the frozen contract, headline metrics, parent comparison, production gate, buy-and-hold comparison, side decomposition, exit-reason decomposition, period decomposition, duration statistics, and MFE/MAE diagnostics. Raw JSON was used only to confirm row/trade coverage and date boundaries.

Two evidence gaps should be noted before production-style routing. First, this report does not include chronological walk-forward or cost-stress robustness results for this exact saved version. Second, because the parent already includes hybrid-named rules despite being marked `white_box`, phase-4 readiness must be interpreted carefully: this is not a clean pre-hybrid whitebox parent. It is already a heavily managed parent with some hybrid overlay behavior.

## 3. Edge Statement

The edge is not a simple right-tail trend-capture system anymore. It wins through a managed high-hit-rate trade lifecycle: SMA cross entries admit trades, a wide ATR stop defines initial risk, breakeven movement and locked stops convert many exits into positive stop-labeled outcomes, side and time filters remove weak contexts, and failed-entry triage tries to cut trades that do not prove themselves. The win rate of `75.65%` is far above the approximate breakeven win rate of `41.02%`, so the system is not surviving on rare giant winners alone. It is surviving because many managed exits are profitable and losses are tightly contained relative to compounding equity.

The strongest clue is the exit decomposition. `stop` exits account for `626` trades and `6430190.44` net PnL with PF `6.9995` and win rate `89.62%`. In a naive strategy, stop exits would usually be a damage bucket. Here, stop exits are the engine because breakeven and lock behavior appear to turn the stop mechanism into a managed-profit exit. The parent should therefore be protected from any mutation that treats stop exits as failures.

## 4. Identity Drift Check

Identity drift is significant and explicit. The parent likely started as a medium-horizon moving-average crossover strategy with ATR stops, but it now behaves more like a short-cycle managed-trade system. Median hold is `11` bars, the 75th percentile is `27` bars, and both the 90th and 95th percentile are exactly `40` bars, matching the time-decay horizon. That shows the trade lifecycle is actively shaped by the management stack.

The current causal identity is acceptable because the strategy remains causal, decision-time explainable, and stronger than the frozen baseline lineage. But future mutations must respect the new identity. The goal is not to return it to a pure trend-following crossover model; the goal is to refine the managed-trade parent without damaging the stop-managed profit engine.

## 5. Diagnostic Evidence

The strategy has broad chronological evidence. Every calendar year from 2017 through 2026 is positive. The weakest PF year is 2018 at `2.2759`, still profitable. 2024 and 2025 are large contributors, with 2024 producing `1406310.19` net PnL and PF `6.2467`, while 2025 produces `2506272.94` net PnL and PF `4.13`. The parent does not appear to depend on one lucky year, although compounding naturally makes later years contribute larger absolute PnL.

Side evidence is balanced. Longs produce `3748632.6` net PnL across `490` trades with PF `4.478` and win rate `75.71%`. Shorts produce `2153818.18` net PnL across `274` trades with PF `4.4511` and win rate `75.55%`. The short side has fewer trades because the quality gate blocks `294` short contexts, but the surviving shorts are clearly useful. There is no evidence for side removal.

Exit evidence is uneven. The stop bucket is excellent: `626` trades, `6430190.44` net PnL, PF `6.9995`, win rate `89.62%`, average bars `11.73`. Reverse exits are small but positive: `11` trades, `57678.32` net PnL, PF `2.8381`. The losing buckets are the time-failure exits: `time_decay` has `99` trades, `-311480.01` net PnL, PF `0.041`, win rate `16.16%`; `hybrid_time_decay_triage` has `28` trades, `-273937.97` net PnL, PF `0.0`, win rate `0.0%`. Together, these time-failure exits lose about `585417.98`.

The excursion evidence is subtle. Average MFE/R is only `0.3687`, while average MAE/R is `-0.3676`. That symmetry suggests trades frequently experience modest favorable and adverse movement, and the management rules are doing much of the work. It also warns against naive tighter stops or aggressive early exits: winners may require some adverse movement, and the profitable stop bucket may rely on giving trades enough room.

## 6. Failure Localization

**Side-specific weakness:** No side-specific weakness is evidenced. Both sides are profitable, high-PF, and high-win-rate after gating. A side removal mutation would be unjustified.

**Exit-specific weakness:** The clear localized weakness is time-failure handling. `time_decay` and `hybrid_time_decay_triage` are materially negative in standalone decomposition. That does not automatically mean they should be removed because they may prevent worse losses. But it does justify a focused diagnostic and mutation queue around whether failed-entry exits can be made more selective.

**Period/regime weakness:** The report does not expose a damaging year or broad chronological regime. All years are positive. 2018 is weaker but still robust enough that a year/regime gate would be premature.

**Duration weakness:** The duration distribution shows concentration at the `40`-bar time-decay threshold. That is expected given the rules, but it also means time-decay is an important behavioral boundary. The 90th/95th percentile at `40` bars makes failed-entry triage a natural diagnostic target.

**Time-of-day/week weakness:** The current time-risk filter already blocks `244` entries, with UTC hours `[13,15,21]` and Sunday blocked. The report does not show remaining hour-level decomposition, so further time filtering is an open question rather than a conclusion.

**Excursion weakness:** Average MFE/R around `0.37` implies many trades do not travel far before being managed. This supports diagnostics around failed-entry confirmation, but does not support tighter stops without survival analysis.

**Cost sensitivity:** The report has strong margin over buy-and-hold and strong PF, but does not include cost-stress results. Cost robustness remains unverified for this exact parent.

**Trade-count weakness:** Trade count is adequate at `764`, with broad period coverage. Any mutation that reduces trades sharply should be treated as fragile.

## 7. Rival Explanations

The most tempting explanation is that the time-decay and hybrid time-decay exits are simply bad rules. That may be true, but the report alone cannot prove it. They may be negative because they are assigned to trades that were already failing and would have lost more if held to a later stop or reverse exit. A direct removal could improve the exit-reason table while worsening drawdown, worst daily return, or portfolio expectancy.

A second rival explanation is that the parent is overfit by the compounding capital model. The production gate allows `fixed_risk_pct`, and the initial risk is bounded at `1%`, but compounding makes later-year PnL enormous. This is not a rejection, because drawdown and buy-and-hold comparison are strong, but it means robustness must be tested before paper-style routing.

A third rival explanation is that the hybrid overlays are already doing the job that phase 4 would normally do. Because hybrid time-decay and reverse triage are present, the next step should not automatically be another hybrid layer. The remaining weakness is still explainable enough to test as a whitebox refinement.

## 8. Mutation Queue

1. **Failed-entry time-decay confirmation gate.** Hypothesis: the current time-decay exits catch many bad trades, but they may be too blunt. A confirmation rule can reduce unnecessary time-failure exits by requiring the trade to still be weak at the time-decay decision point. The smallest active first test should enable a confirmation layer that allows time-decay closure only when unrealized R remains weak and MFE/R has not exceeded a modest threshold. It must improve or preserve net PnL, daily Sortino, drawdown, and exit decomposition without deleting the stop-managed profit engine. Rejection condition: it is rejected if it merely delays losses, increases drawdown, or reduces the profitable stop bucket materially.

2. **Time-risk residual hour diagnostic gate.** Hypothesis: remaining weak entries may cluster in a few unblocked UTC pockets. The smallest active first test would add only one evidenced hour or a small curated hour set after report/export generation exposes remaining hour expectancy. This waits because the current report lacks hour decomposition beyond the existing blocked counters. Rejection condition: reject if it cuts many trades while producing only cosmetic PF improvement.

3. **Breakeven lock refinement.** Hypothesis: `breakeven_lock_r=1.0` may be central to the profitable stop bucket, but a more nuanced lock rule could reduce adverse later exits. This waits because the stop bucket is already the strongest engine and should not be disturbed before failed-entry exits are understood. Rejection condition: reject if stop-exit PF or net PnL deteriorates.

4. **Reverse-exit triage refinement.** Hypothesis: reverse exits are few and positive, while hybrid reverse blocks are `17`; there may be a small improvement in reversal handling. This waits because the sample is tiny and not the dominant failure. Rejection condition: reject if the sample remains too small or if gains are low-sample artifacts.

## 9. Recommended First Test

The recommended first test is a failed-entry time-decay confirmation gate. This is the narrowest mutation that attacks the localized weakness without changing the entry engine, side permissions, sizing, ATR stop, breakeven rule, or time-risk filter.

The active first test should add `time_decay_triage_confirmation_enabled=true`. It should evaluate only when the existing time-decay or hybrid time-decay logic is already about to close a trade. It should use only decision-time state: current unrealized R, MFE/R so far, bars held, side, timestamp, current fast/slow MA relationship, recent cross count, and whether a breakeven stop move has occurred. A defensible first configuration is to confirm failed-entry closure only if unrealized R is at or below `0R` and MFE/R is below or near the existing `time_decay_min_mfe_r=0.35`. The rule must record candidate exits seen, exits confirmed, exits suppressed, and the later outcome of suppressed exits.

This first test should run as an unsaved preview against the frozen parent on the same dataset `ds_d14d74e36d0d`. It should not optimize ordinary parameters first. If the active rule fails in this simple form, the family should not hide the failure with a wide search.

## 10. Acceptance Rule

Accept the mutation only if it improves the frozen parent in a portfolio-relevant way. The child should preserve at least most of the `764`-trade evidence base, keep max drawdown near or below the parent `3.87%`, avoid worsening worst daily return beyond `-2.06%`, and preserve the profitable stop-managed engine. It should improve or materially clean up the negative time-failure exits without damaging both sides or concentrating gains in a single year.

Because the parent is already exceptionally strong, acceptance should not require a dramatic PF jump. A modest improvement in net PnL, daily Sortino, Calmar, worst daily return, or exit decomposition is meaningful if trade count, side balance, period breadth, and buy-and-hold outperformance remain intact. Raw profit factor alone is not sufficient.

## 11. Rejection Rule

Reject the mutation if it only wins by deleting trades, if total trades collapse below a credible sample, if the `stop` exit bucket loses its role as the dominant profit engine, if either long or short side becomes materially weaker, if losses shift into a particular year/regime, if max drawdown or worst daily return worsens materially, or if the rule depends on future exit information. Also reject it if suppressing time-decay exits simply relabels losses into later stop exits without improving portfolio metrics.

## 12. Phase-4 Readiness

This parent is close to phase-4 quality in headline terms: it has enough trades, very strong profit factor, low drawdown, broad annual positivity, balanced side behavior, and major buy-and-hold outperformance. However, phase 3 is not done yet because there is an obvious explainable weakness in the time-failure exit buckets. In addition, the parent already contains hybrid-named overlays, so routing to phase 4 would be conceptually messy until this whitebox/hybrid boundary is cleaned up.

Before any production-ready language, this version must pass the Mutation Lab robustness gate: chronological walk-forward folds plus doubled commission, doubled slippage, and combined doubled execution costs. The current report does not include those checks.

## 13. Final Routing

Proceed to the first whitebox mutation from the queue: implement a failed-entry time-decay confirmation gate as an active unsaved preview. Do not promote, do not route to phase 4, and do not run broad `Optimize all` first. The next coding step should be one narrow rule-family change that refines time-decay closure decisions while preserving the existing entry, side, sizing, stop, breakeven, and time-risk contracts.
