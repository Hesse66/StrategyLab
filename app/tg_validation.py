from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True, slots=True)
class ChronologicalSplit:
    development_ids: tuple[str, ...]
    holdout_ids: tuple[str, ...]
    walk_forward: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]


def chronological_split(operations: Sequence[dict[str, Any]], holdout_fraction: float = 0.25, folds: int = 3) -> ChronologicalSplit:
    ordered = sorted(operations, key=lambda item: (item["opened_at"], item["execution_id"]))
    if not ordered:
        return ChronologicalSplit((), (), ())
    holdout_count = max(1, int(len(ordered) * holdout_fraction)) if len(ordered) >= 2 else 0
    development = ordered[:-holdout_count] if holdout_count else ordered
    holdout = ordered[-holdout_count:] if holdout_count else []
    windows: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    if len(development) >= 2:
        boundaries = [int(len(development) * ratio / (folds + 1)) for ratio in range(1, folds + 2)]
        for index, boundary in enumerate(boundaries[:-1]):
            boundary = max(1, boundary)
            test_end = max(boundary + 1, boundaries[index + 1])
            train = development[:boundary]
            test = development[boundary:test_end]
            if train and test:
                windows.append((tuple(item["execution_id"] for item in train), tuple(item["execution_id"] for item in test)))
    return ChronologicalSplit(
        tuple(item["execution_id"] for item in development),
        tuple(item["execution_id"] for item in holdout),
        tuple(windows),
    )


def pnl_metrics(results: Sequence[dict[str, Any]]) -> dict[str, float | int]:
    pnls = [float(item["net_pnl"]) for item in results if item.get("net_pnl") is not None]
    gross_profit = sum(value for value in pnls if value > 0)
    gross_loss = abs(sum(value for value in pnls if value < 0))
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for value in pnls:
        equity += value
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return {
        "operations": len(pnls),
        "net_pnl": gross_profit - gross_loss,
        "gross_profit_net": gross_profit,
        "gross_loss_net": gross_loss,
        "profit_factor": gross_profit / gross_loss if gross_loss else (999999.0 if gross_profit else 0.0),
        "max_drawdown_money": max_drawdown,
        "win_rate": sum(value > 0 for value in pnls) / len(pnls) if pnls else 0.0,
        "expectancy": sum(pnls) / len(pnls) if pnls else 0.0,
    }


def dual_promotion_improvement(candidate: dict[str, Any], baseline: dict[str, Any]) -> bool:
    return (
        float(candidate["gross_profit_net"]) > float(baseline["gross_profit_net"])
        and float(candidate["gross_loss_net"]) < float(baseline["gross_loss_net"])
    )
