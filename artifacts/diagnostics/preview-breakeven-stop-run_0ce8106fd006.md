# Unsaved Preview - Breakeven Stop on run_0ce8106fd006

Frozen parent: `run_0ce8106fd006`

Dataset: `ds_4e109af56413`

Candidate parameters:

```json
{
  "breakeven_stop_enabled": true,
  "breakeven_trigger_mfe_r": 0.75,
  "breakeven_lock_r": 0.0
}
```

## Result

The first active phase-3 candidate did not survive comparison against the frozen parent.

| Metric | Frozen Parent | Unsaved Preview | Delta |
|---|---:|---:|---:|
| Net PnL | 90923.34 | 78008.06 | -12915.28 |
| Return % | 90.92 | 78.01 | -12.91 |
| Profit Factor | 1.4079 | 1.4441 | +0.0362 |
| Expected Payoff | 90.02 | 77.01 | -13.01 |
| Total Trades | 1010 | 1013 | +3 |
| Daily Sharpe | 1.4130 | 1.3616 | -0.0514 |
| Daily Sortino | 1.6192 | 1.6448 | +0.0256 |
| Worst Daily Return % | -1.35 | -1.35 | 0.00 |
| Calmar | 16.8553 | 15.3147 | -1.5406 |
| Outperformance % | -172.61 | -185.52 | -12.91 |
| Calmar Delta | 6.7048 | 5.1643 | -1.5405 |

## Exit Evidence

| Exit Reason | Trades | Net PnL |
|---|---:|---:|
| gann_state_exit | 565 | 189084.56 |
| stop | 224 | -109413.87 |
| breakeven_stop | 223 | -1398.18 |
| time_exit | 1 | -264.45 |

Diagnostics:

- Breakeven stop moves: `515`
- Breakeven stop exits: `223`
- Stop exits: `224`
- Gann-state exits: `565`

## Interpretation

The rule does what it was designed to do mechanically: it converts many full stop losses into near-flat `breakeven_stop` exits and reduces normal stop damage. However, it also materially reduces the Gann-state winner bucket, from the frozen parent's `734` Gann-state exits and `230713.98` net PnL to `565` exits and `189084.56` net PnL.

That tradeoff is not acceptable for the first candidate. The preview improves profit factor, but it lowers net PnL, expected payoff, daily Sharpe, Calmar, and buy-and-hold outperformance. This is exactly the rejection pattern described in the diagnostics: the rule cleans up stop optics while cutting too much right-tail continuation.

## Routing

Reject this active breakeven first candidate. Do not promote it and do not optimize it broadly as if it had survived.

The next whitebox step should be a more selective failed-entry triage or a later/higher-threshold breakeven ablation only if new diagnostics can prove it will avoid damaging the Gann-state right tail.
