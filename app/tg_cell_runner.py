from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any

from app.config import settings
from app.storage import Repository
from app.tg_lab import TgManagementLabService


FIELDS = (
    "cell_id", "asset", "timeframe", "side", "operation_count",
    "optimization_eligible", "promotion_sample_eligible", "state",
    "baseline_experiment_id", "baseline_status", "baseline_net_pnl",
    "baseline_profit_factor", "optimization_experiment_id",
    "optimization_status", "recommendation", "candidate_net_pnl",
    "candidate_profit_factor", "error",
)


def _read_rows(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["cell_id"]: row for row in csv.DictReader(handle)}


def _write_rows(path: Path, rows: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for key in sorted(rows):
            writer.writerow(rows[key])
    os.replace(temporary, path)


def _metrics(experiment: dict[str, Any], candidate: bool = False) -> dict[str, Any]:
    result = experiment["result_json"]
    if candidate:
        selected = result.get("selected_candidate") or {}
        return (selected.get("sections") or {}).get("global") or {}
    return (result.get("baseline_sections") or {}).get("global") or {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run resumable asset/timeframe/direction TgSignalSniper optimization",
    )
    parser.add_argument("--snapshot-id", required=True)
    parser.add_argument("--output")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    settings.ensure_dirs()
    service = TgManagementLabService(Repository())
    plan = service.list_cells(args.snapshot_id)
    output = Path(args.output) if args.output else (
        settings.tg_experiment_dir / "cell_runs" / args.snapshot_id / "summary.csv"
    )
    rows = _read_rows(output) if args.resume else {}
    cells = plan["cells"]
    optimizable = sum(item["optimization_eligible"] for item in cells)
    print(
        f"CELL_PLAN={len(cells)} baselines; {optimizable} optimizations "
        "(unit=asset/timeframe/direction)", flush=True,
    )
    print(f"SUMMARY={output}", flush=True)

    failures = 0
    for ordinal, cell in enumerate(cells, start=1):
        cell_id = f"{cell['asset']}:{cell['timeframe']}:{cell['side']}"
        existing = rows.get(cell_id, {})
        if args.resume and existing.get("state") in {"DIAGNOSTIC_COMPLETE", "OPTIMIZATION_COMPLETE"}:
            print(f"SKIP {ordinal}/{len(cells)} {cell_id}: {existing['state']}", flush=True)
            continue
        row: dict[str, Any] = {
            **existing,
            **cell,
            "cell_id": cell_id,
            "state": existing.get("state") or "PENDING",
            "error": "",
        }
        rows[cell_id] = row
        try:
            if not row.get("baseline_experiment_id"):
                print(f"BASELINE {ordinal}/{len(cells)} {cell_id} ({cell['operation_count']} ops)", flush=True)
                baseline = service.run_baseline(
                    args.snapshot_id, cell["asset"], cell["timeframe"], cell["side"],
                )
                baseline_metrics = _metrics(baseline)
                row.update({
                    "baseline_experiment_id": baseline["experiment_id"],
                    "baseline_status": baseline["status"],
                    "baseline_net_pnl": baseline_metrics.get("net_pnl"),
                    "baseline_profit_factor": baseline_metrics.get("profit_factor"),
                    "state": "BASELINE_COMPLETE",
                })
                _write_rows(output, rows)

            if not cell["optimization_eligible"]:
                row["state"] = "DIAGNOSTIC_COMPLETE"
                _write_rows(output, rows)
                print(f"DIAGNOSTIC {cell_id}: sample below 20; search skipped", flush=True)
                continue

            def progress(event: dict[str, Any]) -> None:
                print(
                    f"  {cell_id} {event['stage']} {event['completed']}/{event['total']} "
                    f"({event['percent']:.2f}%)",
                    flush=True,
                )

            print(f"OPTIMIZE {ordinal}/{len(cells)} {cell_id}", flush=True)
            optimized = service.optimize_asset(
                args.snapshot_id, cell["asset"], progress_callback=progress,
                timeframe=cell["timeframe"], side=cell["side"],
            )
            candidate_metrics = _metrics(optimized, candidate=True)
            row.update({
                "optimization_experiment_id": optimized["experiment_id"],
                "optimization_status": optimized["status"],
                "recommendation": optimized["result_json"].get("recommendation"),
                "candidate_net_pnl": candidate_metrics.get("net_pnl"),
                "candidate_profit_factor": candidate_metrics.get("profit_factor"),
                "state": "OPTIMIZATION_COMPLETE",
                "error": "",
            })
            _write_rows(output, rows)
        except Exception as exc:  # preserve progress and continue other independent cells
            failures += 1
            row["state"] = "FAILED"
            row["error"] = f"{type(exc).__name__}: {exc}"
            _write_rows(output, rows)
            print(f"FAILED {cell_id}: {row['error']}", file=sys.stderr, flush=True)

    complete = sum(
        row.get("state") in {"DIAGNOSTIC_COMPLETE", "OPTIMIZATION_COMPLETE"}
        for row in rows.values()
    )
    print(f"CELL_RUN_COMPLETE={complete}/{len(cells)}; failures={failures}", flush=True)
    return 1 if failures or complete != len(cells) else 0


if __name__ == "__main__":
    raise SystemExit(main())
