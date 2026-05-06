# Full-Whitebox Diagnostics - run_0ce8106fd006

Source report: `artifacts/reports/run_0ce8106fd006.md`

Raw JSON was used only to recover row count, exact date coverage, first/last trade timestamps, and exit-specific MFE/MAE details not exposed in the Markdown report.

## 1. Frozen Parent Contract

The frozen parent is `run_0ce8106fd006`, family `xauusd_ghl_dc`, version `ver_8557b530000c`, stage `white_box`, verdict `promotion_candidate`. It trades `XAUUSD` on `IC Markets MT5`, timeframe `30m`, using dataset `ds_4e109af56413`. The equity curve contains `100319` bars from `2017-11-02T07:00:00+00:00` through `2026-05-01T19:00:00+00:00`. The first recorded trade opens at `2017-11-08T12:00:00+00:00`; the last closes at `2026-05-01T19:00:00+00:00`.

The engine is `ghl_dc_breakout_v1`, a translated GHL+DC breakout continuation system. After optimization it is long-only: `allow_long=true`, `allow_short=false`. Live parameters are `gann_high_period=21`, `gann_low_period=13`, `donchian_length=55`, `max_breakout_bars=12`, `atr_len=34`, `stop_mode=atr`, `stop_mult=2.5`, `sizing_mode=fixed_risk_pct`, `risk_pct=0.01`, `max_leverage=1.0`, `initial_capital=100000.0`, `commission_pct=0.0`, `slippage_ticks=10`, and `tick_size=0.01`.

The parent defines its current evidence with `1010` trades, net PnL `90923.34`, return `90.92%`, profit factor `1.4079`, max drawdown `5.39%`, expected payoff `90.02`, win rate `37.33%`, breakeven win rate `29.73%`, daily Sharpe `1.4130`, daily Sortino `1.6192`, worst daily return `-1.35%`, Calmar `16.8553`, average entry exposure `99.69%`, and maximum entry exposure `100.00%`.

Against buy and hold, the strategy does not win on absolute return. Buy and hold earns `263532.97`, return `263.53%`, with max drawdown `25.96%` and Calmar `10.1504`. The parent underperforms buy and hold by `-172.61%` in raw return, but wins on drawdown discipline and Calmar by `6.7048`.

## 2. Evidence Sufficiency

The report is sufficient for phase-3 diagnostics on the major questions: it contains the frozen contract, headline metrics, buy-and-hold comparison, parent comparison, side decomposition, exit-reason decomposition, period decomposition, duration statistics, and aggregate MFE/MAE. The JSON was needed only for details the report does not yet surface: row count, exact dataset timestamps, exact first/last trade timestamps, and MFE/MAE by exit reason.

This is mature enough for phase-3 reasoning. The sample has `1010` trades across more than eight years of M30 data. It is not a tiny-sample profit-factor artifact. The report would be stronger if future diagnostics included MFE/MAE by exit reason directly, because that detail is central when deciding between breakeven, trailing, time-decay, and stop-width mutations.

## 3. Edge Statement

The edge is payoff asymmetry with controlled drawdown, not hit rate. A `37.33%` win rate is acceptable because the breakeven win rate implied by the average win/loss relationship is `29.73%`. The parent makes money when long breakout attempts develop into continuation trades and exit by Gann-state logic. It loses money when breakouts fail quickly into ATR stops.

The strategy's real claim is not that it beats holding gold on raw return. It claims that it can participate in XAUUSD upside with far lower drawdown, producing a better Calmar profile. That is a valid research identity, but it means future mutations should protect the continuation winners rather than force a high win-rate profile.

## 4. Identity Drift Check

The translated parent has already drifted from a broad two-sided GHL+DC concept into a long-only managed breakout strategy. That drift is acceptable because optimization found the short side unhelpful and the resulting parent still has a causal, explainable structure: long breakouts, ATR-defined initial risk, and Gann-state exits for continuation.

The parent should not now be mutated into a mean-reversion system, target-taker, or heavily filtered sparse-trade model unless evidence proves the breakout engine itself is wrong. The current identity depends on keeping enough attempts for the long-side breakout distribution to express itself.

## 5. Diagnostic Evidence

Side decomposition is simple and important: the parent is entirely long-side. Long trades contribute all `1010` trades and all `90923.34` net PnL, with profit factor `1.4079`, win rate `37.33%`, average win `832.45`, average loss `-352.15`, and average duration `16.16` bars. There are no short trades because `allow_short=false`.

Exit decomposition localizes the strategy's money flow. `gann_state_exit` produces `734` trades, net PnL `230713.98`, profit factor `3.7757`, win rate `51.36%`, average win `832.45`, average loss `-232.83`, and average duration `20.43` bars. `stop` produces `275` trades, net PnL `-139507.01`, profit factor `0.0`, average loss `-507.30`, and average duration `4.83` bars. `time_exit` appears once and loses `-283.63`, so it is not a current structural driver.

Period evidence is mixed but usable. Positive periods include 2017, 2019, 2020, 2021, 2022, 2023, 2025, and 2026. Weak periods are 2018 at `-2902.29` and 2024 at `-261.67`. The edge is not one-year-only, but it is uneven: the parent survives choppy or difficult years without catastrophic drawdown, then compounds hard in favorable years such as 2025 and early 2026.

Duration evidence fits the claimed identity. Median trade duration is `13` bars, with 75th percentile `22`, 90th percentile `33`, and 95th percentile `42`. This is a short-to-medium continuation system, not a scalper and not a multi-week trend holder.

Aggregate excursion evidence shows average `mfe_r=1.3579` and average `mae_r=-0.7363`. JSON exit-level evidence sharpens the diagnosis: Gann-state exits have average `mfe_r=1.6868` and average `mae_r=-0.4664`, while stop exits have average `mfe_r=0.4844` and average `mae_r=-1.4563`. More than half of stop exits, `57.1%`, reached at least `0.25R` favorable excursion; `33.8%` reached at least `0.50R`; `21.1%` reached at least `0.75R`; only `12.4%` reached at least `1.00R`. Stop failures also happen early: `67.3%` of stop exits close within `5` bars, and `86.2%` close within `8` bars.

## 6. Failure Localization

The first localized failure is stop-exit damage. The parent is profitable despite losing `-139507.01` on stops, because Gann-state exits earn `230713.98`. That makes stop management the most evidenced whitebox weakness, but it does not justify simply tightening the ATR stop. Winners still need some adverse movement tolerance, and the Gann-state right tail must be protected.

The second failure is absolute buy-and-hold underperformance. The strategy's raw return is `90.92%` versus buy-and-hold `263.53%`. This is not automatically fatal because drawdown is much lower, but it limits production claims. The parent is a drawdown-adjusted candidate, not a raw-return replacement for holding gold.

The third failure is chronological unevenness. 2018 and 2024 are weak, while 2025 and 2026 contribute heavily. This does not bury the parent, but it argues against production routing before walk-forward and cost-stress testing.

No current evidence supports side-selection repair as the next mutation. The weak side has already been removed. No current evidence supports a broad session/time filter because the report does not expose hour, weekday, session, or volatility-regime decomposition.

## 7. Rival Explanations

One rival explanation is that the parent only wins because 2025 and early 2026 were unusually friendly to XAUUSD continuation. Period evidence weakens but does not eliminate this concern: several earlier years are positive, but the return profile is uneven. This should be handled later by chronological walk-forward and regime decomposition, not by guessing a regime filter now.

Another rival explanation is that the ATR stop is too wide or too narrow. The report does not prove either. Stop exits lose heavily, but Gann-state winners show that successful trades need room to move. Ordinary `atr_len` and `stop_mult` retuning already happened in phase 2, so phase 3 should not begin by repeating that sweep.

A third rival explanation is that short trades could be valuable in certain regimes. The frozen parent has no short trades, and the optimized result explicitly selected `allow_short=false`. Without side-by-regime evidence showing a useful short niche, reintroducing shorts would be a speculative reversal of phase-2 evidence.

## 8. Mutation Queue

The first-ranked mutation is an MFE-activated breakeven/profit-lock stop. The hypothesis is that a subset of failed long breakouts first moves favorably enough to justify reducing open risk, and that this can shrink the stop-loss bucket without damaging the Gann-state continuation engine. The smallest active first test should enable the rule with `breakeven_trigger_r=0.75` and `breakeven_lock_r=0.0`.

The second-ranked mutation is an early failed-entry triage rule, but it should wait. Stop losers close quickly, so an early triage rule may help, but the report does not yet show enough non-progress labels, bars-since-entry progress, or early MFE path detail to define a better first test than breakeven.

The third-ranked mutation is a period/regime gate. It should wait because the current report shows annual outcomes but not the actual explanatory regime variable. A volatility, trend-strength, or time-of-week filter would be plausible only after a diagnostic artifact proves which context is responsible.

The fourth-ranked mutation is a phase-4 hybrid overlay. It should wait because there is still an obvious explainable whitebox weakness: stop-exit damage after partial favorable excursion.

## 9. Recommended First Test

Implement one active first-test candidate: MFE-activated breakeven/profit-lock stop management for `ghl_dc_breakout_v1`.

For long trades, after entry, compute favorable excursion in R using data available at the current bar. If `mfe_r >= breakeven_trigger_r`, move the active stop to at least `entry_price + initial_risk_per_unit * breakeven_lock_r`. Do not loosen the stop. Preserve the existing Gann-state exit as the primary winner-harvesting mechanism.

First preview parameters:

```json
{
  "breakeven_stop_enabled": true,
  "breakeven_trigger_r": 0.75,
  "breakeven_lock_r": 0.0
}
```

This test is conservative. A `0.75R` trigger touches `21.1%` of current stop exits, while still being less likely than a `0.25R` or `0.50R` trigger to interfere with trades that need normal noise tolerance before becoming Gann-state winners.

## 10. Acceptance Rule

Accept the mutation only if it beats the frozen parent on the same full-history dataset without weakening the evidence base. The child should improve or preserve net PnL, improve profit factor above `1.4079`, keep max drawdown at or below `5.39%`, preserve expected payoff near or above `90.02`, maintain a large trade sample near the parent, and reduce stop-exit damage without materially reducing Gann-state exit net PnL.

Portfolio-period evidence matters more than trade cosmetics. Daily Sharpe, Daily Sortino, worst daily return, Calmar, exposure, and initial-risk behavior must remain comparable or improve. The child must preserve the drawdown-adjusted advantage over buy and hold. A higher win rate alone is not enough.

## 11. Rejection Rule

Reject the mutation if it wins by damaging the economic engine. Specific kill conditions are: trade count collapses, Gann-state exit PnL or right-tail capture is materially reduced, expected payoff deteriorates meaningfully, worst daily return worsens, max drawdown rises, yearly decomposition hides shifted losses, or the improvement comes only from exiting too early and making the system look cleaner while lowering payoff asymmetry.

Reject it immediately if implementation depends on future data or on intrabar assumptions that the MT5 backtest cannot reproduce.

## 12. Phase-4 Readiness

The parent is not ready for phase 4 yet. It has enough trades, positive full-history net PnL, acceptable drawdown, and a credible drawdown-adjusted case against buy and hold. But it still has an obvious whitebox weakness: the stop-loss bucket is large, fast, and partially preceded by favorable excursion.

Phase 4 becomes reasonable only after the breakeven/profit-lock stop mutation either survives and becomes the next parent, or is rejected with clear evidence showing that simple stop management cannot improve the parent. Even then, production-readiness would still require chronological walk-forward folds and execution-cost stress tests: doubled commission, doubled slippage, and combined doubled execution costs.

## 13. Final Routing

Route to one active phase-3 mutation: implement MFE-activated breakeven/profit-lock stop management as an unsaved preview against frozen parent `run_0ce8106fd006` on dataset `ds_4e109af56413`.

Do not promote, do not route to phase 4, and do not paper trade this parent yet.
