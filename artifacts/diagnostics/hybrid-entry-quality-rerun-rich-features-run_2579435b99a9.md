# Hybrid Entry-Quality Rerun With Rich GHL+DC Features - run_2579435b99a9

Parent: `run_2579435b99a9`

Reason for rerun: the first entry-quality experiments used a feature export inherited from the MA-cross parent. Several intended GHL+DC features were missing. The engine now exports decision-time GHL+DC features, and the hybrid experiments were rerun.

## Feature Export Fix

The GHL+DC engine now exports populated entry features including:

- `atr_pct`
- `normalized_ma_distance`
- `recent_return_20`
- `recent_range_20`
- `recent_volatility_20`
- `recent_cross_count`
- `stop_distance_atr`
- `donchian_breakout_distance_atr`
- `breakout_age_bars`
- `bars_since_gann_flip`
- Gann SMA slope fields
- Donchian channel width and breakout distance fields

The rerun exports show `0` missing values for the scorecard feature set.

## Rerun Results

| Veto Fraction | Experiment | Auto Verdict | Net PnL Delta | PF Delta | DD Delta | Trade Delta |
|---:|---|---|---:|---:|---:|---:|
| 0.15 | `hyb_2a938dc30123` | `hybrid_candidate` | -1843.57 | +0.0216 | +0.50 | -53 |
| 0.10 | `hyb_3080f1c98652` | `hybrid_candidate` | -1398.69 | +0.0103 | +0.44 | -35 |

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

0.15 veto metrics:

- Net PnL: `111661.11`
- PF: `1.6193`
- DD: `5.67%`
- Expected Payoff: `135.68`
- Trades: `823`
- Daily Sharpe: `3.0968`
- Daily Sortino: `6.2055`
- Worst Daily Return: `-1.36%`
- Calmar: `19.6967`

0.10 veto metrics:

- Net PnL: `112105.99`
- PF: `1.6080`
- DD: `5.61%`
- Expected Payoff: `133.30`
- Trades: `841`
- Daily Sharpe: `3.0492`
- Daily Sortino: `6.1323`
- Worst Daily Return: `-1.36%`
- Calmar: `19.9876`

## Veto Quality

The richer feature export materially improved the experiment versus the first run, but it still does not satisfy the 04-1 acceptance contract.

0.15 veto:

- Vetoed trades: `53`
- Vetoed net PnL: `1843.57`
- Vetoed `gann_state_exit`: `46`, net PnL `4819.64`
- Vetoed `stop`: `7`, net PnL `-2976.07`

0.10 veto:

- Vetoed trades: `35`
- Vetoed net PnL: `1398.69`
- Vetoed `gann_state_exit`: `32`, net PnL `2613.66`
- Vetoed `stop`: `3`, net PnL `-1214.97`

## Interpretation

The richer export fixed the data quality issue, but the entry-quality veto still fails the parent comparison that matters. It slightly improves PF and expected payoff, and it greatly improves daily Sharpe/Sortino in the offline filtered-equity accounting, but it lowers net PnL, increases max drawdown, worsens worst daily return slightly, and reduces Calmar.

Most importantly, the veto still removes net-positive future `gann_state_exit` trades. That violates the parent-protection rule: do not damage the right-tail continuation engine to make trade-level optics look cleaner.

The app's automatic `hybrid_candidate` verdict is too permissive for this research contract because it accepts a PF improvement despite lower net PnL and Calmar. Under the 04-1 acceptance rule, this branch is rejected.

## Routing

Reject live-engine implementation of the entry-quality veto branch.

Next practical route: fallback regime-context diagnostic focused on the weak walk-forward fold, not another entry-quality veto. If that fallback also fails, freeze `ver_9a0ca0f8616c` as a strong research parent with `needs_review` robustness rather than forcing a hybrid overlay.
