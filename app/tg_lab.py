from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import subprocess
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from fastapi import HTTPException

from app.config import BASE_DIR, settings
from app.tg_import import TgSnapshotImporter, canonical_json
from app.tg_models import ENGINE_VERSION, IMPORTER_VERSION, MODEL_VERSION, ManagementPolicy, SUPPORTED_ASSETS
from app.tg_replay import TgSignalReplayEngine
from app.tg_validation import chronological_split, dual_promotion_improvement, pnl_metrics


class TgManagementLabService:
    def __init__(self, repository: Any) -> None:
        self.repository = repository
        self.importer = TgSnapshotImporter(repository)
        self.replay_engine = TgSignalReplayEngine()
        settings.ensure_dirs()

    def import_snapshot(self, package_path: str) -> dict[str, Any]:
        return self.importer.import_package(package_path)

    def list_snapshots(self) -> list[dict[str, Any]]:
        return self.repository.list_tg_snapshots()

    def snapshot_detail(self, snapshot_id: str) -> dict[str, Any]:
        snapshot = self._snapshot(snapshot_id)
        return snapshot

    def coverage(self, snapshot_id: str) -> dict[str, Any]:
        snapshot = self._snapshot(snapshot_id)
        return {
            "snapshot_id": snapshot_id,
            "checksum": snapshot["checksum"],
            "broker_profile": snapshot["broker_profile"],
            "cohort_id": snapshot["cohort_id"],
            **snapshot["coverage_json"],
        }

    def run_baseline(self, snapshot_id: str, asset: str) -> dict[str, Any]:
        return self._run(snapshot_id, asset, optimize=False)

    def optimize_asset(self, snapshot_id: str, asset: str, seed: int = 0) -> dict[str, Any]:
        return self._run(snapshot_id, asset, optimize=True, seed=seed)

    def list_experiments(self, snapshot_id: str | None = None, asset: str | None = None) -> list[dict[str, Any]]:
        return self.repository.list_tg_experiments(snapshot_id, asset)

    def experiment(self, experiment_id: str) -> dict[str, Any]:
        payload = self.repository.get_tg_experiment(experiment_id)
        if not payload:
            raise HTTPException(404, "TgSignalSniper experiment not found")
        return payload

    def _snapshot(self, snapshot_id: str) -> dict[str, Any]:
        snapshot = self.repository.get_tg_snapshot(snapshot_id)
        if not snapshot:
            raise HTTPException(404, "TgSignalSniper snapshot not found")
        return snapshot

    def _run(self, snapshot_id: str, asset: str, *, optimize: bool, seed: int = 0) -> dict[str, Any]:
        asset = asset.upper()
        if asset not in SUPPORTED_ASSETS:
            raise HTTPException(400, f"Unsupported initial cohort asset: {asset}")
        snapshot = self._snapshot(snapshot_id)
        snapshot_db = Path(snapshot["path"]) / "snapshot.sqlite3"
        all_operations = self._load_operations(snapshot_db, asset)
        evidence_tiers = self._evidence_tiers(snapshot_db, all_operations)
        version_sets = sorted({(
            item["statistics_schema_version"], item["signal_version"], item["parser_version"],
            item["execution_policy_version"], item["management_policy_version"], item["config_fingerprint"],
        ) for item in all_operations})
        def version_key(item: dict[str, Any]) -> tuple[str, str, str, str, str, str]:
            return (
                item["statistics_schema_version"], item["signal_version"],
                item["parser_version"], item["execution_policy_version"],
                item["management_policy_version"], item["config_fingerprint"],
            )
        grouped: dict[tuple[str, str, str, str, str, str], list[dict[str, Any]]] = {}
        for operation in all_operations:
            grouped.setdefault(version_key(operation), []).append(operation)
        selected_version_set = (
            max(
                grouped,
                key=lambda key: (
                    max(str(item.get("published_at") or "") for item in grouped[key]),
                    len(grouped[key]), key,
                ),
            )
            if grouped else None
        )
        # Every closed operation in the declared cohort is mandatory evidence.
        # Version sets are diagnostic strata, never an exclusion filter.
        operations = list(all_operations)
        latest_operations = list(grouped.get(selected_version_set, []))
        baseline_versions = sorted({
            item["management_policy_version"] for item in latest_operations
            if item.get("management_policy_version")
        })
        baseline_policy = None
        for version in reversed(baseline_versions):
            baseline_policy = self.replay_engine.policy_from_snapshot(
                snapshot_db, version,
            )
            if baseline_policy is not None:
                break
        config = {
            "snapshot_id": snapshot_id,
            "asset": asset,
            "reference_version_set": (
                list(selected_version_set) if selected_version_set else None
            ),
            "version_sets_are_strata_not_filters": True,
            "observed_version_sets": [list(item) for item in version_sets],
            "seed": seed,
            "optimize": optimize,
            "holdout_fraction": 0.25,
            "walk_forward_folds": 3,
            "minimum_exploratory_operations": 20,
            "minimum_promotional_operations": 40,
            "engine_version": ENGINE_VERSION,
            "importer_version": IMPORTER_VERSION,
            "model_version": MODEL_VERSION,
        }
        code_hash = self._code_hash()
        experiment_hash = hashlib.sha256(canonical_json({"snapshot": snapshot["checksum"], "config": config, "code": code_hash}).encode()).hexdigest()
        experiment_id = f"tgexp_{experiment_hash[:16]}"

        exclusions: dict[str, list[str]] = {}
        baseline_results: dict[str, dict[str, Any]] = {}
        parity_diagnostics: list[dict[str, Any]] = []
        parity_failed = baseline_policy is None
        aggregate_actual = 0.0
        aggregate_replay = 0.0
        aggregate_abs_actual = 0.0
        for operation in operations:
            reasons: list[str] = []
            if not baseline_policy:
                reasons.append("INCOMPATIBLE_OR_MISSING_BASELINE_POLICY")
            if reasons:
                exclusions[operation["execution_id"]] = reasons
                continue
            # The immutable broker-deal baseline does not require a replay path.
            broker_operation = dict(operation)
            broker_operation["_use_broker_actual_baseline"] = True
            replay = self.replay_engine.replay(
                broker_operation, [], {}, baseline_policy,
            )
            replay_payload = replay.to_dict()
            baseline_results[operation["execution_id"]] = replay_payload
            if not replay.comparable or replay.net_pnl is None:
                exclusions[operation["execution_id"]] = list(replay.exclusions) or [replay.status]
                continue
            actual = operation.get("broker_realized_net_pnl")
            if actual is None:
                exclusions[operation["execution_id"]] = ["MISSING_BROKER_REALIZED_PNL"]
                continue
            actual = float(actual)
            difference = abs(float(replay.net_pnl) - actual)
            tolerance = max(0.01, 0.01 * float(operation.get("risk_amount") or 0))
            diagnostic = self._parity_diagnostic(operation, replay_payload, difference, tolerance)
            parity_diagnostics.append(diagnostic)
            if difference > tolerance:
                parity_failed = True
            aggregate_actual += actual
            aggregate_replay += float(replay.net_pnl)
            aggregate_abs_actual += abs(actual)
        aggregate_difference = abs(aggregate_replay - aggregate_actual)
        aggregate_tolerance = max(1.0, 0.0025 * aggregate_abs_actual)
        if aggregate_difference > aggregate_tolerance:
            parity_failed = True
        comparable = [operation for operation in operations if operation["execution_id"] in baseline_results and operation["execution_id"] not in exclusions]
        split = chronological_split(comparable)
        baseline_sections = self._sections(comparable, baseline_results, split)
        stress_profiles = list(snapshot["contract_json"].get("stress_profiles", []))
        parity = {
            "status": "BASELINE_PARITY_FAILED" if parity_failed else "PASSED",
            "individual_tolerance_formula": "max(USD 0.01, 0.01 * initial_risk_amount)",
            "aggregate_tolerance_formula": "max(USD 1.00, 0.0025 * sum(abs(actual_net_pnl)))",
            "aggregate_actual_net_pnl": aggregate_actual,
            "aggregate_replay_net_pnl": aggregate_replay,
            "aggregate_difference": aggregate_difference,
            "aggregate_tolerance": aggregate_tolerance,
            "operations": parity_diagnostics,
        }

        candidates: list[dict[str, Any]] = []
        selected: dict[str, Any] | None = None
        evidence_status = self._evidence_status(len(comparable), len(operations), parity_failed, snapshot, operations, asset)
        if optimize and baseline_policy and not parity_failed and len(comparable) >= 20:
            for order, candidate_policy in enumerate(self._candidate_policies(baseline_policy)):
                candidate_results = self._replay_many(snapshot_db, comparable, candidate_policy)
                sections = self._sections(comparable, candidate_results, split)
                same_comparable_set = all(candidate_results[item["execution_id"]].get("comparable") for item in comparable)
                exact_promotion_set = all(
                    candidate_results[item["execution_id"]]
                    .get("diagnostics", {}).get("promotion_eligible", False)
                    for item in comparable
                )
                wf_pass = dual_promotion_improvement(sections["walk_forward_oos"], baseline_sections["walk_forward_oos"])
                holdout_pass = dual_promotion_improvement(sections["holdout"], baseline_sections["holdout"])
                stress_scenarios = []
                stress_gate = True
                for profile in stress_profiles:
                    name = str(profile.get("name") or "stress")
                    baseline_stress_policy = replace(
                        baseline_policy,
                        policy_id=f"{baseline_policy.policy_id}_{name}",
                        parent_policy_id=baseline_policy.policy_id,
                        latency_msc=int(profile.get("latency_msc") or 0),
                        exit_slippage_price=float(profile.get("slippage_price") or 0),
                        stress_same_millisecond_stop_first=bool(profile.get("same_millisecond_stop_first", False)),
                    )
                    candidate_stress_policy = replace(
                        candidate_policy,
                        policy_id=f"{candidate_policy.policy_id}_{name}",
                        latency_msc=int(profile.get("latency_msc") or 0),
                        exit_slippage_price=float(profile.get("slippage_price") or 0),
                        stress_same_millisecond_stop_first=bool(profile.get("same_millisecond_stop_first", False)),
                    )
                    baseline_stress = self._sections(comparable, self._replay_many(snapshot_db, comparable, baseline_stress_policy), split)
                    candidate_stress = self._sections(comparable, self._replay_many(snapshot_db, comparable, candidate_stress_policy), split)
                    scenario_pass = dual_promotion_improvement(candidate_stress["walk_forward_oos"], baseline_stress["walk_forward_oos"]) and dual_promotion_improvement(candidate_stress["holdout"], baseline_stress["holdout"])
                    stress_gate = stress_gate and scenario_pass
                    stress_scenarios.append({"name": name, "profile": profile, "baseline_sections": baseline_stress, "candidate_sections": candidate_stress, "dual_gate": scenario_pass})
                candidate = {
                    "evaluation_order": order,
                    "policy": candidate_policy.to_dict(),
                    "parent_policy_id": baseline_policy.policy_id,
                    "sections": sections,
                    "walk_forward_dual_gate": wf_pass,
                    "holdout_dual_gate": holdout_pass,
                    "stress_scenarios": stress_scenarios,
                    "stress_gate": stress_gate,
                    "same_comparable_operation_set": same_comparable_set,
                    "exact_promotion_set": exact_promotion_set,
                    "promotion_gate": same_comparable_set and exact_promotion_set and wf_pass and holdout_pass and stress_gate and len(comparable) >= 40,
                    "complexity": self._complexity(baseline_policy, candidate_policy),
                    "results": candidate_results,
                }
                candidate["selection_score"] = self._selection_score(candidate, baseline_sections)
                candidates.append(candidate)
            eligible = [item for item in candidates if item["promotion_gate"]]
            ranked = eligible or candidates
            if ranked:
                selected = sorted(ranked, key=lambda item: (-item["selection_score"], item["sections"]["holdout"]["max_drawdown_money"], item["complexity"], item["evaluation_order"]))[0]
            if len(comparable) < 40:
                evidence_status = "RESEARCH_ONLY"
            elif selected and selected["promotion_gate"]:
                evidence_status = "PROMOTION_CANDIDATE"
            else:
                evidence_status = "REJECTED"

        result = {
            "experiment_id": experiment_id,
            "snapshot_id": snapshot_id,
            "snapshot_checksum": snapshot["checksum"],
            "broker_profile": snapshot["broker_profile"],
            "cohort_id": snapshot["cohort_id"],
            "asset": asset,
            "status": evidence_status,
            "promotion_is_statistical_only": True,
            "baseline_policy": baseline_policy.to_dict() if baseline_policy else None,
            "baseline_parity": parity,
            "coverage": snapshot["coverage_json"].get("assets", {}).get(asset, {}),
            "cohort_execution_ids": [item["execution_id"] for item in operations],
            "included_execution_ids": [item["execution_id"] for item in comparable],
            "excluded_executions": exclusions,
            "version_strata": {
                "|".join(key): [item["execution_id"] for item in values]
                for key, values in grouped.items()
            },
            "quality_flags": {
                item["execution_id"]: [
                    flag for flag, present in (
                        ("MANUAL_INTERVENTION", item.get("manual_intervention")),
                        ("ANOMALOUS_STATE", item.get("anomalous_state")),
                        ("MISSING_COST_BREAKDOWN", not item.get("costs_complete")),
                        ("UNRESOLVED_HISTORICAL_POLICY", not item.get("policy_resolved")),
                        ("MISSING_SYMBOL_SPEC", not item.get("symbol_spec_resolved")),
                    ) if present
                ]
                for item in operations
            },
            "evidence_tiers": evidence_tiers,
            "chronology": {
                "development_ids": list(split.development_ids),
                "holdout_ids": list(split.holdout_ids),
                "walk_forward": [{"train_ids": list(train), "oos_ids": list(test)} for train, test in split.walk_forward],
            },
            "baseline_sections": baseline_sections,
            "baseline_results": baseline_results,
            "candidates_tested": len(candidates),
            "search_space": [item["policy"] for item in candidates],
            "stress_profiles": stress_profiles,
            "candidates": candidates,
            "selected_candidate": selected,
            "timeframe_lane_diagnostics": self._subgroup_metrics(comparable, baseline_results, selected),
            "engine_version": ENGINE_VERSION,
            "importer_version": IMPORTER_VERSION,
            "model_version": MODEL_VERSION,
            "code_hash": code_hash,
            "seed": seed,
        }
        paths = self._write_artifacts(experiment_id, result)
        stored = {
            "experiment_id": experiment_id,
            "snapshot_id": snapshot_id,
            "broker_profile": snapshot["broker_profile"],
            "cohort_id": snapshot["cohort_id"],
            "asset": asset,
            "status": evidence_status,
            "engine_version": ENGINE_VERSION,
            "code_hash": code_hash,
            "config_json": config,
            "result_json": result,
            "artifact_path": str(paths["json"]),
            "report_path": str(paths["markdown"]),
            "created_at": datetime.now(UTC).isoformat(),
        }
        self.repository.put_tg_experiment(stored)
        return self.repository.get_tg_experiment(experiment_id) or stored

    @staticmethod
    def _load_operations(snapshot_db: Path, asset: str) -> list[dict[str, Any]]:
        connection = sqlite3.connect(snapshot_db)
        try:
            return [json.loads(row[0]) for row in connection.execute("SELECT payload_json FROM operations WHERE asset = ? ORDER BY opened_at, execution_id", (asset,))]
        finally:
            connection.close()

    @staticmethod
    def _evidence_tiers(
        snapshot_db: Path, operations: list[dict[str, Any]],
    ) -> dict[str, str]:
        connection = sqlite3.connect(snapshot_db)
        try:
            tables = {
                str(row[0]) for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            exact_ids: set[str] = set()
            if "tick_coverage" in tables:
                for execution_id, payload_json in connection.execute(
                    "SELECT execution_id,payload_json FROM tick_coverage"
                ):
                    payload = json.loads(payload_json)
                    if (
                        str(payload.get("status")) == "COMPLETE"
                        and int(
                            payload.get("coverage_gap_count")
                            or payload.get("gap_count") or 0
                        ) == 0
                    ):
                        exact_ids.add(str(execution_id))
            mark_ids = (
                {
                    str(row[0]) for row in connection.execute(
                        "SELECT DISTINCT execution_id FROM one_second_marks"
                    )
                }
                if "one_second_marks" in tables else set()
            )
            return {
                item["execution_id"]: (
                    "EXACT_TICK" if item["execution_id"] in exact_ids
                    else "APPROXIMATE_1S"
                    if item["execution_id"] in mark_ids else "MISSING"
                )
                for item in operations
            }
        finally:
            connection.close()

    def _replay_many(self, snapshot_db: Path, operations: list[dict[str, Any]], policy: ManagementPolicy) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        for operation in operations:
            _, ticks, coverage = self.replay_engine.load_operation(snapshot_db, operation["execution_id"])
            results[operation["execution_id"]] = self.replay_engine.replay(operation, ticks, coverage, policy).to_dict()
        return results

    @staticmethod
    def _sections(operations: list[dict[str, Any]], results: dict[str, dict[str, Any]], split: Any) -> dict[str, Any]:
        by_id = {item["execution_id"]: item for item in operations}
        def metrics(ids: Iterable[str]) -> dict[str, Any]:
            selected = [results[item] for item in ids if item in results and results[item].get("comparable")]
            return pnl_metrics(selected)
        wf_ids = [execution_id for _, test in split.walk_forward for execution_id in test]
        return {
            "global": metrics(by_id),
            "development": metrics(split.development_ids),
            "walk_forward_oos": metrics(wf_ids),
            "holdout": metrics(split.holdout_ids),
            "walk_forward_windows": [
                {"train": metrics(train), "oos": metrics(test), "train_ids": list(train), "oos_ids": list(test)}
                for train, test in split.walk_forward
            ],
        }

    @staticmethod
    def _parity_diagnostic(operation: dict[str, Any], replay: dict[str, Any], difference: float, tolerance: float) -> dict[str, Any]:
        milestones = replay.get("milestones", [])
        replay_reason = replay.get("fills", [{}])[-1].get("reason") if replay.get("fills") else None
        return {
            "execution_id": operation["execution_id"],
            "actual_net_pnl": operation.get("broker_realized_net_pnl"),
            "replay_net_pnl": replay.get("net_pnl"),
            "difference": difference,
            "tolerance": tolerance,
            "passed": difference <= tolerance,
            "diagnostics": {
                "leg_order": [item.get("leg_id") for item in replay.get("fills", [])],
                "partial_targets": [item.get("event") for item in milestones if str(item.get("event", "")).startswith("TP")],
                "remaining_volume": replay.get("final_remaining_volume"),
                "breakeven": any("BREAKEVEN" in str(item.get("event")) for item in milestones),
                "stop_after_tp2": any(item.get("event") == "STOP_TO_TP1_AFTER_TP2" for item in milestones),
                "actual_close_reason": operation.get("close_reason"),
                "replay_close_reason": replay_reason,
                "opened_at_utc": operation.get("opened_at"),
                "closed_at_utc": operation.get("closed_at"),
                "timestamp_differences_are_diagnostic_only": True,
            },
        }

    @staticmethod
    def _candidate_policies(baseline: ManagementPolicy) -> list[ManagementPolicy]:
        mutations: list[dict[str, Any]] = [
            {"early_breakeven_activation_r": 0.5},
            {"early_breakeven_activation_r": 0.75},
            {"early_breakeven_activation_r": 1.0, "early_breakeven_offset_r": 0.05},
            {"trailing_activation_r": 1.0, "trailing_distance_r": 0.5, "trailing_step_r": 0.25},
            {"trailing_activation_r": 1.5, "trailing_distance_r": 0.75, "trailing_step_r": 0.25},
            {"trailing_activation_r": 1.0, "trailing_distance_r": 0.5, "trailing_step_r": 0.25, "trailing_after": "tp1", "tp1_action": "trailing"},
            {"trailing_activation_r": 1.5, "trailing_distance_r": 0.75, "trailing_step_r": 0.25, "trailing_after": "tp2", "tp2_action": "trailing"},
            {"mfe_protect_activation_r": 1.0, "mfe_protect_fraction": 0.5},
            {"mfe_protect_activation_r": 1.5, "mfe_protect_fraction": 0.7},
            {"partials": (0.4, 0.3, 0.3)},
            {"partials": (0.6, 0.2, 0.2)},
            {"time_stop_seconds": 3600},
            {"time_stop_seconds": 7200},
        ]
        candidates = []
        for ordinal, mutation in enumerate(mutations, start=1):
            candidates.append(replace(baseline, policy_id=f"{baseline.policy_id}_m{ordinal:02d}", parent_policy_id=baseline.policy_id, **mutation))
        return candidates

    @staticmethod
    def _complexity(baseline: ManagementPolicy, candidate: ManagementPolicy) -> int:
        base = baseline.to_dict()
        current = candidate.to_dict()
        ignored = {"policy_id", "parent_policy_id"}
        return sum(base[key] != current[key] for key in base if key not in ignored)

    @staticmethod
    def _selection_score(candidate: dict[str, Any], baseline_sections: dict[str, Any]) -> float:
        score = 0.0
        for section in ("walk_forward_oos", "holdout"):
            current = candidate["sections"][section]
            baseline = baseline_sections[section]
            score += (current["gross_profit_net"] - baseline["gross_profit_net"]) + (baseline["gross_loss_net"] - current["gross_loss_net"])
        return score

    @staticmethod
    def _evidence_status(count: int, total_count: int, parity_failed: bool, snapshot: dict[str, Any], operations: list[dict[str, Any]], asset: str) -> str:
        if total_count < 20:
            return "INSUFFICIENT_TRADES"
        exact_count = int(snapshot.get("coverage_json", {}).get("assets", {}).get(asset, {}).get("complete_coverage", 0))
        if exact_count < 20 and any(item.get("one_second_mark_count") for item in operations):
            return "RESEARCH_ONLY"
        if exact_count < 20:
            return "INSUFFICIENT_EXACT_COVERAGE"
        if count < 20:
            return "INSUFFICIENT_TRADES"
        if parity_failed:
            return "BASELINE_PARITY_FAILED"
        if count < 40:
            return "RESEARCH_ONLY"
        if any(not item.get("costs_complete") or not item.get("policy_resolved") or not item.get("symbol_spec_resolved") for item in operations):
            return "RESEARCH_ONLY"
        return "RESEARCH_ONLY"

    @staticmethod
    def _subgroup_metrics(operations: list[dict[str, Any]], baseline_results: dict[str, dict[str, Any]], selected: dict[str, Any] | None) -> list[dict[str, Any]]:
        groups: dict[tuple[str, str], list[str]] = {}
        for operation in operations:
            groups.setdefault((operation["timeframe"], operation["strategy_lane"]), []).append(operation["execution_id"])
        diagnostics = []
        candidate_results = selected.get("results", {}) if selected else {}
        for (timeframe, lane), ids in sorted(groups.items()):
            baseline = pnl_metrics([baseline_results[item] for item in ids if item in baseline_results])
            candidate = pnl_metrics([candidate_results[item] for item in ids if item in candidate_results]) if selected else None
            diagnostics.append({"timeframe": timeframe, "lane": lane, "operation_ids": ids, "baseline": baseline, "candidate": candidate, "candidate_worsens_subgroup": bool(candidate and candidate["net_pnl"] < baseline["net_pnl"])})
        return diagnostics

    def _write_artifacts(self, experiment_id: str, result: dict[str, Any]) -> dict[str, Path]:
        root = settings.tg_experiment_dir
        json_path = root / f"{experiment_id}.json"
        csv_path = root / f"{experiment_id}.csv"
        markdown_path = root / f"{experiment_id}.md"
        json_path.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["execution_id", "included", "evidence_tier", "quality_flags", "exclusion_reasons", "baseline_net_pnl", "candidate_net_pnl", "candidate_status"])
            writer.writeheader()
            selected_results = (result.get("selected_candidate") or {}).get("results", {})
            ids = sorted(set(result["included_execution_ids"]) | set(result["excluded_executions"]))
            for execution_id in ids:
                writer.writerow({
                    "execution_id": execution_id,
                    "included": execution_id in result["included_execution_ids"],
                    "evidence_tier": result.get("evidence_tiers", {}).get(execution_id),
                    "quality_flags": "|".join(result.get("quality_flags", {}).get(execution_id, [])),
                    "exclusion_reasons": "|".join(result["excluded_executions"].get(execution_id, [])),
                    "baseline_net_pnl": result["baseline_results"].get(execution_id, {}).get("net_pnl"),
                    "candidate_net_pnl": selected_results.get(execution_id, {}).get("net_pnl"),
                    "candidate_status": selected_results.get(execution_id, {}).get("status"),
                })
        markdown_path.write_text(self._markdown_report(result), encoding="utf-8")
        return {"json": json_path, "csv": csv_path, "markdown": markdown_path}

    @staticmethod
    def _markdown_report(result: dict[str, Any]) -> str:
        baseline = result["baseline_sections"]
        lines = [
            f"# TgSignalSniper management experiment {result['experiment_id']}", "",
            f"- Asset: {result['asset']}", f"- Broker: {result['broker_profile']}",
            f"- Cohort: {result['cohort_id']}", f"- Snapshot: `{result['snapshot_id']}`",
            f"- Engine: `{result['engine_version']}`", f"- Status: **{result['status']}**", "",
            "`PROMOTION_CANDIDATE` is a statistical recommendation only. This lab never publishes policies or contacts AutoKraken, MT5, or Telegram.", "",
            "## Evidence", "",
            f"- Included operations: {len(result['included_execution_ids'])}",
            f"- Excluded/censored operations: {len(result['excluded_executions'])}",
            f"- Exact tick paths: {sum(value == 'EXACT_TICK' for value in result.get('evidence_tiers', {}).values())}",
            f"- One-second research paths: {sum(value == 'APPROXIMATE_1S' for value in result.get('evidence_tiers', {}).values())}",
            f"- Observed immutable version strata: {len(result.get('version_strata', {}))} (used as diagnostics, never as exclusions)",
            f"- Baseline parity: {result['baseline_parity']['status']}", "",
            "## Baseline sections", "",
            "| Section | Operations | Gross profit net | Gross loss net | Net P&L |", "|---|---:|---:|---:|---:|",
        ]
        for key in ("development", "walk_forward_oos", "holdout", "global"):
            metrics = baseline[key]
            lines.append(f"| {key} | {metrics['operations']} | {metrics['gross_profit_net']:.2f} | {metrics['gross_loss_net']:.2f} | {metrics['net_pnl']:.2f} |")
        lines.extend(["", "## Coverage and backfill", ""])
        missing = result.get("coverage", {}).get("requires_backfill_execution_ids", [])
        lines.append(f"Executions requiring tick backfill: {', '.join(missing) if missing else 'none declared' }.")
        lines.extend(["", "## Timeframe and lane diagnostics", ""])
        for group in result["timeframe_lane_diagnostics"]:
            lines.append(f"- {group['timeframe']} / {group['lane']}: {len(group['operation_ids'])} operations; baseline net {group['baseline']['net_pnl']:.2f}.")
        if result.get("selected_candidate"):
            selected = result["selected_candidate"]
            lines.extend(["", "## Selected candidate", "", f"- Policy: `{selected['policy']['policy_id']}`", f"- Walk-forward dual gate: {selected['walk_forward_dual_gate']}", f"- Holdout dual gate: {selected['holdout_dual_gate']}"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _code_hash() -> str:
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=BASE_DIR, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return "unknown"
