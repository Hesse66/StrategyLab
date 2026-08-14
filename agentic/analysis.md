# TgSignalSniper management lab — current state

Implementation and review are complete. The canonical durable contract is in
`docs/tg_signal_management_lab.md`; executable behavior is in `app/tg_*.py`.
The final regression passed 109 tests, and the real browser flow imported a
finalized fixture and replayed its baseline without console errors.

## Boundary

StrategyLab imports completed offline packages only. It never imports MetaTrader or
Telegram libraries, contacts either service, opens an active AutoKraken database,
or changes an AutoKraken file. Every source SQLite file must be a consolidated,
finalized snapshot without WAL/SHM sidecars.

## Existing architecture

The existing `BacktestEngine` generates entries from candle streams and the
`MutationLabService` owns bar-oriented mutations and robustness checks. External
real executions are a different experimental unit, so the new engine is an
independent service. It reuses the repository/artifact conventions and the same
chronological-validation vocabulary without converting executions into bars.

## AutoKraken contract observed

- Tick archive schema version 2.
- Codec `zlib-struct-qddI-v1`; record layout `<qddI`.
- SHA-256 covers the compressed chunk payload.
- Coverage is declared per execution with start/end, status, and gap count.
- Operational migrations currently reach version 19.
- Native broker legs and execution events are persisted separately.
- Exact management configuration and broker symbol economics are not completely
  reconstructible from the operational rows alone.

Therefore a promotion-capable package requires an exact policy registry keyed by
`management_policy_version`, broker-originated symbol specifications, and the
cost/deal evidence needed for net counterfactual P&L. Missing evidence remains
importable for research but is fail-closed for promotion.

## Durable decisions

- Snapshots and experiments are content-addressed and immutable.
- Tick order is `(time_msc, source_ordinal, ticket, leg)`; source ordinal is the
  decoded archive order, never a price-derived sort.
- Archive-declared complete coverage with zero gaps is authoritative even through
  natural no-tick intervals. Broken chunks, invalid checksums, uncovered events,
  or outcome-changing ambiguity censor an operation.
- Baseline parity excludes manual, anomalous, censored, and cost-incomplete rows.
- Per-operation tolerance is `max(0.01 USD, 0.01 * initial_risk_amount)`.
- Aggregate tolerance is `max(1 USD, 0.0025 * sum(abs(actual_net_pnl)))`.
- Development uses the chronological first 75%; the final 25% is untouched.
- Promotion requires higher net gross profit and lower net gross loss in both
  aggregate walk-forward OOS and final holdout.
- Assets remain independent; timeframe and lane are diagnostic dimensions only.
