# Active: weekly cell-level optimization

Best-Agent moves: the requested outcome is a weekly optimization whose statistical
selection unit is exactly `(asset, timeframe, side)`, while preserving existing
asset-wide runs only as historical diagnostics.  The chosen perspective combines
John Tukey's exploratory-data separation (do not pool materially different strata)
with David Hand's validation discipline (evidence thresholds remain local to the
population being selected).  This transfers here as exact cell filtering before
chronological split/search, independent WFO/holdout per cell, and truthful sample
eligibility.  Anticipatory corrections are a resumable runner, durable progress,
unique experiment provenance, and no expensive search below 20 operations.

Acceptance contract: CLI and service accept a complete timeframe/side pair; every
cell result contains only matching operations and has a unique experiment identity;
the weekly runner baselines every observed cell, optimizes only cells with at least
20 operations, preserves the 40-operation promotion threshold, resumes safely, and
never presents an aggregate asset result as a cell policy decision.  Existing
asset-wide calls remain compatible and no production policy is automatically
published.

Checklist: [done] implement exact cell discovery/filtering and provenance;
[done] add focused regression tests; [done] add a resumable PowerShell runner
and weekly instructions; [done] run 37 focused tests, 166 full-suite tests, and a
real snapshot preflight (28 cells, 13 search-eligible); [pending] commit/push StrategyLab, then launch the visible optimization
and stop monitoring after verified startup.  Done means all observable acceptance
conditions pass and the visible process is running from committed code.

# Durable current state

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
