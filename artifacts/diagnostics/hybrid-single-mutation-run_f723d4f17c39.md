# Hybrid Single Mutation - run_f723d4f17c39

## 1. Frozen White-Box Parent Contract

The frozen parent is `run_f723d4f17c39`, version `ver_cfbfb3577dd3`, family `xauusd_ghl_dc`, asset `XAUUSD`, venue `IC Markets MT5`, timeframe `30m`, dataset `ds_4e109af56413`. It is the XAUUSD transplant of BTC winner `run_a871be4f8292`, using `ma_cross_atr_stop_v1`.

The parent is a very short-cycle whitebox strategy: `fast_len=1`, `slow_len=3`, `entry_mode=crossover_plus_pullback`, both long and short enabled, ATR stop `atr_len=52`, `stop_mult=3.3`, breakeven enabled at `0.25R` and locked at `1.0R`, `sizing_mode=mt5_fixed_risk_lot`, `initial_capital=5000`, `risk_pct=0.01`, `max_leverage=1.0`, `commission_pct=0.0035`, `slippage_ticks=10`.

Frozen metrics: Net PnL `1243550863.27`, PF `2.9883`, max DD `2.55%`, trades `43747`, expected payoff `28425.97`, win rate `36.86%`, daily Sharpe `12.4154`, daily Sortino `33.0676`, worst daily return `-1.58%`, Calmar `9757142.0151`.

## 2. Why Hybrid Is Justified or Not

Hybrid research is justified because the parent is alive and heavily evidenced, but the simple whitebox repair attempts were too blunt. `reverse_confirmation` improved PF but destroyed too much activity and reduced Net PnL materially. `entry_exposure_gate` also failed because hard exposure thresholds broke the compounding/rotation engine. The remaining task is not another hard gate; it is a narrow scoring layer that reduces participation intensity in weak candidates while preserving the whitebox mechanism.

## 3. Remaining Weakness to Solve

The remaining weakness is entry-quality heterogeneity inside a high-frequency rotation engine. The parent takes many low-quality trades, but hard-coded rules cannot safely identify which ones to delete. Reverse exits are ugly but necessary to rotation. High exposure looks suspicious but hard caps break the strategy. A small entry-quality score can combine several decision-time clues and act softly through sizing rather than replacing the strategy.

## 4. Chosen Hybrid Role

Choose exactly one role: an entry-quality conservative size modifier.

The hybrid layer scores each parent-approved entry at decision time. Low-score entries are not removed in the first experiment; they receive a reduced risk multiplier. The parent still controls signal generation, side, stop, breakeven, reverse behavior, and exit rules.

## 5. Feature Contract

Use only features known at entry:

```text
side
weekday
utc_hour
month
fast_minus_slow
normalized_ma_distance
fast_slope
slow_slope
atr_pct
recent_return_20
recent_range_20
recent_volatility_20
recent_cross_count
stop_distance_atr
stop_distance_pct
entry_exposure_pct
initial_risk_pct
```

Do not use future `net_pnl`, `reason`, `mfe_r`, `mae_r`, `bars_held`, final stop movement, or future returns as features.

## 6. Model Contract

Use logistic regression or a simple scorecard. Prefer logistic regression first because it is transparent, CPU-cheap, and coefficient-auditable. Numeric features should be standardized on the training fold only; categorical features like side/hour/weekday/month can be one-hot encoded. No deep learning, no GPU, no opaque model, and no market-wide prediction target.

## 7. Validation Contract

Validation must be chronological. Use rolling or anchored walk-forward splits across 2017-2026. Train on earlier periods, validate/test on later periods, and compare every hybrid-sized child to the frozen parent over the same test period.

The offline preview should apply a `0.5x` risk multiplier to the bottom score band, starting with the bottom `20%` of scores. It must report parent-vs-child Net PnL, PF, max DD, expected payoff, trade count, effective reduced-size count, side decomposition, exit decomposition, yearly decomposition, daily Sharpe, daily Sortino, worst daily return, Calmar, average exposure, max exposure, and buy-and-hold comparison.

## 8. Acceptance Rule

Accept the offline mutation only if it improves drawdown or daily risk metrics while preserving most of the parent’s Net PnL and activity. A valid win would keep the whitebox engine intact, reduce risk on a bounded minority of trades, preserve both sides, preserve the stop-managed profit bucket, and avoid concentrating improvement in one period.

Do not accept a result that merely improves PF while sacrificing the compounding engine.

## 9. Failure Rule

Fail the mutation if it relies on leaky features, if it only works in-sample, if the bottom-score group is not stable across chronological folds, if it reduces or vetoes too many trades, if Net PnL collapses, if either side is damaged materially, or if the live-engine proxy cannot reproduce the offline result.

## 10. Live-Engine Promotion Contract

Offline success is only a research filter. Promotion requires converting the score into explicit strategy parameters inside the backtest engine:

```text
hybrid_entry_quality_sizing_enabled
hybrid_entry_quality_score_threshold
hybrid_entry_quality_low_score_risk_mult
hybrid_entry_quality_model_version
hybrid_entry_quality_coefficients
```

The engine must compute the same features at entry and apply the multiplier before quantity is finalized. The app must expose the controls in mutation edges and reports must show score-band counts, reduced-size counts, and parent comparison. If the live proxy loses the offline edge, reject or keep disabled.

## 11. First Hybrid Experiment

Create a trade-level export from `run_f723d4f17c39`, train a chronological logistic-regression entry-quality score, and run an offline sizing simulation where the bottom `20%` of score-ranked entries receive `0.5x` risk. Compare against the frozen parent by fold and full-period aggregate.

The first experiment should not delete trades.

## 12. Final Routing

Route: proceed to the first hybrid experiment. The immediate next practical step is to create/export the parent trade-feature table for `run_f723d4f17c39` and run the offline chronological logistic-regression sizing preview. Do not implement the live hybrid branch until the offline experiment survives.
