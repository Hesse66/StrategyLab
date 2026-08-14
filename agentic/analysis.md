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

Each asset selects the immutable version set attached to its most recently
published execution; older sets remain explicit `VERSION_SET_MISMATCH`
exclusions. Chronological 75/25 validation and the 20/40-operation research and
promotion gates remain unchanged.

The Axi Demo Pro finalized package imported successfully. Baseline parity passed
for each latest exact-covered asset set, but the current cohorts are still too
small for management promotion. No production policy is approved.
