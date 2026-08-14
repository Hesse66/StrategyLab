# TgSignalSniper management lab implementation plan

Status: complete and validated. Retained as the concise implementation map.

1. Add canonical immutable snapshot models and a verified read-only importer.
2. Add `tg_signal_management_v1` tick replay and declarative policy validation.
3. Add baseline parity, chronological split, bounded candidate lineage, metrics,
   promotion gates, and deterministic experiment artifacts.
4. Extend persistence, FastAPI, CLI, and the existing UI with offline-only flows.
5. Add synthetic AutoKraken-compatible fixtures and deterministic unit/integration
   tests, including source immutability and no network/MT5/Telegram dependencies.
6. Update operational documentation and durable repository guidance.
7. Run focused tests, full regression, UI smoke validation, inspect the diff, then
   commit and push while verifying local HEAD, remote HEAD, and working tree.

## Definition of done

The regression proves import integrity/idempotence/collisions, exact tick decoding,
coverage censoring, replay semantics, cost handling, baseline parity, chronological
validation without leakage, per-asset grouping, the exact dual promotion rule,
determinism, offline boundaries, exports, and a working browser surface.
