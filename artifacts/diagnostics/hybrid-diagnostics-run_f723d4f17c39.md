# Hybrid-Blackbox Diagnostics - run_f723d4f17c39

## 1. Frozen Whitebox Parent Contract

The frozen whitebox parent is `run_f723d4f17c39`, family `xauusd_ghl_dc`, version `ver_cfbfb3577dd3`. It is the XAUUSD M30 transplant of BTC winner `run_a871be4f8292`, tested on `ds_4e109af56413`, `XAUUSD`, `IC Markets MT5`, `30m`, with `100319` bars in the report.

The engine is `ma_cross_atr_stop_v1`, execution is bar-close research execution with `slippage_ticks=10` and `commission_pct=0.0035`, both long and short are enabled, and sizing is `mt5_fixed_risk_lot` with `initial_capital=5000`, `risk_pct=0.01`, `max_leverage=1.0`, `contract_size=100`, `min_lot=0.01`, and `lot_step=0.01`. The live strategy parameters are `ma_kind=sma`, `fast_len=1`, `slow_len=3`, `entry_mode=crossover_plus_pullback`, `max_no_cross=4`, `atr_len=52`, `stop_mult=3.3`, breakeven enabled at `0.25R` with `1.0R` lock, time-risk disabled, short-quality gate disabled, and hybrid reverse triage effectively inert at `hybrid_reverse_exit_min_mfe_r=0.0`.

The parent verdict is `promotion_candidate`. Headline metrics are Net PnL `1243550863.27`, return `24871017.27%`, PF `2.9883`, max drawdown `2.55%`, expected payoff `28425.97`, total trades `43747`, win rate `36.86%`, average win/loss ratio `5.1196`, daily Sharpe `12.4154`, daily Sortino `33.0676`, worst daily return `-1.58%`, Calmar `9757142.0151`, and buy-and-hold outperformance `24870753.6%`.

## 2. Evidence Sufficiency

The report plus phase-3 artifacts are sufficient to decide whether phase 4 is justified. The report contains the frozen contract, headline metrics, buy-and-hold comparison, side decomposition, exit-reason decomposition, period decomposition, duration statistics, MFE/MAE, and diagnostic counters. Raw JSON was useful to derive entry feature availability and to test narrower explanations: reverse exits are followed by same-bar opposite entries, and those post-reverse entries produce large positive net PnL.

Two whitebox mutations were tested and rejected. `reverse_confirmation` raised PF but cut Net PnL from `1243550863.27` to `1002003408.57` and trades from `43747` to `25437`. `entry_exposure_gate` at `75%` reduced Net PnL to `173884.62` and trades to `1739`; even high thresholds below `100%` failed to beat the parent. This means the remaining problem is not well handled by simple hard-coded gates.

## 3. Why Hybrid Is Justified or Not

Hybrid work is justified as research, not as production routing. The parent is a living whitebox strategy: it has `43747` trades, broad 2017-2026 positive yearly evidence, strong drawdown control, both sides profitable, and strong portfolio-period metrics. It is not sample-starved.

Hybrid work is justified because the obvious whitebox fixes were too blunt. The reverse bucket is ugly in isolation, but blocking it damages the rotation mechanism because every reverse exit is also a same-bar flip into the next trade; those post-reverse entries produce `808278267.12` net PnL. Exposure gates were also too blunt because the system compounds through changing equity and lot constraints. The remaining task is therefore not "remove reverse exits" or "cap exposure"; it is to score entry quality softly enough to preserve the engine while reducing low-quality participation.

## 4. Whitebox Causal Identity

The whitebox parent is a short-cycle XAU managed-trade engine. It uses very fast moving-average structure, frequent long/short rotation, and MT5-style fixed-risk lot sizing. Its economic engine is payoff asymmetry and stop/breakeven management, not hit rate. Stop exits are the profit bucket: `14351` stop exits generate `1814299859.62` net PnL with PF `67.0953`. Reverse exits are the accounting cost of rotation: `29395` reverse exits lose `-570743749.76`, but those exits often open the next profitable sequence.

The hybrid component must not replace entries, exits, stops, or side logic. It may only score candidate entries at the moment the whitebox engine wants to enter, then either reduce risk or lightly rank/filter the lowest-quality candidates.

## 5. Remaining Weakness to Solve

The remaining weakness is noisy entry participation inside a high-frequency rotation engine. The parent takes many trades with low favorable excursion or negative outcome, but simple rules cannot separate harmful churn from necessary churn without deleting the winners that fund the strategy.

The trade rows already expose decision-time feature families that can support a narrow entry-quality score: side, weekday, UTC hour, month, fast/slow SMA state, normalized MA distance, slopes, ATR percent, recent return, recent range, recent volatility, recent cross count, stop distance, stop distance ATR, and stop distance percent. A hybrid score can test whether a combination of these known-at-entry fields identifies a low-quality tail better than one-variable whitebox gates.

## 6. Ranked Hybrid Mutation Queue

1. **Entry-quality conservative size modifier.** At entry time, score the setup using decision-time features and reduce risk/quantity for the lowest-quality score band rather than vetoing the trade. This is first because hard vetoes destroyed activity, while a size modifier can preserve rotation and lower exposure to weak candidates.

2. **Entry-quality veto only for the worst score tail.** This waits because veto behavior already proved dangerous with whitebox gates. It may be tested later only if the score separates an extreme bad tail without removing the economic engine.

3. **Reverse-flip quality score.** Score only entries that occur after a same-bar reverse. This waits because post-reverse entries are net positive overall, so the first hybrid should learn general entry quality before touching the most delicate mechanism.

4. **Regime-context score.** Score market context by volatility/chop/time state and reduce risk in low-expectancy regimes. This waits because the current evidence localizes the weakness at candidate-entry quality more directly than at broad regimes.

## 7. Chosen First Hybrid Role

The first hybrid role is a conservative position-size modifier at entry time. The whitebox engine still decides whether a trade exists, its direction, stop, and exits. The hybrid layer only computes an entry-quality score and applies a limited risk multiplier to the lowest-quality score band.

The first offline experiment should not delete trades. It should simulate, for example, `1.0x` size for normal/high-score entries and `0.5x` size for the bottom score band. A later live-engine version can expose this as explicit parameters such as `hybrid_entry_quality_sizing_enabled`, `hybrid_entry_quality_score_threshold`, and `hybrid_entry_quality_low_score_risk_mult`.

## 8. Feature Contract

Allowed decision-time features are those present in `entry_features` at the candidate entry:

- setup identity: `side`, `weekday`, `utc_hour`, `month`
- moving-average context: `fast_sma`, `slow_sma`, `fast_minus_slow`, `normalized_ma_distance`, `fast_slope`, `slow_slope`
- volatility and recent path: `atr`, `atr_pct`, `recent_return_20`, `recent_range_20`, `recent_volatility_20`
- chop/noise context: `recent_cross_count`
- risk geometry: `stop_distance`, `stop_distance_atr`, `stop_distance_pct`

These are known at entry because they are derived from prior/current bar state and the candidate fill/stop calculated by the parent. Leakage risks are explicit: do not use future `reason`, future `net_pnl`, future `mfe_r`, future `mae_r`, final `bars_held`, future stop movement, or any post-entry outcome as input features.

## 9. Label Contract

The first label should be binary and entry-quality oriented, not a market prediction. A defensible label is:

```text
worthwhile_trade = 1 if net_pnl > 0 or mfe_r >= 0.25
worthwhile_trade = 0 if net_pnl < 0 and mfe_r < 0.20
ambiguous otherwise
```

Ambiguous trades should either be excluded from classifier training or assigned low sample weight. This label matches the role: the model is not predicting the whole market; it is estimating whether the parent’s candidate entry has enough quality to deserve full risk.

For offline accounting, also retain continuous outcomes: `net_pnl`, `return_on_equity_pct`, `mfe_r`, `mae_r`, `reason`, and `bars_held`. They are diagnostics and labels only, never features.

## 10. Model Contract

Use a transparent CPU-friendly model. The first model should be logistic regression with standardized numeric features and one-hot categorical features, or an even simpler scorecard if linear coefficients are unstable. No deep learning, no GPU, no full-market forecasting model, and no opaque model as the first experiment.

The model output is a calibrated probability or score. It should be converted into a simple decision rule for offline preview: bottom score band receives reduced size; all other trades retain parent size. A shallow decision tree may be a fallback only if logistic regression cannot express any useful separation and the tree remains auditable.

## 11. Validation Contract

Validation must be chronological. Use walk-forward splits across the 2017-2026 dataset, such as train on earlier years and validate/test on later years, rolling forward. Do not random-split trades.

Every split must compare the hybrid-sized child against the frozen whitebox parent. Report retained trade count, reduced-size trade count, effective exposure reduction, Net PnL, PF, max drawdown, expected payoff, win rate, side decomposition, exit decomposition, yearly decomposition, daily Sharpe, daily Sortino, worst daily return, Calmar, and buy-and-hold comparison.

The hybrid layer must not survive by shrinking nearly everything. A conservative first target is to reduce size on roughly the worst `10%-25%` of score-ranked trades, then test whether that improves drawdown or risk-adjusted metrics without materially reducing Net PnL.

## 12. Acceptance Rule

Accept the offline hybrid preview only if it improves risk-adjusted evidence without destroying the parent. Minimum survival evidence: Net PnL preserved within a tight tolerance or improved, max drawdown improved, daily Sharpe/Sortino preserved or improved, worst daily return improved, Calmar preserved or improved, both sides still profitable, stop-exit engine still dominates, and the size-reduced share remains credible rather than most trades.

For promotion beyond offline preview, the same logic must be implemented inside the live backtest engine as explicit strategy parameters and rerun against the same frozen parent. Offline success alone is not promotion.

## 13. Rejection Rule

Reject the hybrid if it uses leaky features, if it only works in-sample, if it deletes or shrinks most trades, if it damages the stop-managed profit engine, if it concentrates gains in a small period, if it harms one side materially, if the live-engine proxy cannot reproduce offline results, or if the model cannot be explained as a bounded entry-quality size modifier.

## 14. Live-Engine Promotion Contract

Offline preview is only the first gate. If the scorecard/logistic experiment survives, convert it to explicit backtest-engine parameters:

```text
hybrid_entry_quality_sizing_enabled
hybrid_entry_quality_score_threshold
hybrid_entry_quality_low_score_risk_mult
hybrid_entry_quality_coefficients/version
```

The live engine must compute the same decision-time features at entry, apply the risk multiplier before quantity is finalized, expose the branch in Mutation Engine, and report score bands, reduced-size counts, side splits, and outcome diagnostics. If the live implementation loses the offline edge, keep it disabled or reject it.

## 15. Required Data Export

Create a trade-level export with one row per executed parent trade. Required columns:

- grouping keys: `trade_id`, `entry_ts`, `exit_ts`, `year`, `month`, `weekday`, `utc_hour`
- decision-time features: all `entry_features` fields listed above, plus `direction`, `entry_price`, `stop_price`, `entry_notional`, `entry_exposure_pct`, `initial_risk_pct`, `sizing_mode`
- labels/outcomes: `net_pnl`, `gross_pnl`, `return_on_equity_pct`, `mfe_r`, `mae_r`, `bars_held`, `reason`, `win_loss`
- diagnostics only: side/year/exit buckets and original parent metrics for comparison

Mark clearly which columns are features and which are labels. Feature generation must freeze the parent run first so the model trains on parent candidates, not on a changing child.

## 16. First Hybrid Experiment

Export parent trade rows from `run_f723d4f17c39`. Train a chronological logistic-regression entry-quality score using only decision-time features. In each validation/test fold, sort trades by score and apply a simulated `0.5x` risk multiplier to the bottom score band, starting with the bottom `20%`. Compare the resulting equity and trade diagnostics against the frozen parent.

Do not code the live strategy branch until the offline preview survives at least one chronological validation.

## 17. Fallback Candidate If First Test Fails

If conservative sizing fails, test a narrower post-reverse entry-quality score as the fallback. That branch should score only entries that immediately follow a reverse exit, because those entries are net positive overall but contain both a huge stop-win subset and a large reverse-loss subset. It must still begin as a size modifier, not a hard veto.

## 18. Final Routing

Route: proceed to the first hybrid experiment from the queue. The next task is to improve report/export generation or create a one-off export for parent trade rows, then run an offline chronological logistic-regression entry-quality sizing preview. Do not route to paper trading or production. Do not implement a live hybrid branch until the offline experiment survives.
