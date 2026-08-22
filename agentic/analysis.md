# Current state

The offline TgSignalSniper management domain is implemented in `app/tg_*.py`;
its durable contract is `docs/tg_signal_management_lab.md`. It has no MT5,
Telegram, AutoKraken, demo/live, or automatic-promotion connector.

Finalized packages preserve immutable operational records, broker-native deal
costs, symbol economics, and checksummed BID/ASK tick chunks. The unchanged
parent baseline uses exact broker deals; candidate and stress policies use exact
tick replay. Post-close candidates may continue only through the archive's
declared terminal horizon. Missing coverage, unresolved ordering, incomplete
horizons, or open volume at the horizon are censored.

The versioned importer accepts AutoKraken operational migrations 16–20.
Migration 20 preserves venue, quote, translation, venue order/position identity,
and provider geometry as diagnostics. Populated migration-20 provider geometry is
canonical for targets and initial provider stop, while `entry_actual` remains the
replay entry; migrations 16–19 retain their legacy frozen interpretation.

Every closed operation in the cohort participates regardless of its historical
version. Immutable policy/configuration versions are diagnostic strata, never
`VERSION_SET_MISMATCH` filters or a way to improve metrics by removing trades.
Chronological 75/25 validation reserves holdout for exactly one final candidate;
all search, family selection, equivalence bootstrap, and parameter decisions use
development and walk-forward OOS only.

The replay supports provider-original targets, fixed-R target geometry, and
bounded joint target/management candidates. Any invalid target at fill, new
censoring, missing broker target-normalization contract, or change in the
comparable operation set closes promotion. No production policy is approved or
published by StrategyLab.
