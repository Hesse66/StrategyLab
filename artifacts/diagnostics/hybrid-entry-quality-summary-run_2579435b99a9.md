# Hybrid Entry-Quality Experiment Summary - run_2579435b99a9

Parent: `run_2579435b99a9`

Contract: `artifacts/diagnostics/hybrid-diagnostics-run_2579435b99a9.md`

## Experiments Run

| Veto Fraction | Experiment | Verdict | Net PnL Delta | PF Delta | DD Delta | Trade Delta |
|---:|---|---|---:|---:|---:|---:|
| 0.15 | `hyb_ef43908803ea` | `rejected_no_edge` | -14910.00 | -0.0378 | 0.00 | -57 |
| 0.10 | `hyb_4234b88b57e0` | `rejected_no_edge` | -13511.56 | -0.0456 | 0.00 | -36 |

## Parent vs Hybrid Metrics

Parent metrics:

- Net PnL: `113504.68`
- PF: `1.5977`
- DD: `5.17%`
- Expected Payoff: `129.57`
- Trades: `876`
- Daily Sharpe: `1.7114`
- Daily Sortino: `1.9770`
- Worst Daily Return: `-1.35%`
- Calmar: `21.9339`

0.15 veto:

- Net PnL: `98594.68`
- PF: `1.5599`
- DD: `5.17%`
- Expected Payoff: `120.38`
- Trades: `819`
- Daily Sharpe: `2.9338`
- Daily Sortino: `5.7535`
- Worst Daily Return: `-1.46%`
- Calmar: `19.0527`

0.10 veto:

- Net PnL: `99993.12`
- PF: `1.5521`
- DD: `5.17%`
- Expected Payoff: `119.04`
- Trades: `840`
- Daily Sharpe: `2.8783`
- Daily Sortino: `5.6811`
- Worst Daily Return: `-1.44%`
- Calmar: `19.3229`

## Veto Quality

The veto did not identify bad entries. It removed net-positive trades.

0.15 veto:

- Vetoed trades: `57`
- Vetoed net PnL: `14910.00`
- Vetoed `gann_state_exit`: `51`, net PnL `18826.26`
- Vetoed `stop`: `5`, net PnL `-3599.08`
- Vetoed `time_exit`: `1`, net PnL `-317.18`

0.10 veto:

- Vetoed trades: `36`
- Vetoed net PnL: `13511.56`
- Vetoed `gann_state_exit`: `34`, net PnL `15432.69`
- Vetoed `stop`: `2`, net PnL `-1921.13`

## Implementation Gap

This first offline experiment is useful as a rejection signal, but it also exposed an export weakness. Several intended GHL+DC decision-time features are missing in the current trade rows and therefore score as `missing`, including:

- `normalized_ma_distance`
- `fast_slope`
- `slow_slope`
- `atr_pct`
- `recent_return_20`
- `recent_range_20`
- `recent_volatility_20`
- `recent_cross_count`
- `stop_distance_atr`

Those feature names were inherited from the MA-cross parent feature contract. The GHL+DC engine currently writes smaller `entry_features`, so the scorecard is relying heavily on coarse timing/month/weekday buckets. That is not enough for a trustworthy hybrid entry-quality conclusion.

## Conclusion

The first offline entry-quality veto branch is rejected. Both `0.15` and `0.10` vetoes reduce net PnL, PF, expected payoff, and Calmar, and they veto mostly profitable future `gann_state_exit` trades.

Do not implement a live hybrid entry-quality gate from these results.

## Next Practical Step

Improve the GHL+DC feature export before testing another hybrid model. Add decision-time GHL+DC features to `entry_features`, then rerun the offline entry-quality diagnostics. If the richer export still vetoes future Gann-state winners, abandon entry-quality veto and move to the fallback regime-context diagnostic.
