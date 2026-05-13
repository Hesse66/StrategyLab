# Full-Whitebox Single Mutation After Reverse Rejection - run_f723d4f17c39

## 1. Frozen Parent Contract

The frozen parent remains `run_f723d4f17c39`, version `ver_cfbfb3577dd3`, family `xauusd_ghl_dc`. This is the XAUUSD M30 transplant of BTC winner `run_a871be4f8292`, tested on dataset `ds_4e109af56413` for `XAUUSD` at `IC Markets MT5` / `30m`.

The engine is `ma_cross_atr_stop_v1`. The current live parameters are `ma_kind=sma`, `fast_len=1`, `slow_len=3`, `entry_mode=crossover_plus_pullback`, `max_no_cross=4`, long and short enabled, `atr_len=52`, `stop_mult=3.3`, breakeven enabled with `breakeven_trigger_mfe_r=0.25` and `breakeven_lock_r=1.0`, `sizing_mode=mt5_fixed_risk_lot`, `initial_capital=5000`, `risk_pct=0.01`, `max_leverage=1.0`, `min_lot=0.01`, `lot_step=0.01`, `commission_pct=0.0035`, and `slippage_ticks=10`.

The frozen parent metrics are Net PnL `1243550863.27`, return `24871017.27%`, PF `2.9883`, max drawdown `2.55%`, expected payoff `28425.97`, trades `43747`, win rate `36.86%`, daily Sharpe `12.4154`, daily Sortino `33.0676`, worst daily return `-1.58%`, Calmar `9757142.0151`, and buy-and-hold outperformance `24870753.6%`.

The previously proposed `reverse_confirmation` mutation was implemented as an active preview and rejected. Its first preview changed Net PnL from `1243550863.27` to `1002003408.57`, PF from `2.9883` to `3.1478`, drawdown from `2.55%` to `3.00%`, and trades from `43747` to `25437`. Small variants also failed to beat the frozen parent on Net PnL. Therefore this new mutation must not repeat reverse-exit blocking.

## 2. Current Causal Identity

The parent is a short-cycle XAU managed-trade engine, not a direct BTC trend continuation clone anymore. It uses very fast SMA structure, high activity, MT5-style fixed-risk lot sizing, and breakeven/ATR stop management. It makes money through payoff asymmetry rather than hit rate: the win rate is only `36.86%`, but the average win/loss ratio is `5.1196`, so the approximate breakeven win rate is only `16.34%`.

Reverse exits look ugly in isolation, but they are partly the cost of rotating into the next trade. In the raw trade sequence, every reverse exit is followed by a same-bar opposite entry. Those `29395` same-bar post-reverse entries produce `808278267.12` net PnL. Their stop-exit subset produces `1179561227.61`, while their later reverse-exit subset loses `-371277713.90`. This means reverse churn cannot simply be blocked without damaging the rotation engine that funds the strategy.

## 3. Evidence Behind the Mutation

The next evidenced weakness is not exit timing; it is capital efficiency at high intended exposure.

Entry exposure decomposition from the saved trade rows shows that low-exposure trades fund most of the system, while high-exposure trades consume a large amount of activity for modest contribution:

| Entry Exposure Band | Trades | Net PnL | Win Rate |
|---|---:|---:|---:|
| `0% <= exposure < 10%` | `26828` | `1060617711.17` | `37.87%` |
| `10% <= exposure < 25%` | `4252` | `114759434.35` | `36.52%` |
| `25% <= exposure < 50%` | `670` | `35717267.82` | `37.76%` |
| `50% <= exposure < 75%` | `759` | `11310834.37` | `34.78%` |
| `75% <= exposure < 100%` | `11233` | `21159103.11` | `34.63%` |
| `exposure >= 100%` | `5` | `-13487.55` | `40.00%` |

The `75%-100%` band contains `11233` trades, roughly a quarter of all activity, but contributes only `21159103.11` net PnL, less than two percent of the parent Net PnL. This is a cleaner mutation target than reverse exits because it attacks capital-efficiency drag without interfering directly with the same-bar reversal mechanism that appears to feed later winners.

## 4. Chosen Single Mutation

Implement one mutation: a high-entry-exposure admission gate.

This is a risk-admission rule, not an ordinary parameter sweep. The gate evaluates the intended entry exposure after the engine has computed fill, stop, quantity, and entry notional, but before opening the position. If intended exposure exceeds a threshold, the entry is skipped unless the strategy later proves that a narrow exception is needed. The first test should be simple and active: block only very high intended exposure entries.

The mutation preserves the parent’s economic engine because it does not touch reverse exits, stop exits, breakeven movement, long/short permissions, or the MA entry family. It only asks whether the capital-hungry tail of entries is worth taking.

## 5. Why Competing Mutations Wait

`reverse_confirmation` waits because it was already tested and rejected. Blocking early reversals removed too much activity and reduced Net PnL by `241547454.70` in the first active preview.

Time-decay mutations wait because this run has `0` time-decay exits and `0` hybrid time-decay triage exits.

Side gates wait because both long and short sides are profitable: long net PnL is `720822865.01`, short net PnL is `522727998.26`.

More ordinary optimization waits because this phase is not another broad parameter sweep. The parent already has a strong optimized parameter state; the next useful question is whether a simple, auditable risk-admission rule can improve capital efficiency without destroying trade evidence.

## 6. Implementation Brief

Add an entry exposure gate inside `ma_cross_atr_stop_v1`, evaluated after `_position_quantity(...)` and `entry_notional` are computed for a candidate entry, but before creating `Position`.

The rule needs only decision-time-safe values:

- `equity`
- `fill`
- `stop`
- `quantity`
- `entry_notional`
- `entry_exposure_pct = entry_notional / equity * 100`
- `direction`
- current bar timestamp for reporting/grouping only

Rule state:

```text
entry_exposure_gate_enabled
entry_exposure_gate_max_pct
```

Decision:

```text
if entry_exposure_gate_enabled:
    intended_exposure_pct = (entry_notional / equity) * 100
    if intended_exposure_pct > entry_exposure_gate_max_pct:
        skip the entry
        increment entry_exposure_gate_blocks
        increment side-specific block counter
```

This must be evaluated separately for long and short entries at the point where quantity is already known. It must not alter existing trade exits. It must not use future trade outcome, future MFE/MAE, or final duration. Existing saved versions must upgrade safely with the gate disabled by default.

Reports should add:

```text
entry_exposure_gate_blocks
entry_exposure_gate_long_blocks
entry_exposure_gate_short_blocks
entry_exposure_gate_max_pct
```

For future diagnostics, report generation should eventually include entry-exposure band decomposition, because this mutation was chosen from that evidence.

## 7. New Parameters and Mutation Space

Add parameters:

```json
{
  "entry_exposure_gate_enabled": false,
  "entry_exposure_gate_max_pct": 75.0
}
```

Expose mutation metadata:

```json
[
  {
    "kind": "white_box",
    "lever": "entry_exposure_gate_enabled",
    "path": "parameters.entry_exposure_gate_enabled",
    "priority": 90,
    "values": [true, false],
    "search_mode": "values_only",
    "rationale": "Enable a decision-time gate that rejects entries whose intended exposure is too high for the XAU transplant parent."
  },
  {
    "kind": "white_box",
    "lever": "entry_exposure_gate_max_pct",
    "path": "parameters.entry_exposure_gate_max_pct",
    "priority": 89,
    "values": [60.0, 75.0, 90.0],
    "search_mode": "range",
    "search_min": 50.0,
    "search_max": 100.0,
    "search_step": 5.0,
    "rationale": "Tune the maximum intended entry exposure allowed before a candidate trade is skipped."
  }
]
```

## 8. First Unsaved Preview

Run this active first preview:

```json
{
  "entry_exposure_gate_enabled": true,
  "entry_exposure_gate_max_pct": 75.0
}
```

The first preview should be judged against frozen `run_f723d4f17c39` on the same dataset `ds_4e109af56413`. It should not include any reverse-confirmation overrides.

## 9. Post-Survival Optimization Plan

If the active first preview survives, optimize only `entry_exposure_gate_max_pct` first over `50%` to `100%` in `5%` steps. Do not run `Optimize all` until this rule family proves it can beat the parent.

If the best threshold is near `100%`, the rule is probably weak or inert. If the best threshold is very low and deletes most trades, it should be rejected as an activity-collapse artifact unless portfolio-period evidence clearly improves.

## 10. Acceptance Rule

Accept the mutation only if it improves the frozen parent without hollowing out the strategy. The child should preserve most of the parent’s activity, preferably at least `70%` of the `43747` trades unless the removed trades are demonstrably low-contribution exposure tail; improve or preserve Net PnL; keep PF near or above `2.9883`; improve or preserve max drawdown; keep both long and short sides profitable; preserve the stop-managed profit engine; and keep daily Sharpe, daily Sortino, worst daily return, Calmar, average exposure, max exposure, and initial-risk diagnostics acceptable.

The strongest success case would be a modest trade-count reduction, lower max/average exposure, stable or better Net PnL, and lower drawdown. A PF-only improvement is not enough.

## 11. Rejection Rule

Reject the mutation if it reduces Net PnL materially, deletes too much of the evidence base, damages the stop-exit profit engine, concentrates gains in one recent period, worsens daily portfolio metrics, or merely improves PF by refusing a large number of trades. Reject it immediately if the implementation uses realized trade outcome or any future value to decide whether exposure was acceptable.

## 12. Final Routing

Route: implement `entry_exposure_gate` as the next single active whitebox mutation for `ver_cfbfb3577dd3` / `run_f723d4f17c39` on `ds_4e109af56413`. This is the correct next step after rejecting `reverse_confirmation`. Do not repeat `03-1` yet; the existing diagnostics plus rejection evidence are sufficient for this next one-mutation test.
