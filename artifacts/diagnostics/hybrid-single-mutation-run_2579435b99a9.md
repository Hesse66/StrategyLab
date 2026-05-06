# Hybrid Single-Mutation Routing - run_2579435b99a9

Source report: `artifacts/reports/run_2579435b99a9.md`

Whitebox diagnostics: `artifacts/diagnostics/full-whitebox-diagnostics-run_2579435b99a9.md`

Robustness context: `needs_review`; walk-forward `3/4`; cost stress `3/3`. Failed fold: `2022-02-02T11:00:00+00:00` to `2024-03-18T11:00:00+00:00`, failure `low_daily_sortino`, fold Daily Sortino `0.7398` versus the approximate `0.75` gate.

## 1. Frozen White-Box Parent Contract

The frozen parent is `run_2579435b99a9`, version `ver_9a0ca0f8616c`, family `xauusd_ghl_dc`, stage `white_box`, verdict `promotion_candidate`. It trades `XAUUSD` on `IC Markets MT5`, timeframe `30m`, dataset `ds_4e109af56413`, with `100319` bars from `2017-11-02` through `2026-05-01`.

The parent is a long-only, timing-filtered GHL+DC breakout continuation strategy. Its engine is `ghl_dc_breakout_v1`. The live contract is `allow_long=true`, `allow_short=false`, `gann_high_period=21`, `gann_low_period=13`, `donchian_length=55`, `max_breakout_bars=12`, `atr_len=34`, `stop_mode=atr`, `stop_mult=2.5`, `breakeven_stop_enabled=false`, `time_risk_filter_enabled=true`, `time_risk_block_utc_hours=[1,7,12,14,21]`, `time_risk_block_weekdays=[]`, `sizing_mode=fixed_risk_pct`, `risk_pct=0.01`, `max_leverage=1.0`, `commission_pct=0.0`, and `slippage_ticks=10`.

The frozen evidence is strong enough to be a living parent: net PnL `113504.68`, return `113.50%`, PF `1.5977`, max drawdown `5.17%`, expected payoff `129.57`, `876` trades, win rate `38.24%`, daily Sharpe `1.7114`, daily Sortino `1.9770`, worst daily return `-1.35%`, and Calmar `21.9339`. It does not beat buy and hold on raw return, but it beats buy and hold on drawdown-adjusted efficiency with Calmar delta `11.7835`.

The causal story is narrow: Gann state defines trend state, Donchian confirmation gates breakout entries, UTC time-risk blocks historically weak entry hours, ATR defines initial risk, and Gann-state exits capture continuation winners.

## 2. Why Hybrid Is Justified or Not

Hybrid work is justified, but only as a research step. The parent is not dead, sample-starved, or underdiagnosed. It has `876` trades, positive full-history evidence, a clean whitebox contract, and no obvious remaining single-rule whitebox weakness after the time-risk filter. It also passed execution cost stress `3/3`.

The reason not to call it production-ready is the walk-forward result: `3/4` folds passed, with fold 3 failing only `low_daily_sortino`. That is not a collapse, but it is exactly the kind of remaining weakness a narrow hybrid overlay can investigate. Another hand-written whitebox rule would likely overfit because the obvious ones were already tested or rejected: breakeven damaged the Gann-state right tail, early failed-entry triage looked negative, and remaining hours/weekdays do not show a clear loss pocket.

## 3. Remaining Weakness to Solve

The remaining weakness is not average profitability. It is tail quality and downside clustering in a difficult chronological slice: `2022-02-02` to `2024-03-18`. Fold 3 remains profitable with return `6.71%`, PF `1.1920`, `208` trades, max drawdown `5.00%`, daily Sharpe `0.7994`, and Calmar `1.3420`, but Daily Sortino is `0.7398`, just below gate.

The hybrid layer should attack one problem: identify low-quality entry contexts that are more likely to create downside clustering or poor payoff in difficult regimes, without cutting the Gann-state continuation trades that fund the parent.

## 4. Chosen Hybrid Role

The chosen role is an entry-quality veto overlay.

The hybrid layer should score each otherwise-valid whitebox entry at decision time and veto only the lowest-quality slice. It must not replace Gann/Donchian logic, modify exits, manage stops, or create new entries. It is a narrow quality gate placed after the whitebox signal and before order creation.

This role is preferable to an in-trade early-exit hybrid as the first experiment because simple early trade-management already showed a dangerous pattern: it can clean up losses while damaging future Gann-state winners. Entry scoring is cheaper to validate and easier to promote into explicit strategy parameters if it survives.

## 5. Feature Contract

Only decision-time entry features are allowed. The feature set should come from data already available on the signal bar or earlier:

- Entry timing: UTC hour, weekday, month, whether the hour is adjacent to blocked hours.
- GHL/DC state: current Gann state, bars since Gann flip, breakout age, distance from Donchian breakout level.
- Volatility/risk: ATR, ATR percent of price, stop distance, stop distance as ATR, initial risk percent, spread/slippage proxy if available.
- Recent structure: recent 20-bar return, recent 20-bar range, recent 20-bar realized volatility, distance from recent high/low.
- Trend shape: high/low SMA slopes, normalized distance from Gann state line, recent cross count.
- Portfolio-safe context: entry exposure and risk budget before the trade.

Forbidden features include future MFE/MAE, exit reason, final PnL, future bars, fold labels known only after the fact, or any feature derived from post-entry path.

## 6. Model Contract

Use the smallest transparent CPU-friendly model that can rank entry quality. The first model should be a regularized logistic classifier or a shallow decision tree trained to estimate whether a trade belongs to a poor-quality class, such as negative net PnL or poor R outcome. If both are available, prefer logistic regression for a first pass because its coefficients are auditable and easier to convert into a live proxy.

No deep learning, no GPU, no ensemble, no black-box replacement of the strategy. The output should be a score and a veto threshold, not a new trading system.

## 7. Validation Contract

Validation must be chronological and compared against frozen parent `run_2579435b99a9`.

The offline preview must use walk-forward training and testing. A valid pattern is: train on earlier folds, score the next fold, apply a small veto fraction, and report fold-level metrics against the frozen parent fold. No random train/test split is acceptable as primary evidence.

The veto fraction should be small and predeclared. First test candidates should include `10%` and `15%` veto fractions, but the first formal experiment should report `15%` as the main candidate because the app already has a comparable hybrid entry-quality experiment path. The hybrid must preserve activity; it cannot win by deleting most trades.

Offline survival is only a research filter. Promotion requires implementing the score/proxy as explicit strategy parameters, retesting in the live backtest engine on the same frozen parent and dataset, and then rerunning robustness.

## 8. Acceptance Rule

The offline hybrid survives only if it improves portfolio-period evidence versus the frozen parent without destroying activity. Required evidence:

- Full-history retained trade count remains at least `75%` of parent activity, preferably over `700` trades.
- Net PnL, PF, expected payoff, daily Sharpe, daily Sortino, and Calmar improve or remain materially comparable.
- Worst daily return does not worsen from `-1.35%`.
- Fold 3 Daily Sortino improves above the gate without causing another fold to fail.
- Gann-state right-tail capture is preserved; the model must not veto mostly future Gann-state winners.
- Cost stress remains acceptable after live-engine promotion.

For quant-style review, Daily Sharpe, Daily Sortino, worst daily return, Calmar, exposure, and initial risk are more important than trade-level Sharpe.

## 9. Failure Rule

Reject the hybrid if it only works in full-sample scoring, if it fails chronological validation, if it lowers fold robustness, or if it improves PF by deleting too many trades. Reject it if it materially reduces Gann-state exit PnL, worsens worst daily return, worsens drawdown, or creates a fragile threshold that only rescues the known weak fold while damaging other folds.

Reject it immediately if any feature uses future path information, final trade outcome leakage, or labels unavailable at decision time.

## 10. Live-Engine Promotion Contract

If the offline entry-quality veto survives, it must be translated into explicit live-engine parameters before promotion. Acceptable live proxies include a small set of coefficient weights, a score threshold, and a veto fraction/threshold parameter, all applied only at entry decision time.

The live engine must record:

- hybrid_entry_quality_score
- hybrid_entry_quality_vetoes
- vetoed side
- vetoed hour/week/regime context
- retained versus vetoed diagnostic summaries

The live proxy must reproduce the offline edge on the same frozen parent and dataset. If it does not, keep the branch disabled or reject it. After live-engine survival, rerun the Mutation Lab robustness gate. Only a hybrid parent that passes walk-forward and cost stress may be called a production robustness candidate.

Paper trading, if reached later, should run for both a calendar minimum and a trade-count minimum. Given the historical frequency of `876` trades over roughly 8.5 years, the strategy averages around two trades per week. Paper trading should therefore run for at least several weeks to a few months and until at least `20` to `30` paper trades are observed, whichever takes longer.

## 11. First Hybrid Experiment

Run one offline hybrid entry-quality veto experiment on `run_2579435b99a9`.

Experiment:

- Parent: `run_2579435b99a9` / `ver_9a0ca0f8616c`
- Dataset: `ds_4e109af56413`
- Role: entry-quality veto only
- Model: regularized logistic classifier or shallow transparent classifier
- Features: decision-time entry features only
- Main veto fraction: `0.15`
- Secondary sensitivity: `0.10`
- Validation: chronological walk-forward against the frozen parent
- Primary target: improve fold 3 Daily Sortino while preserving full-history net PnL, PF, Calmar, and trade count

Do not implement a live engine mutation until this offline experiment produces clear chronological evidence.

## 12. Final Routing

Route to `04-1` hybrid diagnostics / offline entry-quality experiment.

Do not return to phase-3 whitebox now, do not promote to paper trading, and do not call the current parent production-ready. The next practical step is a narrow hybrid entry-quality veto diagnostic focused on the weak walk-forward fold and on preserving the Gann-state right tail.
