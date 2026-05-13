from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InstrumentRules:
    instrument_id: str
    tick_size: float
    lot_size: float
    min_size: float
    contract_value: float
    min_notional: float
    max_leverage: float


DEFAULT_OKX_RULES = InstrumentRules(
    instrument_id="BTC-USDT-SWAP",
    tick_size=0.1,
    lot_size=0.01,
    min_size=0.01,
    contract_value=0.01,
    min_notional=5.0,
    max_leverage=100.0,
)


def audit_saved_run_for_okx(run_payload: dict[str, Any], rules: InstrumentRules = DEFAULT_OKX_RULES) -> dict[str, Any]:
    """Credential-free execution audit for converting a backtest into OKX-like orders.

    This does not prove live profitability. It catches structural problems before paper
    trading: impossible order sizes, illegal precision, missing stops, excessive leverage,
    and non-production execution assumptions.
    """
    spec = run_payload.get("spec", {})
    parameters = spec.get("parameters", {})
    metrics = run_payload.get("metrics", {})
    trades = run_payload.get("trades", [])
    failures: list[str] = []
    warnings: list[str] = []
    samples: list[dict[str, Any]] = []

    if parameters.get("execution_model", "next_bar_open") not in {"next_bar_open", "mt5_bar_proxy"}:
        failures.append("non_executable_research_execution_model")
    if parameters.get("sizing_mode") == "fixed_quantity":
        failures.append("diagnostic_fixed_quantity_sizing")
    if float(parameters.get("max_leverage", 1.0)) > rules.max_leverage:
        failures.append("max_leverage_exceeds_instrument_limit")
    if metrics.get("max_entry_exposure_pct", 0.0) > float(parameters.get("max_leverage", 1.0)) * 100 + 0.01:
        failures.append("reported_exposure_exceeds_configured_leverage")

    invalid_size = 0
    invalid_notional = 0
    invalid_stop = 0
    rounded_notional_delta_pct_values: list[float] = []
    for trade in trades:
        entry_price = float(trade.get("entry_price", 0.0))
        stop_price = float(trade.get("stop_price", 0.0))
        quantity = float(trade.get("quantity", 0.0))
        if entry_price <= 0 or quantity <= 0:
            invalid_size += 1
            continue
        contracts = quantity / rules.contract_value
        rounded_contracts = round_to_step(contracts, rules.lot_size)
        rounded_quantity = rounded_contracts * rules.contract_value
        notional = rounded_quantity * entry_price
        if rounded_contracts < rules.min_size:
            invalid_size += 1
        if notional < rules.min_notional:
            invalid_notional += 1
        if stop_price <= 0 or abs(entry_price - stop_price) < rules.tick_size:
            invalid_stop += 1
        original_notional = quantity * entry_price
        if original_notional:
            rounded_notional_delta_pct_values.append(abs(notional - original_notional) / original_notional * 100)
        if len(samples) < 5:
            samples.append(
                {
                    "trade_id": trade.get("trade_id"),
                    "side": trade.get("direction"),
                    "entry_price": entry_price,
                    "quantity_base": round(quantity, 8),
                    "okx_contracts": rounded_contracts,
                    "rounded_quantity_base": round(rounded_quantity, 8),
                    "notional": round(notional, 2),
                    "stop_price": round_to_step(stop_price, rules.tick_size),
                }
            )

    if invalid_size:
        failures.append("orders_below_min_size_or_invalid_quantity")
    if invalid_notional:
        failures.append("orders_below_min_notional")
    if invalid_stop:
        failures.append("invalid_or_too_close_stop")
    if parameters.get("breakeven_stop_enabled") and not trades:
        warnings.append("breakeven_enabled_but_no_trade_samples")
    if parameters.get("breakeven_stop_enabled"):
        warnings.append("breakeven_stop_replacement_requires_live_reduce_only_stop_reconciliation")
    if parameters.get("allow_short") and "Spot" in str(spec.get("venue", "")):
        warnings.append("shorts_on_spot_label_should_route_to_perpetual_or_margin_instrument")

    avg_rounding_delta = (
        sum(rounded_notional_delta_pct_values) / len(rounded_notional_delta_pct_values)
        if rounded_notional_delta_pct_values
        else 0.0
    )
    max_rounding_delta = max(rounded_notional_delta_pct_values) if rounded_notional_delta_pct_values else 0.0
    passed = not failures
    return {
        "mode": "execution_feasibility_audit",
        "venue": "OKX public-rule approximation",
        "instrument": rules.__dict__,
        "status": "passed" if passed else "failed",
        "passed": passed,
        "failures": failures,
        "warnings": warnings,
        "trade_count": len(trades),
        "invalid_size_count": invalid_size,
        "invalid_notional_count": invalid_notional,
        "invalid_stop_count": invalid_stop,
        "avg_rounding_delta_pct": round(avg_rounding_delta, 6),
        "max_rounding_delta_pct": round(max_rounding_delta, 6),
        "order_samples": samples,
        "next_step": (
            "Paper runner can be prepared after robustness passes."
            if passed
            else "Fix execution contract before paper trading."
        ),
    }


def round_to_step(value: float, step: float) -> float:
    if step <= 0:
        return value
    return round(round(value / step) * step, 10)
