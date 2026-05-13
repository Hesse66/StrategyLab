# Full-Whitebox Single Mutation - run_f723d4f17c39

## 1. Frozen Parent Contract

The frozen parent is `run_f723d4f17c39`, version `ver_cfbfb3577dd3`, family `xauusd_ghl_dc`. It is the XAUUSD M30 transplant of BTC winner `run_a871be4f8292`, optimized on `ds_4e109af56413` for `XAUUSD` at `IC Markets MT5` / `30m`.

The engine is `ma_cross_atr_stop_v1`. Entry style is `crossover_plus_pullback`, `ma_kind=sma`, `fast_len=1`, `slow_len=3`, `max_no_cross=4`, both long and short are enabled, ATR stop uses `atr_len=52` and `stop_mult=3.3`, breakeven is enabled with `breakeven_trigger_mfe_r=0.25` and `breakeven_lock_r=1.0`, sizing is `mt5_fixed_risk_lot` with `initial_capital=5000`, `risk_pct=0.01`, `max_leverage=1.0`, `contract_size=100`, `min_lot=0.01`, `lot_step=0.01`, `commission_pct=0.0035`, and `slippage_ticks=10`.

The verdict is `promotion_candidate`. Frozen metrics are Net PnL `1243550863.27`, return `24871017.27%`, PF `2.9883`, max drawdown `2.55%`, expected payoff `28425.97`, trades `43747`, win rate `36.86%`, daily Sharpe `12.4154`, daily Sortino `33.0676`, worst daily return `-1.58%`, Calmar `9757142.0151`, and buy-and-hold outperformance `24870753.6%`.

## 2. Current Causal Identity

This parent is no longer a direct copy of the BTC intraday identity. After transplantation to XAU and optimization, it behaves as a very short-cycle managed-trade strategy. It enters frequently, holds briefly, and makes money when breakeven/ATR stop management captures favorable movement. Median duration is `2` bars, 75th percentile is `3` bars, and the system took `43747` trades.

The strategy does not win by being right most of the time. It wins because average winners are much larger than average losers. The win rate is only `36.86%`, but the average win/loss ratio is `5.1196`, making the approximate breakeven win rate `16.34%`.

## 3. Evidence Behind the Mutation

The clearest weakness is not time-decay, side selection, or ordinary parameter length. Time-decay exits are `0`. Both sides are profitable: longs make `720822865.01`, shorts make `522727998.26`. The dominant defect is reverse exits.

Reverse exits: `29395` trades, net PnL `-570743749.76`, PF `0.0455`, win rate `6.95%`, average hold `1.75` bars.

Stop exits: `14351` trades, net PnL `1814299859.62`, PF `67.0953`, win rate `98.1%`, average hold `2.76` bars.

The reverse problem is symmetric and persistent. Long reverse exits lose `-318334232.32`; short reverse exits lose `-252409517.44`. Reverse exits lose in every year, while stop exits make money in every year. The damaged trades are mostly young: reverse exits held `<=2` bars account for `24557` trades and `-551420719.20` net PnL. Reverse exits with `mfe_r < 0.20` account for `25430` trades and `-545324330.88`.

## 4. Chosen Single Mutation

Implement one mutation: an early reverse-exit confirmation gate.

This rule changes the reverse-exit logic, not an ordinary parameter length. When an opposite MA signal appears while a position is open, the engine should no longer always close immediately for `reason="reverse"`. Instead, for young positions with weak favorable excursion, it should require confirmation before accepting the reverse exit. If the trade is already sufficiently adverse, the reverse exit remains allowed as an escape.

The mutation preserves the economic engine because it does not remove entries, stops, breakeven, both-side trading, or ATR management. It only prevents the most evidenced destructive behavior: early opposite-signal churn before the stop-management engine has had a chance to work.

## 5. Why Competing Mutations Wait

Time-decay confirmation waits because this XAU parent has `0` time-decay exits and `0` hybrid time-decay triage exits. That mutation is irrelevant here.

Side gates wait because both long and short sides are strongly profitable overall, and both sides suffer from the same reverse-exit failure.

Time-risk filtering waits because the current report does not provide UTC-hour reverse-exit decomposition. A time filter may become useful later, but it is not the smallest evidenced rule.

Further parameter tuning waits because phase 3 should test one rule-family mutation against the frozen parent, not keep moving ordinary lengths after the parent already survived baseline optimization.

## 6. Implementation Brief

Add a reverse confirmation rule inside `ma_cross_atr_stop_v1`, evaluated only when `position` exists and the current bar produces an opposite signal:

- long position plus `short_signal`
- short position plus `long_signal`

Evaluate it before the existing reverse close block. The data available at decision time is `bars_held`, current close, entry price, current stop, current position direction, current MFE from `position.max_favorable_excursion`, `initial_risk`, and whether the stop has moved to breakeven. Do not use future exit reason, future MFE/MAE, final trade PnL, or full duration.

Rule state:

```text
reverse_confirmation_enabled
reverse_confirm_max_bars
reverse_confirm_min_mfe_r
reverse_confirm_allow_if_unrealized_r_lte
reverse_confirm_require_no_breakeven_move
```

Decision logic:

```text
if reverse_confirmation_enabled and opposite_signal:
    bars_held = index - position.entry_index
    mfe_r = position.max_favorable_excursion / initial_risk
    unrealized_r = current_unrealized_per_unit / initial_risk
    is_young = bars_held <= reverse_confirm_max_bars
    weak_excursion = mfe_r < reverse_confirm_min_mfe_r
    adverse_escape = unrealized_r <= reverse_confirm_allow_if_unrealized_r_lte
    breakeven_exception = reverse_confirm_require_no_breakeven_move and position.stop_moved_to_breakeven

    suppress_reverse = is_young and weak_excursion and not adverse_escape
    if breakeven_exception:
        suppress_reverse = false
```

If `suppress_reverse` is true, do not close the current position for `reverse`, and also suppress the opposite entry on the same bar so the engine does not flip immediately. This mirrors the current `hybrid_reverse_exit_triage` behavior.

Reports should record:

```text
reverse_confirmation_candidates
reverse_confirmation_exits_allowed
reverse_confirmation_suppressed
reverse_confirmation_suppressed_net_pnl
reverse_confirmation_adverse_escape_allowed
```

Trades closed after one or more suppressed reverse candidates should carry `reverse_confirmation_suppressed` so future diagnostics can see whether suppression later helped or hurt.

## 7. New Parameters and Mutation Space

Add defaults:

```json
{
  "reverse_confirmation_enabled": false,
  "reverse_confirm_max_bars": 2,
  "reverse_confirm_min_mfe_r": 0.20,
  "reverse_confirm_allow_if_unrealized_r_lte": -0.35,
  "reverse_confirm_require_no_breakeven_move": false
}
```

Expose mutation-space metadata:

```json
[
  {
    "kind": "white_box",
    "lever": "reverse_confirmation_enabled",
    "path": "parameters.reverse_confirmation_enabled",
    "priority": 90,
    "values": [true, false],
    "search_mode": "values_only",
    "rationale": "Enable the early reverse-exit confirmation gate for the XAU BTC-transplant parent."
  },
  {
    "kind": "white_box",
    "lever": "reverse_confirm_max_bars",
    "path": "parameters.reverse_confirm_max_bars",
    "priority": 89,
    "values": [1, 2, 3],
    "search_mode": "range",
    "search_min": 1,
    "search_max": 4,
    "search_step": 1,
    "rationale": "Tune how young a position must be before reverse confirmation can suppress an opposite signal."
  },
  {
    "kind": "white_box",
    "lever": "reverse_confirm_min_mfe_r",
    "path": "parameters.reverse_confirm_min_mfe_r",
    "priority": 88,
    "values": [0.10, 0.20, 0.30],
    "search_mode": "range",
    "search_min": 0.05,
    "search_max": 0.50,
    "search_step": 0.05,
    "rationale": "Tune the minimum favorable excursion needed before a young reverse exit is trusted."
  },
  {
    "kind": "white_box",
    "lever": "reverse_confirm_allow_if_unrealized_r_lte",
    "path": "parameters.reverse_confirm_allow_if_unrealized_r_lte",
    "priority": 87,
    "values": [-0.50, -0.35, -0.20],
    "search_mode": "range",
    "search_min": -0.75,
    "search_max": -0.10,
    "search_step": 0.05,
    "rationale": "Keep an adverse escape valve so the confirmation gate does not trap failing trades."
  },
  {
    "kind": "white_box",
    "lever": "reverse_confirm_require_no_breakeven_move",
    "path": "parameters.reverse_confirm_require_no_breakeven_move",
    "priority": 86,
    "values": [false, true],
    "search_mode": "values_only",
    "rationale": "Optionally stop suppressing reverse exits after breakeven management has already taken control."
  }
]
```

## 8. First Unsaved Preview

Run the first preview active, not disabled:

```json
{
  "reverse_confirmation_enabled": true,
  "reverse_confirm_max_bars": 2,
  "reverse_confirm_min_mfe_r": 0.20,
  "reverse_confirm_allow_if_unrealized_r_lte": -0.35,
  "reverse_confirm_require_no_breakeven_move": false
}
```

Compare the unsaved child against frozen `run_f723d4f17c39` on the same `ds_4e109af56413` dataset.

## 9. Post-Survival Optimization Plan

If the active first preview improves the frozen parent without deleting the evidence base, optimize only the new reverse-confirmation levers first. Do not run broad `Optimize all` until the rule family itself has survived. The first optimization pass should search `reverse_confirm_max_bars`, `reverse_confirm_min_mfe_r`, and `reverse_confirm_allow_if_unrealized_r_lte`; only after that should the boolean `reverse_confirm_require_no_breakeven_move` be tested.

After one or two focused passes, compare the best child to frozen parent on net PnL, PF, drawdown, expected payoff, trade count, side decomposition, exit decomposition, yearly decomposition, daily Sharpe, daily Sortino, worst daily return, Calmar, and buy-and-hold comparison.

## 10. Acceptance Rule

Accept the mutation only if it reduces reverse-exit damage while preserving the stop-managed profit engine. The child should improve net PnL or drawdown materially, keep PF near or above `2.9883`, preserve a credible trade count, avoid damaging both long and short sides, keep stop exits strongly profitable, reduce reverse-exit net loss, and avoid concentrating gains in one or two recent years.

Portfolio-period metrics matter more than cosmetic trade-level changes. Daily Sharpe, daily Sortino, worst daily return, Calmar, exposure, and initial risk must stay acceptable.

## 11. Rejection Rule

Reject the mutation if it wins only by deleting most trades, if reverse suppression causes larger stop losses, if stop-exit PnL collapses, if one side is damaged materially, if drawdown rises, if the rule becomes an inert no-op, or if it improves raw PnL while making yearly behavior less robust. Reject it immediately if implementation relies on future MFE/MAE or any value unavailable at the reverse decision bar.

## 12. Final Routing

Route: implement this one mutation as an unsaved preview for `ver_cfbfb3577dd3` / `run_f723d4f17c39` on `ds_4e109af56413`. Do not route to phase 4 yet. Do not keep testing BTC-derived time-decay confirmation levers on this XAU run because they have no active exit bucket here.
