# TgSignalSniper management lab implementation plan

Status: complete and validated. Retained as the concise implementation map.

1. Add canonical immutable snapshot models and a verified read-only importer.
2. Extend the single replay as `tg_signal_management_v2` with immutable provider
   targets, FIXED_R target geometry, and declarative management policies.
3. Add baseline parity, strict 75/25 chronology, WF-only family selection, one
   untouched holdout evaluation, bounded 106/3/39 lineage, bootstrap equivalence,
   full promotion gates, and deterministic experiment artifacts.
4. Extend persistence, FastAPI, CLI, and the existing UI with offline-only flows.
5. Add synthetic AutoKraken-compatible fixtures and deterministic unit/integration
   tests, including source immutability and no network/MT5/Telegram dependencies.
6. Update operational documentation and durable repository guidance.
7. Run focused tests, full regression, UI smoke validation, inspect the diff, then
   commit and push while verifying local HEAD, remote HEAD, and working tree.

## Definition of done

The regression proves import integrity/idempotence/collisions, exact tick decoding,
coverage censoring, replay semantics, cost handling, baseline parity, chronological
validation without leakage, per-asset grouping, the full GP/GL/net/PF/DD rule,
determinism, offline boundaries, exports, and a working browser surface.
