# Hybrid Entry-Quality Offline Experiment - run_f723d4f17c39

## Export

- Trade feature export: `artifacts/exports/hybrid-entry-quality-trades-run_f723d4f17c39.csv`
- Rows: `43747`
- Model: standard-library logistic regression, fold-local standardization, one-hot categorical features.
- Offline action: bottom `20%` score band receives `0.5x` PnL/risk multiplier; no trades are deleted.
- Fold accounting uses the parent equity available at the start of each test year, so drawdown percentages are comparable to the parent path.

## Full Parent Reference

- Net PnL: `1243550863.27`
- PF: `2.9883`
- Max DD %: `2.55`
- Trades: `43747`
- Daily Sharpe: `12.4194`
- Daily Sortino: `33.0827`
- Worst daily return %: `-1.58`

## Walk-Forward Summary

| Fold | Start Equity | Test Trades | Reduced | Parent Net | Child Net | Delta Net | Parent DD% | Child DD% | Parent PF | Child PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017-2020 -> 2021 | 168467168.17 | 5132 | 1026 | 98590103.26 | 88890750.37 | -9699352.89 | 0.22 | 0.23 | 2.5578 | 2.5501 |
| 2017-2021 -> 2022 | 267057271.43 | 5105 | 1021 | 114648271.51 | 102989099.93 | -11659171.58 | 0.2 | 0.15 | 2.6887 | 2.7126 |
| 2017-2022 -> 2023 | 381705542.94 | 5058 | 1011 | 97110142.62 | 88670896.66 | -8439245.96 | 0.12 | 0.12 | 2.6218 | 2.6432 |
| 2017-2023 -> 2024 | 478815685.56 | 5205 | 1041 | 150695693.87 | 137368734.4 | -13326959.47 | 0.1 | 0.09 | 2.8608 | 2.873 |
| 2017-2024 -> 2025 | 629511379.43 | 5169 | 1033 | 331905263.9 | 290668536.7 | -41236727.2 | 0.11 | 0.12 | 3.298 | 3.3218 |
| 2017-2025 -> 2026 | 961416643.33 | 1670 | 334 | 282139219.94 | 242199417.49 | -39939802.45 | 0.34 | 0.34 | 3.5059 | 3.3896 |

## Aggregated Out-Of-Sample 2021-2026

- Start equity: `168467168.17`
- Parent Net PnL: `1075088695.1`
- Child Net PnL: `950787435.55`
- Delta Net PnL: `-124301259.55`
- Parent PF: `3.0321`
- Child PF: `3.0172`
- Parent Max DD %: `0.34`
- Child Max DD %: `0.37`
- Parent Daily Sharpe: `22.8424`
- Child Daily Sharpe: `24.0371`
- Parent Daily Sortino: `75.5724`
- Child Daily Sortino: `64.8841`
- Parent Worst Daily Return %: `-0.13`
- Child Worst Daily Return %: `-0.12`

## Decision

Reject this first offline hybrid sizing preview. It reduces size on a bounded minority of trades, but the score does not preserve parent economics: every chronological test fold loses Net PnL versus the frozen parent, and the aggregate out-of-sample child gives up too much profit for too little risk improvement.

## Next Practical Step

Do not implement this general logistic sizing modifier in the live engine. If phase 4 continues, test the fallback candidate: a narrower post-reverse entry-quality size modifier, because the general entry-quality score was too broad.
