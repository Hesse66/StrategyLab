# Offline TgSignalSniper management lab

This subsystem evaluates post-fill management policies for real TgSignalSniper
executions. It is deliberately disconnected from AutoKraken, MetaTrader, Telegram,
and every live or demo account. A package must be generated and finalized outside
StrategyLab before import.

## Package contract

A package is a directory containing `manifest.json` and finalized source files.
StrategyLab rejects SQLite sources with `-wal` or `-shm` sidecars and opens accepted
files using SQLite read-only/query-only immutable mode. It never checkpoints or
migrates a source.

Minimal manifest:

```json
{
  "manifest_schema_version": 1,
  "snapshot_state": "FINALIZED",
  "broker_name": "Axi Demo Pro",
  "broker_profile": "AXI_DEMO_PRO",
  "cohort": {
    "cohort_id": "axi-demo-pro-20260810",
    "published_from_utc": "2026-08-10T05:00:00+00:00",
    "original_timezone": "America/Bogota",
    "assets": ["XAUUSD", "EURUSD", "BTCUSD", "NASDAQ", "US30"]
  },
  "versions": {
    "operational_migration": 19,
    "tick_archive_schema": 2
  },
  "files": {
    "operational_sqlite": "tg_signal.sqlite3",
    "tick_sqlite": "tg_ticks.sqlite3",
    "trades_csv": "tg_signal_trades.csv",
    "shadow_csv": "tg_signal_shadow.csv",
    "deals_csv": "broker_deals.csv",
    "policy_registry": "policies.json",
    "symbol_specs": "symbol_specs.json"
  }
}
```

`policy_registry` is keyed by the exact `management_policy_version`. Each policy
may carry the frozen configuration fingerprint and must declare only post-fill
management. `symbol_specs` is keyed by MT5 symbol and must be captured from the
broker snapshot; at minimum it supplies `contract_size`, `volume_min`, and
`volume_step`. Deals identify `execution_id` and expose profit, commission, swap,
and fee. Missing policy, broker economics, lot constraints, or costs makes the
evidence research-only/non-comparable.

The importer supports operational migrations 16–19 for structural research.
Fields introduced by later migrations are not inferred for older packages; their
absence closes the promotion gate. Tick archives must use schema 2 and codec
`zlib-struct-qddI-v1`, with SHA-256 over every compressed chunk.

## Commands

```powershell
# Create the package outside StrategyLab using the offline AutoKraken close workflow.
# StrategyLab begins at registration/import:
.venv\Scripts\python -m app.cli tg-import-snapshot --package D:\offline-snapshots\axi-demo-pro-close

.venv\Scripts\python -m app.cli tg-coverage --snapshot-id tgsnap_<checksum>

.venv\Scripts\python -m app.cli tg-run-baseline --snapshot-id tgsnap_<checksum> --asset XAUUSD

.venv\Scripts\python -m app.cli tg-optimize --snapshot-id tgsnap_<checksum> --asset XAUUSD --seed 0

.venv\Scripts\python -m app.cli tg-report --experiment-id tgexp_<checksum>
```

The same operations are available under `/api/tg-management`. The browser UI has
an “Offline Execution Research” panel. There is intentionally no publish, sync,
MT5, Telegram, or AutoKraken action.

## Replay and evidence

`tg_signal_management_v1` freezes the real entry, direction, initial volume,
provider stop and targets. BUY exits use BID and SELL exits use ASK. Tick order is
`time_msc`, preserved decoded `source_ordinal`, ticket, then leg. Natural periods
without ticks are valid when the archive declares complete coverage and zero gaps.
Invalid checksums, broken coverage, an event outside coverage, or an
outcome-changing ordering ambiguity censor the execution. One-second marks can
guide research but never establish exact promotional evidence.

Baseline parity excludes manual/anomalous, censored, and cost-incomplete executions.
For the unmodified parent policy, exact broker deals are the authoritative source
of realized baseline P&L, including entry/exit commission, swap, and fees. Tick
replay remains authoritative for counterfactual candidates and stress variants.
Its individual tolerance is `max(USD 0.01, 0.01 × initial_risk_amount)` and its
aggregate tolerance is `max(USD 1, 0.0025 × sum(abs(actual_net_pnl)))`.

Candidate replay may continue beyond the real broker close only when the archive
declares a complete post-close horizon. The terminal event is the first original
TP3, original SL, applicable daily/weekly forced close, or 48 accumulated market
hours. An incomplete/future horizon or a candidate still open at the completed
horizon is censored, never marked to market as a completed advantage. Native TP
fills use their requested broker level rather than a later tick overshoot.

Operations are sorted chronologically. The first 75% is development data with
expanding walk-forward windows; the final 25% is untouched holdout. Fewer than 20
complete comparable operations yields `INSUFFICIENT_TRADES`; 20–39 yields
`RESEARCH_ONLY`. At 40 or more, a policy can become `PROMOTION_CANDIDATE` only if
it increases `gross_profit_net` and decreases `gross_loss_net` in both aggregated
walk-forward OOS and final holdout. This status is statistical advice only.

When a snapshot contains several immutable statistical/configuration versions,
every closed cohort trade from the declared publication boundary is evaluated.
Immutable version sets remain visible as diagnostic strata and never become
`VERSION_SET_MISMATCH` exclusions. Actual broker performance uses every trade;
exact BID/ASK paths are promotion-grade, while imported one-second position-price
paths remain explicitly approximate research evidence
exclusions instead of being mixed or rewritten. A missing exact policy registry
entry fails baseline parity for that selected set.

## Artifacts and backfill diagnosis

Canonical content-addressed snapshots live under `artifacts/tg_snapshots/`.
Experiment JSON, CSV, and Markdown reports live under
`artifacts/tg_experiments/`. Coverage output lists the exact execution IDs whose
archive is missing, incomplete, gapped, or does not span the required interval.

The locally observed 22-row statistics CSV is fixture/reference material only. It
is not the final VPS cohort. Promotion evaluation requires the finalized post-close
operational database, exact tick archive, shadow/statistics exports, and available
broker costs/deals.
