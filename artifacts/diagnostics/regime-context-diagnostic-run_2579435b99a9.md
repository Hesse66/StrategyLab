# Regime-Context Diagnostic - run_2579435b99a9

## Frozen Parent

The frozen parent is `run_2579435b99a9`, version `ver_9a0ca0f8616c`, family `xauusd_ghl_dc`, engine `ghl_dc_breakout_v1`, asset `XAUUSD`, venue `IC Markets MT5`, timeframe `M30`, dataset `ds_4e109af56413`.

This is the full-whitebox time-risk child of `run_0ce8106fd006`. It keeps the translated GHL+DC breakout engine and adds the active UTC time-risk block:

- `time_risk_filter_enabled=true`
- `time_risk_block_utc_hours=[1, 7, 12, 14, 21]`
- `time_risk_block_weekdays=[]`
- `breakeven_stop_enabled=false`

Frozen parent metrics:

| Metric | Value |
|---|---:|
| Net PnL | 113,504.68 |
| Profit Factor | 1.5977 |
| Max Drawdown | 5.17% |
| Expected Payoff | 129.57 |
| Trades | 876 |
| Daily Sharpe | 1.7114 |
| Daily Sortino | 1.9770 |
| Worst Daily Return | -1.35% |
| Calmar | 21.9339 |

The parent passed cost stress `3/3` and walk-forward `3/4`. Its unresolved robustness weakness is one chronological fold from `2022-02-02 11:00 UTC` to `2024-03-18 11:00 UTC`, where the strategy remains profitable but weaker: approximately `8,722.55` net PnL, `1.1923` PF, `209` trades, and daily Sortino below the robustness threshold.

## Question Tested

After the first hybrid entry-quality veto failed, this diagnostic tested whether the remaining weakness could support a narrow regime-context hybrid or whitebox gate. The test looked for decision-time-safe feature pockets that were specifically poor in the weak 2022-2024 fold and sufficiently stable outside that fold to justify a future rule.

The export used enriched GHL+DC entry features generated at entry time, including volatility context, recent returns/range, moving-average distance and slopes, Donchian channel context, breakout age, bars since Gann flip, UTC hour, weekday, and month. Outcome fields such as exit reason, MFE, MAE, duration, and PnL were used only for diagnostics, not as decision-time features.

## Chronological Fold Evidence

| Fold | Period | Trades | Net PnL | PF | Bad Outcome Rate |
|---|---|---:|---:|---:|---:|
| Fold 1 | 2017-11-02 to 2019-12-18 | 196 | 12,604.45 | 1.4951 | 29.59% |
| Fold 2 | 2019-12-18 to 2022-02-02 | 238 | 17,201.10 | 1.3304 | 28.15% |
| Fold 3 | 2022-02-02 to 2024-03-18 | 209 | 8,722.55 | 1.1923 | 30.14% |
| Fold 4 | 2024-03-18 to 2026-05-01 | 233 | 74,976.58 | 2.1189 | 24.46% |

Fold 3 is real weakness, but not a collapse. It still makes money, keeps a credible trade count, and does not show a simple "do not trade this market state" signature. The biggest distinction is not that volatility or trend structure disappears; fold 3 sits between earlier and later regimes on most median features. Fold 4 is simply much more productive while sharing several directionally similar feature ranges.

## Candidate Bucket Findings

The scan found several fold-3-negative pockets. Examples:

| Candidate Pocket | Fold 3 Evidence | Outside Fold 3 Evidence | Interpretation |
|---|---:|---:|---|
| High `atr_pct` bucket | 61 trades, -3,186.33 net, 0.7866 PF | 158 trades, +23,253.23 net, 1.6846 PF | Weak only in fold 3; dangerous as a global volatility gate. |
| Mid `recent_return_20` bucket | 45 trades, -5,268.20 net, 0.5398 PF | 169 trades, +9,192.07 net, 1.2594 PF | Real fold-3 damage, but outside sample still positive. |
| High `recent_return_20` bucket | 54 trades, -3,343.89 net, 0.7404 PF | 165 trades, +24,485.59 net, 1.6894 PF | A global momentum-context veto would likely cut important winners. |
| Mid/high `fast_slope` buckets | Negative in fold 3 | Positive outside fold 3 | Not stable enough for a general slope regime gate. |
| Selected weekday/month buckets | Negative in fold 3 | Strongly positive outside fold 3 | Calendar pockets look fold-specific and overfit-prone. |

The useful conclusion is negative: the weak fold can be described after the fact, but the available decision-time features do not yet isolate a stable, portable regime context. The same pockets that hurt in 2022-2024 often contribute positively in the rest of the sample.

## Hybrid Mutation Decision

Do not implement a regime-context gate from this diagnostic.

A valid phase-4 branch would need to preserve the whitebox parent while reducing weak-fold exposure. The available bucket evidence does not satisfy that bar. A model or rule trained to avoid the weak fold would likely learn a period-specific filter rather than a robust decision-time relationship. That would risk deleting the strategy's economic engine in other years, especially because fold 4 contains strong gains in feature ranges that overlap the weak-fold candidates.

## Practical Conclusion

The current best parent remains `run_2579435b99a9` / `ver_9a0ca0f8616c`. It is a strong research parent, not a production-ready parent. Its status should remain `needs_review` because walk-forward robustness is `3/4`, even though cost stress is `3/3`.

The failed entry-quality veto and this failed regime-context diagnostic both point to the same conclusion: there is no obvious next narrow hybrid layer justified by the current evidence. Phase 4 should not be forced.

## Operational Caveat

The cost-stress result should be read carefully. If the strategy cost assumptions still use `commission_pct=0.0`, then `commission_2x` is effectively a no-op. Slippage stress remains informative, but commission stress is not meaningful until the IC Markets XAUUSD cost model is represented with a non-zero commission or equivalent spread/fee assumption.

## Final Routing

Route: skip further hybrid mutation for now and freeze `run_2579435b99a9` as the current research dossier candidate, with robustness status `needs_review`.

The next practical step is to improve the cost model / robustness dossier before any paper-trading discussion: represent IC Markets XAUUSD execution costs more realistically, rerun robustness, and only then decide whether the parent remains a robustness candidate or needs repair.
