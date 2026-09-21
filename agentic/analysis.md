# Active: weekly US30 policy compatibility

The 2026-09-20 snapshot adds an asset-specific US30 management policy containing
management fields plus `asset`, fixed-R `target_levels_r`, and
`time_stop_even_if_breakeven`.  The current decoder forwards the combined payload
directly to `ManagementPolicy`, aborting the weekly batch before US30, XAUUSD and
EURUSD.  The repair must split the registered payload into the existing
management and target-geometry models, preserve the true broker-deal baseline,
use the frozen US30 geometry for management-only and stressed baseline replays,
and reject unsupported time-stop semantics rather than silently dropping them.

Checklist: [done] implemented the split decoder and baseline-geometry
propagation; [done] added regression coverage for the exact US30 payload and
incomplete broker-deal fallback; [done] 35 focused TgSignalSniper tests pass and
the real US30 snapshot baseline now has exact parity (-82.58/-82.58, delta 0);
[waiting] resume only US30/XAUUSD/EURUSD in visible PowerShell and let the user
report completion before result review.

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
