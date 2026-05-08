from __future__ import annotations

import copy
import math
import uuid
from dataclasses import dataclass
from datetime import datetime
from statistics import mean
from typing import Any

from fastapi import HTTPException

from app.data import Bar


@dataclass(slots=True)
class Position:
    direction: int
    entry_index: int
    entry_ts: datetime
    entry_price: float
    stop_price: float
    quantity: float
    entry_commission: float
    entry_equity: float
    entry_notional: float
    initial_risk_per_unit: float
    stop_initialized_on_index: int
    entry_features: dict[str, Any]
    max_favorable_excursion: float = 0.0
    max_adverse_excursion: float = 0.0
    stop_moved_to_breakeven: bool = False
    time_decay_confirmation_suppressed: int = 0
    reverse_confirmation_suppressed: int = 0


def sma(values: list[float], length: int) -> list[float | None]:
    output: list[float | None] = []
    running = 0.0
    for index, value in enumerate(values):
        running += value
        if index >= length:
            running -= values[index - length]
        output.append((running / length) if index + 1 >= length else None)
    return output


def ema(values: list[float], length: int) -> list[float | None]:
    output: list[float | None] = []
    alpha = 2 / (length + 1)
    current: float | None = None
    for index, value in enumerate(values):
        if index + 1 < length:
            output.append(None)
            continue
        if current is None:
            window = values[index + 1 - length : index + 1]
            current = sum(window) / length
        else:
            current = (value * alpha) + (current * (1 - alpha))
        output.append(current)
    return output


def atr(bars: list[Bar], length: int) -> list[float | None]:
    output: list[float | None] = []
    trs: list[float] = []
    previous_close = bars[0].close if bars else 0.0
    for index, bar in enumerate(bars):
        tr = max(bar.high - bar.low, abs(bar.high - previous_close), abs(bar.low - previous_close))
        trs.append(tr)
        if index + 1 < length:
            output.append(None)
        else:
            window = trs[index + 1 - length : index + 1]
            output.append(sum(window) / length)
        previous_close = bar.close
    return output


def rolling_high(values: list[float], length: int) -> list[float | None]:
    output: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < length:
            output.append(None)
            continue
        output.append(max(values[index + 1 - length : index + 1]))
    return output


def rolling_low(values: list[float], length: int) -> list[float | None]:
    output: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < length:
            output.append(None)
            continue
        output.append(min(values[index + 1 - length : index + 1]))
    return output


def compute_metrics(
    initial_capital: float,
    trades: list[dict[str, Any]],
    equity_curve: list[dict[str, Any]],
    buy_hold_return: float,
    buy_hold_return_pct: float,
    buy_hold_start_price: float = 0.0,
    buy_hold_end_price: float = 0.0,
    buy_hold_max_drawdown_pct: float = 0.0,
) -> dict[str, Any]:
    periodic = periodic_equity_metrics(equity_curve, initial_capital)
    empty_exit_metrics = {
        "stop_exit_net_pnl": 0.0,
        "stop_exit_profit_factor": 0.0,
        "stop_exit_win_rate_pct": 0.0,
        "stop_exit_pnl_share_pct": 0.0,
        "reverse_exit_net_pnl": 0.0,
        "reverse_exit_profit_factor": 0.0,
        "reverse_exit_win_rate_pct": 0.0,
    }
    if not trades:
        return {
            "initial_capital": initial_capital,
            "net_pnl": 0.0,
            "return_pct": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "profit_factor": 0.0,
            "expected_payoff": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "daily_sharpe": periodic["daily_sharpe"],
            "daily_sortino": periodic["daily_sortino"],
            "daily_volatility_pct": periodic["daily_volatility_pct"],
            "worst_daily_return_pct": periodic["worst_daily_return_pct"],
            "positive_day_pct": periodic["positive_day_pct"],
            "daily_return_count": periodic["daily_return_count"],
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "percent_profitable": 0.0,
            "avg_pnl": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "ratio_avg_win_loss": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "avg_bars_in_trade": 0.0,
            "avg_bars_winning": 0.0,
            "avg_bars_losing": 0.0,
            "max_equity_drawdown": 0.0,
            "max_equity_drawdown_pct": 0.0,
            "max_equity_runup": 0.0,
            "avg_entry_exposure_pct": 0.0,
            "max_entry_exposure_pct": 0.0,
            "avg_initial_risk_pct": 0.0,
            "max_initial_risk_pct": 0.0,
            "buy_hold_return": buy_hold_return,
            "buy_hold_return_pct": buy_hold_return_pct,
            "buy_hold_start_price": buy_hold_start_price,
            "buy_hold_end_price": buy_hold_end_price,
            "buy_hold_max_drawdown_pct": buy_hold_max_drawdown_pct,
            "calmar": 0.0,
            "buy_hold_calmar": 0.0,
            "calmar_delta": 0.0,
            "outperformance": -buy_hold_return,
            "outperformance_pct": -buy_hold_return_pct,
            **empty_exit_metrics,
        }
    pnls = [trade["net_pnl"] for trade in trades]
    returns = [trade["return_on_equity_pct"] / 100 for trade in trades]
    wins = [trade for trade in trades if trade["net_pnl"] > 0]
    losses = [trade for trade in trades if trade["net_pnl"] < 0]
    exposures = [float(trade.get("entry_exposure_pct", 0.0)) for trade in trades]
    risk_pcts = [float(trade.get("initial_risk_pct", 0.0)) for trade in trades]
    gross_profit = sum(trade["net_pnl"] for trade in wins)
    gross_loss = abs(sum(trade["net_pnl"] for trade in losses))
    exit_metrics = exit_reason_risk_metrics(trades)
    avg_return = sum(returns) / len(returns)
    variance = sum((item - avg_return) ** 2 for item in returns) / len(returns)
    downside = [item for item in returns if item < 0]
    downside_variance = sum(item**2 for item in downside) / len(downside) if downside else 0.0
    largest_win = max(pnls)
    largest_loss = min(pnls)
    avg_win = gross_profit / len(wins) if wins else 0.0
    avg_loss = sum(trade["net_pnl"] for trade in losses) / len(losses) if losses else 0.0
    drawdown = 0.0
    drawdown_pct = 0.0
    runup = 0.0
    peak = initial_capital
    trough = initial_capital
    for point in equity_curve:
        peak = max(peak, point["equity"])
        trough = min(trough, point["equity"])
        drawdown = max(drawdown, peak - point["equity"])
        drawdown_pct = max(drawdown_pct, ((peak - point["equity"]) / peak) * 100 if peak else 0.0)
        runup = max(runup, point["equity"] - trough)
    return_pct = (sum(pnls) / initial_capital) * 100
    calmar = return_pct / drawdown_pct if drawdown_pct > 0 else (return_pct if return_pct > 0 else 0.0)
    buy_hold_calmar = (
        buy_hold_return_pct / buy_hold_max_drawdown_pct
        if buy_hold_max_drawdown_pct > 0
        else (buy_hold_return_pct if buy_hold_return_pct > 0 else 0.0)
    )
    return {
        "initial_capital": round(initial_capital, 2),
        "net_pnl": round(sum(pnls), 2),
        "return_pct": round(return_pct, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": round(gross_profit / gross_loss, 4) if gross_loss else round(gross_profit, 4),
        "expected_payoff": round(sum(pnls) / len(pnls), 2),
        "sharpe": round((avg_return / math.sqrt(variance)) * math.sqrt(len(returns)), 4) if variance > 0 else 0.0,
        "sortino": round((avg_return / math.sqrt(downside_variance)) * math.sqrt(len(returns)), 4) if downside_variance > 0 else 0.0,
        "daily_sharpe": periodic["daily_sharpe"],
        "daily_sortino": periodic["daily_sortino"],
        "daily_volatility_pct": periodic["daily_volatility_pct"],
        "worst_daily_return_pct": periodic["worst_daily_return_pct"],
        "positive_day_pct": periodic["positive_day_pct"],
        "daily_return_count": periodic["daily_return_count"],
        "total_trades": len(trades),
        "winning_trades": len(wins),
        "losing_trades": len(losses),
        "percent_profitable": round((len(wins) / len(trades)) * 100, 2),
        "avg_pnl": round(sum(pnls) / len(pnls), 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "ratio_avg_win_loss": round(abs(avg_win / avg_loss), 4) if avg_loss else 0.0,
        "largest_win": round(largest_win, 2),
        "largest_loss": round(largest_loss, 2),
        "avg_bars_in_trade": round(sum(trade["bars_held"] for trade in trades) / len(trades), 2),
        "avg_bars_winning": round(sum(trade["bars_held"] for trade in wins) / len(wins), 2) if wins else 0.0,
        "avg_bars_losing": round(sum(trade["bars_held"] for trade in losses) / len(losses), 2) if losses else 0.0,
        "max_equity_drawdown": round(drawdown, 2),
        "max_equity_drawdown_pct": round(drawdown_pct, 2),
        "max_equity_runup": round(runup, 2),
        "avg_entry_exposure_pct": round(sum(exposures) / len(exposures), 2) if exposures else 0.0,
        "max_entry_exposure_pct": round(max(exposures), 2) if exposures else 0.0,
        "avg_initial_risk_pct": round(sum(risk_pcts) / len(risk_pcts), 4) if risk_pcts else 0.0,
        "max_initial_risk_pct": round(max(risk_pcts), 4) if risk_pcts else 0.0,
        "buy_hold_return": round(buy_hold_return, 2),
        "buy_hold_return_pct": round(buy_hold_return_pct, 2),
        "buy_hold_start_price": round(buy_hold_start_price, 4),
        "buy_hold_end_price": round(buy_hold_end_price, 4),
        "buy_hold_max_drawdown_pct": round(buy_hold_max_drawdown_pct, 2),
        "calmar": round(calmar, 4),
        "buy_hold_calmar": round(buy_hold_calmar, 4),
        "calmar_delta": round(calmar - buy_hold_calmar, 4),
        "outperformance": round(sum(pnls) - buy_hold_return, 2),
        "outperformance_pct": round(return_pct - buy_hold_return_pct, 2),
        **exit_metrics,
    }


def exit_reason_risk_metrics(trades: list[dict[str, Any]]) -> dict[str, float]:
    output: dict[str, float] = {}
    total_net = sum(float(trade.get("net_pnl", 0.0)) for trade in trades)
    for reason in ("stop", "reverse"):
        segment = [trade for trade in trades if trade.get("reason") == reason]
        wins = [trade for trade in segment if float(trade.get("net_pnl", 0.0)) > 0]
        losses = [trade for trade in segment if float(trade.get("net_pnl", 0.0)) < 0]
        gross_profit = sum(float(trade.get("net_pnl", 0.0)) for trade in wins)
        gross_loss = abs(sum(float(trade.get("net_pnl", 0.0)) for trade in losses))
        net_pnl = gross_profit - gross_loss
        output[f"{reason}_exit_net_pnl"] = round(net_pnl, 2)
        output[f"{reason}_exit_profit_factor"] = round(gross_profit / gross_loss, 4) if gross_loss else round(gross_profit, 4)
        output[f"{reason}_exit_win_rate_pct"] = round((len(wins) / len(segment)) * 100, 2) if segment else 0.0
    output["stop_exit_pnl_share_pct"] = round((output["stop_exit_net_pnl"] / total_net) * 100, 2) if total_net > 0 else 0.0
    return output


def periodic_equity_metrics(equity_curve: list[dict[str, Any]], initial_capital: float) -> dict[str, float]:
    daily_closes: dict[str, float] = {}
    for point in equity_curve:
        ts = str(point.get("ts", ""))
        if not ts:
            continue
        day = ts[:10]
        daily_closes[day] = float(point.get("equity", initial_capital))
    returns: list[float] = []
    previous = initial_capital
    for day in sorted(daily_closes):
        close = daily_closes[day]
        if previous > 0:
            returns.append((close - previous) / previous)
        previous = close
    if not returns:
        return {
            "daily_sharpe": 0.0,
            "daily_sortino": 0.0,
            "daily_volatility_pct": 0.0,
            "worst_daily_return_pct": 0.0,
            "positive_day_pct": 0.0,
            "daily_return_count": 0,
        }
    avg_return = sum(returns) / len(returns)
    variance = sum((item - avg_return) ** 2 for item in returns) / len(returns)
    downside = [item for item in returns if item < 0]
    downside_variance = sum(item**2 for item in downside) / len(downside) if downside else 0.0
    annualizer = math.sqrt(365)
    return {
        "daily_sharpe": round((avg_return / math.sqrt(variance)) * annualizer, 4) if variance > 0 else 0.0,
        "daily_sortino": round((avg_return / math.sqrt(downside_variance)) * annualizer, 4) if downside_variance > 0 else 0.0,
        "daily_volatility_pct": round(math.sqrt(variance) * annualizer * 100, 2) if variance > 0 else 0.0,
        "worst_daily_return_pct": round(min(returns) * 100, 2),
        "positive_day_pct": round((sum(1 for item in returns if item > 0) / len(returns)) * 100, 2),
        "daily_return_count": len(returns),
    }


def buy_hold_drawdown_pct(bars: list[Bar], start_index: int) -> float:
    if not bars or start_index >= len(bars):
        return 0.0
    peak = bars[start_index].close
    max_drawdown = 0.0
    for bar in bars[start_index:]:
        peak = max(peak, bar.close)
        if peak:
            max_drawdown = max(max_drawdown, ((peak - bar.close) / peak) * 100)
    return max_drawdown


def benchmark_warmup_index(parameters: dict[str, Any], bar_count: int) -> int:
    if bar_count <= 1:
        return 0
    if "fast_len" in parameters:
        warmup = max(
            int(parameters["fast_len"]),
            int(parameters["slow_len"]),
            int(parameters["atr_len"]),
            int(parameters["noise_lookback"]) + 1,
        )
    else:
        warmup = max(
            int(parameters.get("gann_high_period", 13)),
            int(parameters.get("gann_low_period", 21)),
            int(parameters.get("donchian_length", 55)),
            int(parameters.get("atr_len", 14)),
        )
    return min(warmup, bar_count - 1)


class BacktestEngine:
    def run(self, spec: dict[str, Any], bars: list[Bar]) -> dict[str, Any]:
        engine_id = spec.get("engine_id")
        if engine_id == "ma_cross_atr_stop_v1":
            return self._run_ma_cross_atr_stop(spec, bars)
        if engine_id == "ghl_dc_breakout_v1":
            return self._run_ghl_dc_breakout(spec, bars)
        raise HTTPException(status_code=400, detail=f"Unsupported engine: {engine_id}")

    def _run_ma_cross_atr_stop(self, spec: dict[str, Any], bars: list[Bar]) -> dict[str, Any]:
        parameters = spec["parameters"]
        closes = [bar.close for bar in bars]
        ma_kind = parameters.get("ma_kind", "sma").lower()
        ma_fn = sma if ma_kind == "sma" else ema
        fast = ma_fn(closes, int(parameters["fast_len"]))
        slow = ma_fn(closes, int(parameters["slow_len"]))
        atr_values = atr(bars, int(parameters["atr_len"]))
        short_quality_gate_enabled = bool(parameters.get("short_quality_gate_enabled", False))
        short_quality_gate_values = (
            sma(closes, int(parameters.get("short_quality_gate_len_bars", 0)))
            if short_quality_gate_enabled
            else []
        )

        price_cross_fast: list[bool] = []
        for index, bar in enumerate(bars):
            if index == 0 or fast[index] is None or fast[index - 1] is None:
                price_cross_fast.append(False)
                continue
            previous_relation = closes[index - 1] - float(fast[index - 1])
            current_relation = closes[index] - float(fast[index])
            crossed = (previous_relation <= 0 < current_relation) or (previous_relation >= 0 > current_relation)
            price_cross_fast.append(crossed)

        position: Position | None = None
        trades: list[dict[str, Any]] = []
        equity_curve: list[dict[str, Any]] = []
        equity = float(parameters.get("initial_capital", 100_000.0))
        tick_size = float(parameters.get("tick_size", 0.01))
        slippage = int(parameters.get("slippage_ticks", 0)) * tick_size
        commission_pct = float(parameters.get("commission_pct", 0.0)) / 100
        mt5_bar_proxy = parameters.get("execution_model", "research_bar_close") == "mt5_bar_proxy"
        pending_entry: dict[str, Any] | None = None
        diagnostics = {
            "bars": len(bars),
            "signals_long": 0,
            "signals_short": 0,
            "entries": 0,
            "stop_exits": 0,
            "reverse_exits": 0,
            "breakeven_stop_moves": 0,
            "short_quality_gate_blocks": 0,
            "time_risk_filter_blocks": 0,
            "entry_exposure_gate_blocks": 0,
            "entry_exposure_gate_long_blocks": 0,
            "entry_exposure_gate_short_blocks": 0,
            "hybrid_time_decay_triage_exits": 0,
            "hybrid_reverse_exit_blocks": 0,
            "reverse_confirmation_candidates": 0,
            "reverse_confirmation_exits_allowed": 0,
            "reverse_confirmation_suppressed": 0,
            "reverse_confirmation_adverse_escape_allowed": 0,
            "reverse_confirmation_suppressed_net_pnl": 0.0,
            "time_decay_exits": 0,
            "time_decay_confirmation_candidates": 0,
            "time_decay_confirmation_exits": 0,
            "time_decay_confirmation_suppressed": 0,
            "time_decay_confirmation_suppressed_net_pnl": 0.0,
            "mt5_stop_modify_rejects": 0,
            "time_exits": 0,
        }
        warmup = max(
            int(parameters["fast_len"]),
            int(parameters["slow_len"]),
            int(parameters["atr_len"]),
            int(parameters["noise_lookback"]) + 1,
        )

        for index, bar in enumerate(bars):
            if index < warmup or fast[index] is None or slow[index] is None or atr_values[index] is None:
                equity_curve.append({"ts": bar.ts.isoformat(), "equity": round(equity, 2)})
                continue

            if mt5_bar_proxy and pending_entry:
                direction = int(pending_entry["direction"])
                if position and position.direction != direction:
                    exit_price = max(bar.open - slippage, 0.0) if position.direction == 1 else bar.open + slippage
                    trade = self._close_trade(
                        position=position,
                        bar=bar,
                        index=index,
                        price=exit_price,
                        reason="reverse",
                        commission_pct=commission_pct,
                        equity_before=equity,
                    )
                    trades.append(trade)
                    equity += trade["net_pnl"]
                    diagnostics["reverse_exits"] += 1
                    position = None
                if position is None:
                    fill = bar.open + slippage if direction == 1 else max(bar.open - slippage, 0.0)
                    stop = (
                        fill - (float(pending_entry["atr_value"]) * float(parameters["stop_mult"]))
                        if direction == 1
                        else fill + (float(pending_entry["atr_value"]) * float(parameters["stop_mult"]))
                    )
                    quantity = self._position_quantity(parameters, equity, fill, stop)
                    entry_notional = fill * quantity
                    if self._entry_exposure_gate_allows_entry(
                        parameters=parameters,
                        direction=direction,
                        equity=equity,
                        entry_notional=entry_notional,
                        diagnostics=diagnostics,
                    ):
                        signal_index = int(pending_entry["signal_index"])
                        entry_features = self._entry_features(
                            bars=bars,
                            index=signal_index,
                            direction=direction,
                            fast=fast,
                            slow=slow,
                            atr_values=atr_values,
                            cross_count=int(pending_entry["cross_count"]),
                            stop_price=stop,
                            entry_price=fill,
                        )
                        position = Position(
                            direction=direction,
                            entry_index=index,
                            entry_ts=bar.ts,
                            entry_price=fill,
                            stop_price=stop,
                            quantity=quantity,
                            entry_commission=fill * quantity * commission_pct,
                            entry_equity=equity,
                            entry_notional=entry_notional,
                            initial_risk_per_unit=abs(fill - stop),
                            stop_initialized_on_index=index,
                            entry_features=entry_features,
                        )
                        diagnostics["entries"] += 1
                pending_entry = None

            if position:
                self._update_excursion(position, bar)

            stop_can_trigger = (
                position is not None
                and (index >= position.stop_initialized_on_index if mt5_bar_proxy else index > position.stop_initialized_on_index)
            )
            if position and stop_can_trigger:
                if position.direction == 1 and bar.low <= position.stop_price:
                    trade = self._close_trade(
                        position=position,
                        bar=bar,
                        index=index,
                        price=max(position.stop_price - slippage, 0.0),
                        reason="stop",
                        commission_pct=commission_pct,
                        equity_before=equity,
                    )
                    trades.append(trade)
                    equity += trade["net_pnl"]
                    diagnostics["stop_exits"] += 1
                    position = None
                elif position.direction == -1 and bar.high >= position.stop_price:
                    trade = self._close_trade(
                        position=position,
                        bar=bar,
                        index=index,
                        price=position.stop_price + slippage,
                        reason="stop",
                        commission_pct=commission_pct,
                        equity_before=equity,
                    )
                    trades.append(trade)
                    equity += trade["net_pnl"]
                    diagnostics["stop_exits"] += 1
                    position = None

            if position and parameters.get("breakeven_stop_enabled", False):
                initial_risk = abs(position.entry_price - position.stop_price)
                if initial_risk:
                    trigger_r = float(parameters.get("breakeven_trigger_mfe_r", 1.0))
                    lock_r = float(parameters.get("breakeven_lock_r", 0.0))
                    mfe_r = position.max_favorable_excursion / initial_risk
                    if mfe_r >= trigger_r:
                        if position.direction == 1:
                            new_stop = position.entry_price + (initial_risk * lock_r)
                            if mt5_bar_proxy and new_stop >= bar.close:
                                diagnostics["mt5_stop_modify_rejects"] += 1
                                new_stop = position.stop_price
                            if new_stop > position.stop_price:
                                position.stop_price = new_stop
                                position.stop_moved_to_breakeven = True
                                diagnostics["breakeven_stop_moves"] += 1
                        else:
                            new_stop = position.entry_price - (initial_risk * lock_r)
                            if mt5_bar_proxy and new_stop <= bar.close:
                                diagnostics["mt5_stop_modify_rejects"] += 1
                                new_stop = position.stop_price
                            if new_stop < position.stop_price:
                                position.stop_price = new_stop
                                position.stop_moved_to_breakeven = True
                                diagnostics["breakeven_stop_moves"] += 1

            if position and parameters.get("hybrid_time_decay_triage_enabled", False):
                bars_held = index - position.entry_index
                checkpoints = parameters.get("hybrid_time_decay_triage_checkpoints", [10, 20, 30])
                if isinstance(checkpoints, (int, float)):
                    checkpoint_set = {int(checkpoints)}
                else:
                    checkpoint_set = {int(item) for item in checkpoints}
                initial_risk = abs(position.entry_price - position.stop_price)
                if initial_risk and bars_held in checkpoint_set:
                    if position.direction == 1:
                        unrealized = bar.close - position.entry_price
                    else:
                        unrealized = position.entry_price - bar.close
                    unrealized_r = unrealized / initial_risk
                    mfe_r = position.max_favorable_excursion / initial_risk
                    max_unrealized_r = float(parameters.get("hybrid_time_decay_triage_max_unrealized_r", 0.10))
                    max_mfe_r = float(parameters.get("hybrid_time_decay_triage_max_mfe_r", 0.25))
                    if unrealized_r <= max_unrealized_r and mfe_r <= max_mfe_r:
                        if not self._time_decay_confirmation_allows_exit(
                            parameters=parameters,
                            position=position,
                            unrealized_r=unrealized_r,
                            mfe_r=mfe_r,
                            diagnostics=diagnostics,
                        ):
                            continue
                        exit_price = max(bar.close - slippage, 0.0) if position.direction == 1 else bar.close + slippage
                        trade = self._close_trade(
                            position=position,
                            bar=bar,
                            index=index,
                            price=exit_price,
                            reason="hybrid_time_decay_triage",
                            commission_pct=commission_pct,
                            equity_before=equity,
                        )
                        trades.append(trade)
                        equity += trade["net_pnl"]
                        diagnostics["hybrid_time_decay_triage_exits"] += 1
                        position = None

            if position and parameters.get("time_decay_exit_enabled", False):
                bars_held = index - position.entry_index
                decay_bars = int(parameters.get("time_decay_bars", 0))
                initial_risk = abs(position.entry_price - position.stop_price)
                mfe_r = position.max_favorable_excursion / initial_risk if initial_risk else 0.0
                if decay_bars > 0 and bars_held >= decay_bars and mfe_r < float(parameters.get("time_decay_min_mfe_r", 0.0)):
                    if position.direction == 1:
                        unrealized = bar.close - position.entry_price
                    else:
                        unrealized = position.entry_price - bar.close
                    unrealized_r = unrealized / initial_risk if initial_risk else 0.0
                    if not self._time_decay_confirmation_allows_exit(
                        parameters=parameters,
                        position=position,
                        unrealized_r=unrealized_r,
                        mfe_r=mfe_r,
                        diagnostics=diagnostics,
                    ):
                        continue
                    exit_price = max(bar.close - slippage, 0.0) if position.direction == 1 else bar.close + slippage
                    trade = self._close_trade(
                        position=position,
                        bar=bar,
                        index=index,
                        price=exit_price,
                        reason="time_decay",
                        commission_pct=commission_pct,
                        equity_before=equity,
                    )
                    trades.append(trade)
                    equity += trade["net_pnl"]
                    diagnostics["time_decay_exits"] += 1
                    position = None

            noise_lookback = int(parameters["noise_lookback"])
            cross_count = sum(1 for item in price_cross_fast[max(0, index - noise_lookback + 1) : index + 1] if item)
            cross_count_ok = cross_count <= int(parameters["max_no_cross"])
            prev_fast = float(fast[index - 1])
            prev_slow = float(slow[index - 1])
            curr_fast = float(fast[index])
            curr_slow = float(slow[index])

            crossover = prev_fast <= prev_slow and curr_fast > curr_slow
            crossunder = prev_fast >= prev_slow and curr_fast < curr_slow
            pullback_long = (
                bar.close < curr_fast
                and bar.close > curr_slow
                and curr_fast > curr_slow
                and cross_count_ok
            )
            pullback_short = (
                bar.close > curr_fast
                and bar.close < curr_slow
                and curr_fast < curr_slow
                and cross_count_ok
            )

            entry_mode = parameters.get("entry_mode", "crossover_only")
            long_signal = crossover and cross_count_ok
            short_signal = crossunder and cross_count_ok
            if entry_mode == "crossover_plus_pullback":
                long_signal = long_signal or pullback_long
                short_signal = short_signal or pullback_short

            if parameters.get("allow_long", True) and long_signal:
                diagnostics["signals_long"] += 1
            else:
                long_signal = False

            if short_signal and short_quality_gate_enabled:
                rule = parameters.get("short_quality_gate_rule", "block_below_sma")
                context_value = short_quality_gate_values[index]
                block_short = context_value is None
                if context_value is not None and rule == "block_below_sma":
                    block_short = bar.close < float(context_value)
                elif context_value is not None and rule == "block_above_sma":
                    block_short = bar.close > float(context_value)
                if block_short:
                    diagnostics["short_quality_gate_blocks"] += 1
                    short_signal = False

            if parameters.get("allow_short", True) and short_signal:
                diagnostics["signals_short"] += 1
            else:
                short_signal = False

            entry_long_signal = long_signal
            entry_short_signal = short_signal
            if parameters.get("time_risk_filter_enabled", False) and (entry_long_signal or entry_short_signal):
                blocked_weekdays = {int(item) for item in parameters.get("time_risk_block_weekdays", [])}
                blocked_hours = {int(item) for item in parameters.get("time_risk_block_utc_hours", [])}
                if bar.ts.weekday() in blocked_weekdays or bar.ts.hour in blocked_hours:
                    diagnostics["time_risk_filter_blocks"] += int(entry_long_signal) + int(entry_short_signal)
                    entry_long_signal = False
                    entry_short_signal = False

            entry_at_close = bar.close
            reverse_exit_blocked = False
            if position and parameters.get("hybrid_reverse_exit_triage_enabled", False):
                initial_risk = abs(position.entry_price - position.stop_price)
                mfe_r = position.max_favorable_excursion / initial_risk if initial_risk else 0.0
                min_mfe_r = float(parameters.get("hybrid_reverse_exit_min_mfe_r", 0.25))
                if (
                    (position.direction == 1 and short_signal)
                    or (position.direction == -1 and long_signal)
                ) and mfe_r < min_mfe_r:
                    diagnostics["hybrid_reverse_exit_blocks"] += 1
                    reverse_exit_blocked = True
                    entry_long_signal = False
                    entry_short_signal = False

            if position and not reverse_exit_blocked:
                if not self._reverse_confirmation_allows_exit(
                    parameters=parameters,
                    position=position,
                    index=index,
                    current_close=bar.close,
                    long_signal=long_signal,
                    short_signal=short_signal,
                    diagnostics=diagnostics,
                ):
                    reverse_exit_blocked = True
                    entry_long_signal = False
                    entry_short_signal = False

            if not mt5_bar_proxy and position and position.direction == 1 and short_signal and not reverse_exit_blocked:
                trade = self._close_trade(
                    position=position,
                    bar=bar,
                    index=index,
                    price=max(entry_at_close - slippage, 0.0),
                    reason="reverse",
                    commission_pct=commission_pct,
                    equity_before=equity,
                )
                trades.append(trade)
                equity += trade["net_pnl"]
                diagnostics["reverse_exits"] += 1
                position = None
            elif not mt5_bar_proxy and position and position.direction == -1 and long_signal and not reverse_exit_blocked:
                trade = self._close_trade(
                    position=position,
                    bar=bar,
                    index=index,
                    price=entry_at_close + slippage,
                    reason="reverse",
                    commission_pct=commission_pct,
                    equity_before=equity,
                )
                trades.append(trade)
                equity += trade["net_pnl"]
                diagnostics["reverse_exits"] += 1
                position = None

            if mt5_bar_proxy:
                if entry_long_signal:
                    pending_entry = {
                        "direction": 1,
                        "atr_value": float(atr_values[index]),
                        "signal_index": index,
                        "cross_count": cross_count,
                    }
                elif entry_short_signal:
                    pending_entry = {
                        "direction": -1,
                        "atr_value": float(atr_values[index]),
                        "signal_index": index,
                        "cross_count": cross_count,
                    }
            elif position is None:
                if entry_long_signal:
                    fill = entry_at_close + slippage
                    stop = fill - (float(atr_values[index]) * float(parameters["stop_mult"]))
                    quantity = self._position_quantity(parameters, equity, fill, stop)
                    entry_notional = fill * quantity
                    if not self._entry_exposure_gate_allows_entry(
                        parameters=parameters,
                        direction=1,
                        equity=equity,
                        entry_notional=entry_notional,
                        diagnostics=diagnostics,
                    ):
                        equity_curve.append({"ts": bar.ts.isoformat(), "equity": round(equity, 2)})
                        continue
                    commission = fill * quantity * commission_pct
                    initial_risk_per_unit = abs(fill - stop)
                    entry_features = self._entry_features(
                        bars=bars,
                        index=index,
                        direction=1,
                        fast=fast,
                        slow=slow,
                        atr_values=atr_values,
                        cross_count=cross_count,
                        stop_price=stop,
                        entry_price=fill,
                    )
                    position = Position(
                        direction=1,
                        entry_index=index,
                        entry_ts=bar.ts,
                        entry_price=fill,
                        stop_price=stop,
                        quantity=quantity,
                        entry_commission=commission,
                        entry_equity=equity,
                        entry_notional=entry_notional,
                        initial_risk_per_unit=initial_risk_per_unit,
                        stop_initialized_on_index=index,
                        entry_features=entry_features,
                    )
                    diagnostics["entries"] += 1
                elif entry_short_signal:
                    fill = max(entry_at_close - slippage, 0.0)
                    stop = fill + (float(atr_values[index]) * float(parameters["stop_mult"]))
                    quantity = self._position_quantity(parameters, equity, fill, stop)
                    entry_notional = fill * quantity
                    if not self._entry_exposure_gate_allows_entry(
                        parameters=parameters,
                        direction=-1,
                        equity=equity,
                        entry_notional=entry_notional,
                        diagnostics=diagnostics,
                    ):
                        equity_curve.append({"ts": bar.ts.isoformat(), "equity": round(equity, 2)})
                        continue
                    commission = fill * quantity * commission_pct
                    initial_risk_per_unit = abs(fill - stop)
                    entry_features = self._entry_features(
                        bars=bars,
                        index=index,
                        direction=-1,
                        fast=fast,
                        slow=slow,
                        atr_values=atr_values,
                        cross_count=cross_count,
                        stop_price=stop,
                        entry_price=fill,
                    )
                    position = Position(
                        direction=-1,
                        entry_index=index,
                        entry_ts=bar.ts,
                        entry_price=fill,
                        stop_price=stop,
                        quantity=quantity,
                        entry_commission=commission,
                        entry_equity=equity,
                        entry_notional=entry_notional,
                        initial_risk_per_unit=initial_risk_per_unit,
                        stop_initialized_on_index=index,
                        entry_features=entry_features,
                    )
                    diagnostics["entries"] += 1

            equity_curve.append({"ts": bar.ts.isoformat(), "equity": round(equity, 2)})

        if position:
            last_bar = bars[-1]
            exit_price = max(last_bar.close - slippage, 0.0) if position.direction == 1 else last_bar.close + slippage
            trade = self._close_trade(
                position=position,
                bar=last_bar,
                index=len(bars) - 1,
                price=exit_price,
                reason="time_exit",
                commission_pct=commission_pct,
                equity_before=equity,
            )
            trades.append(trade)
            equity += trade["net_pnl"]
            diagnostics["time_exits"] += 1
            equity_curve[-1] = {"ts": last_bar.ts.isoformat(), "equity": round(equity, 2)}

        diagnostics["time_decay_confirmation_suppressed_net_pnl"] = round(
            sum(
                trade["net_pnl"]
                for trade in trades
                if int(trade.get("time_decay_confirmation_suppressed", 0)) > 0
            ),
            2,
        )
        diagnostics["reverse_confirmation_suppressed_net_pnl"] = round(
            sum(
                trade["net_pnl"]
                for trade in trades
                if int(trade.get("reverse_confirmation_suppressed", 0)) > 0
            ),
            2,
        )
        initial_capital = float(parameters.get("initial_capital", 100_000.0))
        buy_hold_start_price = bars[warmup].close if len(bars) > warmup else bars[0].close
        buy_hold_end_price = bars[-1].close
        buy_hold_return_pct = (
            ((buy_hold_end_price - buy_hold_start_price) / buy_hold_start_price) * 100
            if buy_hold_start_price
            else 0.0
        )
        buy_hold_return = initial_capital * (buy_hold_return_pct / 100)
        buy_hold_max_drawdown_pct = buy_hold_drawdown_pct(bars, warmup)
        metrics = compute_metrics(
            initial_capital=initial_capital,
            trades=trades,
            equity_curve=equity_curve,
            buy_hold_return=buy_hold_return,
            buy_hold_return_pct=buy_hold_return_pct,
            buy_hold_start_price=buy_hold_start_price,
            buy_hold_end_price=buy_hold_end_price,
            buy_hold_max_drawdown_pct=buy_hold_max_drawdown_pct,
        )
        return {
            "metrics": metrics,
            "trades": trades,
            "equity_curve": equity_curve,
            "diagnostics": diagnostics,
        }

    @staticmethod
    def _time_decay_confirmation_allows_exit(
        *,
        parameters: dict[str, Any],
        position: Position,
        unrealized_r: float,
        mfe_r: float,
        diagnostics: dict[str, Any],
    ) -> bool:
        if not parameters.get("time_decay_triage_confirmation_enabled", False):
            return True
        diagnostics["time_decay_confirmation_candidates"] += 1
        max_unrealized_r = float(parameters.get("time_decay_confirm_max_unrealized_r", 0.0))
        max_mfe_r = float(parameters.get("time_decay_confirm_max_mfe_r", 0.35))
        require_no_breakeven = bool(parameters.get("time_decay_confirm_require_no_breakeven_move", False))
        confirmed = unrealized_r <= max_unrealized_r and mfe_r <= max_mfe_r
        if require_no_breakeven and position.stop_moved_to_breakeven:
            confirmed = False
        if confirmed:
            diagnostics["time_decay_confirmation_exits"] += 1
            return True
        diagnostics["time_decay_confirmation_suppressed"] += 1
        position.time_decay_confirmation_suppressed += 1
        return False

    @staticmethod
    def _reverse_confirmation_allows_exit(
        *,
        parameters: dict[str, Any],
        position: Position,
        index: int,
        current_close: float,
        long_signal: bool,
        short_signal: bool,
        diagnostics: dict[str, Any],
    ) -> bool:
        if not parameters.get("reverse_confirmation_enabled", False):
            return True
        opposite_signal = (position.direction == 1 and short_signal) or (position.direction == -1 and long_signal)
        if not opposite_signal:
            return True
        diagnostics["reverse_confirmation_candidates"] += 1
        initial_risk = abs(position.entry_price - position.stop_price)
        if not initial_risk:
            diagnostics["reverse_confirmation_exits_allowed"] += 1
            return True
        bars_held = index - position.entry_index
        mfe_r = position.max_favorable_excursion / initial_risk
        if position.direction == 1:
            unrealized = current_close - position.entry_price
        else:
            unrealized = position.entry_price - current_close
        unrealized_r = unrealized / initial_risk

        max_bars = int(parameters.get("reverse_confirm_max_bars", 2))
        min_mfe_r = float(parameters.get("reverse_confirm_min_mfe_r", 0.20))
        adverse_escape_r = float(parameters.get("reverse_confirm_allow_if_unrealized_r_lte", -0.35))
        require_no_breakeven = bool(parameters.get("reverse_confirm_require_no_breakeven_move", False))

        is_young = bars_held <= max_bars
        weak_excursion = mfe_r < min_mfe_r
        adverse_escape = unrealized_r <= adverse_escape_r
        suppress_reverse = is_young and weak_excursion and not adverse_escape
        if require_no_breakeven and position.stop_moved_to_breakeven:
            suppress_reverse = False

        if suppress_reverse:
            diagnostics["reverse_confirmation_suppressed"] += 1
            position.reverse_confirmation_suppressed += 1
            return False
        if adverse_escape:
            diagnostics["reverse_confirmation_adverse_escape_allowed"] += 1
        diagnostics["reverse_confirmation_exits_allowed"] += 1
        return True

    @staticmethod
    def _entry_exposure_gate_allows_entry(
        *,
        parameters: dict[str, Any],
        direction: int,
        equity: float,
        entry_notional: float,
        diagnostics: dict[str, Any],
    ) -> bool:
        if not parameters.get("entry_exposure_gate_enabled", False):
            return True
        exposure_pct = (entry_notional / equity) * 100 if equity > 0 else float("inf")
        max_exposure_pct = float(parameters.get("entry_exposure_gate_max_pct", 75.0))
        if exposure_pct <= max_exposure_pct:
            return True
        diagnostics["entry_exposure_gate_blocks"] += 1
        if direction == 1:
            diagnostics["entry_exposure_gate_long_blocks"] += 1
        else:
            diagnostics["entry_exposure_gate_short_blocks"] += 1
        return False

    def _run_ghl_dc_breakout(self, spec: dict[str, Any], bars: list[Bar]) -> dict[str, Any]:
        parameters = spec["parameters"]
        highs = [bar.high for bar in bars]
        lows = [bar.low for bar in bars]
        closes = [bar.close for bar in bars]
        gann_high_period = int(parameters.get("gann_high_period", 13))
        gann_low_period = int(parameters.get("gann_low_period", 21))
        donchian_length = int(parameters.get("donchian_length", 55))
        max_breakout_bars = int(parameters.get("max_breakout_bars", 7))
        atr_values = atr(bars, int(parameters.get("atr_len", 14)))
        sma_high = sma(highs, gann_high_period)
        sma_low = sma(lows, gann_low_period)
        dc_upper = rolling_high(highs, donchian_length)
        dc_lower = rolling_low(lows, donchian_length)

        hilo_values: list[float | None] = []
        state_values: list[int] = []
        state = 0
        for index, bar in enumerate(bars):
            if index > 0 and sma_high[index - 1] is not None and bar.close > float(sma_high[index - 1]):
                state = 1
            elif index > 0 and sma_low[index - 1] is not None and bar.close < float(sma_low[index - 1]):
                state = -1
            state_values.append(state)
            if state == -1:
                hilo_values.append(sma_high[index])
            elif state == 1:
                hilo_values.append(sma_low[index])
            else:
                hilo_values.append(None)

        position: Position | None = None
        trades: list[dict[str, Any]] = []
        equity_curve: list[dict[str, Any]] = []
        equity = float(parameters.get("initial_capital", 100_000.0))
        tick_size = float(parameters.get("tick_size", 0.01))
        slippage = int(parameters.get("slippage_ticks", 0)) * tick_size
        commission_pct = float(parameters.get("commission_pct", 0.0)) / 100
        mt5_bar_proxy = parameters.get("execution_model", "research_bar_close") == "mt5_bar_proxy"
        pending_entry: dict[str, Any] | None = None
        diagnostics = {
            "bars": len(bars),
            "gann_cross_up": 0,
            "gann_cross_down": 0,
            "signals_long": 0,
            "signals_short": 0,
            "entries": 0,
            "reverse_exits": 0,
            "gann_state_exits": 0,
            "stop_exits": 0,
            "breakeven_stop_moves": 0,
            "breakeven_stop_exits": 0,
            "time_risk_filter_blocks": 0,
            "time_risk_filter_long_blocks": 0,
            "time_risk_filter_short_blocks": 0,
            "mt5_invalid_lot_skips": 0,
            "expired_setups": 0,
            "time_exits": 0,
        }
        pending_long = False
        pending_long_bar = 0
        pending_long_breakout: float | None = None
        pending_short = False
        pending_short_bar = 0
        pending_short_breakdown: float | None = None
        last_gann_flip_index: int | None = None
        warmup = benchmark_warmup_index(parameters, len(bars))

        for index, bar in enumerate(bars):
            if index < warmup or hilo_values[index] is None or atr_values[index] is None:
                equity_curve.append({"ts": bar.ts.isoformat(), "equity": round(equity, 2)})
                continue

            if position:
                self._update_excursion(position, bar)

            if position and index > position.stop_initialized_on_index:
                if position.direction == 1 and bar.low <= position.stop_price:
                    reason = "breakeven_stop" if position.stop_moved_to_breakeven else "stop"
                    trade = self._close_trade(position, bar, index, max(position.stop_price - slippage, 0.0), reason, commission_pct, equity)
                    trades.append(trade)
                    equity += trade["net_pnl"]
                    if reason == "breakeven_stop":
                        diagnostics["breakeven_stop_exits"] += 1
                    else:
                        diagnostics["stop_exits"] += 1
                    position = None
                elif position.direction == -1 and bar.high >= position.stop_price:
                    reason = "breakeven_stop" if position.stop_moved_to_breakeven else "stop"
                    trade = self._close_trade(position, bar, index, position.stop_price + slippage, reason, commission_pct, equity)
                    trades.append(trade)
                    equity += trade["net_pnl"]
                    if reason == "breakeven_stop":
                        diagnostics["breakeven_stop_exits"] += 1
                    else:
                        diagnostics["stop_exits"] += 1
                    position = None

            if position and parameters.get("breakeven_stop_enabled", False):
                initial_risk = position.initial_risk_per_unit
                if initial_risk > 0:
                    trigger_r = float(parameters.get("breakeven_trigger_mfe_r", 1.0))
                    lock_r = float(parameters.get("breakeven_lock_r", 0.0))
                    if position.direction == 1:
                        favorable_r = (bar.high - position.entry_price) / initial_risk
                        if favorable_r >= trigger_r:
                            new_stop = position.entry_price + (initial_risk * lock_r)
                            if new_stop > position.stop_price:
                                position.stop_price = new_stop
                                position.stop_moved_to_breakeven = True
                                diagnostics["breakeven_stop_moves"] += 1
                    else:
                        favorable_r = (position.entry_price - bar.low) / initial_risk
                        if favorable_r >= trigger_r:
                            new_stop = position.entry_price - (initial_risk * lock_r)
                            if new_stop < position.stop_price:
                                position.stop_price = new_stop
                                position.stop_moved_to_breakeven = True
                                diagnostics["breakeven_stop_moves"] += 1

            previous_hilo = hilo_values[index - 1]
            current_hilo = hilo_values[index]
            gann_cross_up = (
                previous_hilo is not None
                and current_hilo is not None
                and closes[index - 1] <= float(previous_hilo)
                and bar.close > float(current_hilo)
            )
            gann_cross_down = (
                previous_hilo is not None
                and current_hilo is not None
                and closes[index - 1] >= float(previous_hilo)
                and bar.close < float(current_hilo)
            )
            if gann_cross_up:
                diagnostics["gann_cross_up"] += 1
                last_gann_flip_index = index
                pending_long = True
                pending_long_bar = index
                pending_long_breakout = dc_upper[index - 1] if index > 0 else None
                pending_short = False
                pending_short_breakdown = None
            if gann_cross_down:
                diagnostics["gann_cross_down"] += 1
                last_gann_flip_index = index
                pending_short = True
                pending_short_bar = index
                pending_short_breakdown = dc_lower[index - 1] if index > 0 else None
                pending_long = False
                pending_long_breakout = None

            long_age = index - pending_long_bar if pending_long else 0
            short_age = index - pending_short_bar if pending_short else 0
            long_signal = (
                pending_long
                and long_age <= max_breakout_bars
                and pending_long_breakout is not None
                and bar.high > pending_long_breakout
                and highs[index - 1] <= pending_long_breakout
            )
            short_signal = (
                pending_short
                and short_age <= max_breakout_bars
                and pending_short_breakdown is not None
                and bar.low < pending_short_breakdown
                and lows[index - 1] >= pending_short_breakdown
            )

            if pending_long and long_age > max_breakout_bars:
                pending_long = False
                pending_long_breakout = None
                diagnostics["expired_setups"] += 1
            if pending_short and short_age > max_breakout_bars:
                pending_short = False
                pending_short_breakdown = None
                diagnostics["expired_setups"] += 1

            close_long = position is not None and position.direction == 1 and bar.close < float(current_hilo) and state_values[index] == -1
            close_short = position is not None and position.direction == -1 and bar.close > float(current_hilo) and state_values[index] == 1
            if close_long or close_short:
                exit_price = max(bar.close - slippage, 0.0) if position and position.direction == 1 else bar.close + slippage
                trade = self._close_trade(position, bar, index, exit_price, "gann_state_exit", commission_pct, equity)
                trades.append(trade)
                equity += trade["net_pnl"]
                diagnostics["gann_state_exits"] += 1
                position = None

            if long_signal and parameters.get("allow_long", True):
                diagnostics["signals_long"] += 1
            else:
                long_signal = False
            if short_signal and parameters.get("allow_short", True):
                diagnostics["signals_short"] += 1
            else:
                short_signal = False

            if parameters.get("time_risk_filter_enabled", False):
                blocked_hours = {int(hour) for hour in parameters.get("time_risk_block_utc_hours", [])}
                blocked_weekdays = {int(day) for day in parameters.get("time_risk_block_weekdays", [])}
                is_blocked_time = bar.ts.hour in blocked_hours or bar.ts.weekday() in blocked_weekdays
                if is_blocked_time and long_signal:
                    diagnostics["time_risk_filter_blocks"] += 1
                    diagnostics["time_risk_filter_long_blocks"] += 1
                    long_signal = False
                if is_blocked_time and short_signal:
                    diagnostics["time_risk_filter_blocks"] += 1
                    diagnostics["time_risk_filter_short_blocks"] += 1
                    short_signal = False

            if position and position.direction == 1 and short_signal:
                trade = self._close_trade(position, bar, index, max(bar.close - slippage, 0.0), "reverse", commission_pct, equity)
                trades.append(trade)
                equity += trade["net_pnl"]
                diagnostics["reverse_exits"] += 1
                position = None
            elif position and position.direction == -1 and long_signal:
                trade = self._close_trade(position, bar, index, bar.close + slippage, "reverse", commission_pct, equity)
                trades.append(trade)
                equity += trade["net_pnl"]
                diagnostics["reverse_exits"] += 1
                position = None

            if position is None and long_signal:
                fill = bar.close + slippage
                stop = self._ghl_dc_initial_stop(parameters, 1, fill, bar, float(atr_values[index] or 0.0), dc_lower[index])
                quantity = self._position_quantity(parameters, equity, fill, stop)
                if quantity <= 0:
                    diagnostics["mt5_invalid_lot_skips"] += 1
                    pending_long = False
                    pending_long_breakout = None
                    equity_curve.append({"ts": bar.ts.isoformat(), "equity": round(equity, 2)})
                    continue
                features = self._ghl_dc_entry_features(
                    bars=bars,
                    index=index,
                    direction=1,
                    parameters=parameters,
                    atr_values=atr_values,
                    sma_high=sma_high,
                    sma_low=sma_low,
                    hilo_values=hilo_values,
                    state_values=state_values,
                    dc_upper=dc_upper,
                    dc_lower=dc_lower,
                    breakout_level=pending_long_breakout,
                    signal_age=long_age,
                    last_gann_flip_index=last_gann_flip_index,
                    stop_price=stop,
                    entry_price=fill,
                )
                position = self._open_position(1, index, bar, fill, stop, quantity, commission_pct, equity, features)
                diagnostics["entries"] += 1
                pending_long = False
                pending_long_breakout = None
            elif position is None and short_signal:
                fill = max(bar.close - slippage, 0.0)
                stop = self._ghl_dc_initial_stop(parameters, -1, fill, bar, float(atr_values[index] or 0.0), dc_upper[index])
                quantity = self._position_quantity(parameters, equity, fill, stop)
                if quantity <= 0:
                    diagnostics["mt5_invalid_lot_skips"] += 1
                    pending_short = False
                    pending_short_breakdown = None
                    equity_curve.append({"ts": bar.ts.isoformat(), "equity": round(equity, 2)})
                    continue
                features = self._ghl_dc_entry_features(
                    bars=bars,
                    index=index,
                    direction=-1,
                    parameters=parameters,
                    atr_values=atr_values,
                    sma_high=sma_high,
                    sma_low=sma_low,
                    hilo_values=hilo_values,
                    state_values=state_values,
                    dc_upper=dc_upper,
                    dc_lower=dc_lower,
                    breakout_level=pending_short_breakdown,
                    signal_age=short_age,
                    last_gann_flip_index=last_gann_flip_index,
                    stop_price=stop,
                    entry_price=fill,
                )
                position = self._open_position(-1, index, bar, fill, stop, quantity, commission_pct, equity, features)
                diagnostics["entries"] += 1
                pending_short = False
                pending_short_breakdown = None

            equity_curve.append({"ts": bar.ts.isoformat(), "equity": round(equity, 2)})

        if position:
            last_bar = bars[-1]
            exit_price = max(last_bar.close - slippage, 0.0) if position.direction == 1 else last_bar.close + slippage
            trade = self._close_trade(position, last_bar, len(bars) - 1, exit_price, "time_exit", commission_pct, equity)
            trades.append(trade)
            equity += trade["net_pnl"]
            diagnostics["time_exits"] += 1
            equity_curve[-1] = {"ts": last_bar.ts.isoformat(), "equity": round(equity, 2)}

        initial_capital = float(parameters.get("initial_capital", 100_000.0))
        buy_hold_start_price = bars[warmup].close if len(bars) > warmup else bars[0].close
        buy_hold_end_price = bars[-1].close
        buy_hold_return_pct = ((buy_hold_end_price - buy_hold_start_price) / buy_hold_start_price) * 100 if buy_hold_start_price else 0.0
        metrics = compute_metrics(
            initial_capital=initial_capital,
            trades=trades,
            equity_curve=equity_curve,
            buy_hold_return=initial_capital * (buy_hold_return_pct / 100),
            buy_hold_return_pct=buy_hold_return_pct,
            buy_hold_start_price=buy_hold_start_price,
            buy_hold_end_price=buy_hold_end_price,
            buy_hold_max_drawdown_pct=buy_hold_drawdown_pct(bars, warmup),
        )
        return {"metrics": metrics, "trades": trades, "equity_curve": equity_curve, "diagnostics": diagnostics}

    @staticmethod
    def _ghl_dc_initial_stop(parameters: dict[str, Any], direction: int, fill: float, bar: Bar, atr_value: float, channel_opposite: float | None) -> float:
        stop_mode = parameters.get("stop_mode", "atr")
        stop_mult = float(parameters.get("stop_mult", 2.5))
        atr_stop = fill - (atr_value * stop_mult) if direction == 1 else fill + (atr_value * stop_mult)
        if stop_mode == "donchian_opposite" and channel_opposite is not None:
            return min(float(channel_opposite), atr_stop) if direction == 1 else max(float(channel_opposite), atr_stop)
        if stop_mode == "bar_extreme":
            return min(bar.low, atr_stop) if direction == 1 else max(bar.high, atr_stop)
        return atr_stop

    @staticmethod
    def _ghl_dc_entry_features(
        bars: list[Bar],
        index: int,
        direction: int,
        parameters: dict[str, Any],
        atr_values: list[float | None],
        sma_high: list[float | None],
        sma_low: list[float | None],
        hilo_values: list[float | None],
        state_values: list[int],
        dc_upper: list[float | None],
        dc_lower: list[float | None],
        breakout_level: float | None,
        signal_age: int,
        last_gann_flip_index: int | None,
        stop_price: float,
        entry_price: float,
    ) -> dict[str, Any]:
        bar = bars[index]
        lookback = min(index, 20)
        prior = bars[index - lookback : index + 1]
        prior_close = bars[index - lookback].close if lookback else bar.close
        prior_high = max(item.high for item in prior)
        prior_low = min(item.low for item in prior)
        prior_returns = [
            (bars[item].close - bars[item - 1].close) / bars[item - 1].close
            for item in range(max(1, index - lookback + 1), index + 1)
            if bars[item - 1].close
        ]
        current_atr = float(atr_values[index] or 0.0)
        current_high_sma = float(sma_high[index] or 0.0)
        current_low_sma = float(sma_low[index] or 0.0)
        previous_high_sma = float(sma_high[index - 1] or current_high_sma) if index > 0 else current_high_sma
        previous_low_sma = float(sma_low[index - 1] or current_low_sma) if index > 0 else current_low_sma
        current_hilo = float(hilo_values[index] or 0.0)
        breakout = float(breakout_level or entry_price)
        opposite_channel = float((dc_lower[index] if direction == 1 else dc_upper[index]) or stop_price)
        stop_distance = abs(entry_price - stop_price)
        gann_state = state_values[index]
        bars_since_flip = index - last_gann_flip_index if last_gann_flip_index is not None else 0
        normalized_gann_distance = ((bar.close - current_hilo) / bar.close) if bar.close and current_hilo else 0.0
        breakout_distance = (bar.close - breakout) if direction == 1 else (breakout - bar.close)
        channel_width = float(dc_upper[index] or bar.high) - float(dc_lower[index] or bar.low)
        recent_cross_count = 0
        for item in range(max(1, index - lookback + 1), index + 1):
            previous = hilo_values[item - 1]
            current = hilo_values[item]
            if previous is None or current is None:
                continue
            crossed_up = bars[item - 1].close <= float(previous) and bars[item].close > float(current)
            crossed_down = bars[item - 1].close >= float(previous) and bars[item].close < float(current)
            if crossed_up or crossed_down:
                recent_cross_count += 1
        return {
            "side": "long" if direction == 1 else "short",
            "weekday": bar.ts.weekday(),
            "utc_hour": bar.ts.hour,
            "month": bar.ts.month,
            "gann_state": gann_state,
            "gann_high_sma": round(current_high_sma, 6),
            "gann_low_sma": round(current_low_sma, 6),
            "gann_high_slope": round(current_high_sma - previous_high_sma, 6),
            "gann_low_slope": round(current_low_sma - previous_low_sma, 6),
            "fast_slope": round(current_high_sma - previous_high_sma, 6),
            "slow_slope": round(current_low_sma - previous_low_sma, 6),
            "hilo_value": round(current_hilo, 6),
            "normalized_ma_distance": round(normalized_gann_distance, 8),
            "bars_since_gann_flip": bars_since_flip,
            "breakout_age_bars": signal_age,
            "donchian_breakout_level": round(breakout, 6),
            "donchian_opposite_level": round(opposite_channel, 6),
            "donchian_channel_width": round(channel_width, 6),
            "donchian_channel_width_pct": round(channel_width / bar.close, 8) if bar.close else 0.0,
            "donchian_breakout_distance": round(breakout_distance, 6),
            "donchian_breakout_distance_atr": round(breakout_distance / current_atr, 6) if current_atr else 0.0,
            "atr": round(current_atr, 6),
            "atr_pct": round(current_atr / bar.close, 8) if bar.close else 0.0,
            "recent_return_20": round((bar.close - prior_close) / prior_close, 8) if prior_close else 0.0,
            "recent_range_20": round((prior_high - prior_low) / bar.close, 8) if bar.close else 0.0,
            "recent_volatility_20": round(math.sqrt(sum(item * item for item in prior_returns) / len(prior_returns)), 8)
            if prior_returns
            else 0.0,
            "recent_cross_count": recent_cross_count,
            "stop_distance": round(stop_distance, 6),
            "stop_distance_atr": round(stop_distance / current_atr, 6) if current_atr else 0.0,
            "stop_distance_pct": round(stop_distance / entry_price, 8) if entry_price else 0.0,
            "time_risk_filter_enabled": bool(parameters.get("time_risk_filter_enabled", False)),
            "blocked_utc_hour_count": len(parameters.get("time_risk_block_utc_hours", [])),
            "is_adjacent_to_blocked_hour": any(
                ((bar.ts.hour - int(hour)) % 24 in (1, 23)) for hour in parameters.get("time_risk_block_utc_hours", [])
            ),
        }

    @staticmethod
    def _open_position(
        direction: int,
        index: int,
        bar: Bar,
        fill: float,
        stop: float,
        quantity: float,
        commission_pct: float,
        equity: float,
        features: dict[str, Any],
    ) -> Position:
        return Position(
            direction=direction,
            entry_index=index,
            entry_ts=bar.ts,
            entry_price=fill,
            stop_price=stop,
            quantity=quantity,
            entry_commission=fill * quantity * commission_pct,
            entry_equity=equity,
            entry_notional=fill * quantity,
            initial_risk_per_unit=abs(fill - stop),
            stop_initialized_on_index=index,
            entry_features=features,
        )

    @staticmethod
    def _position_quantity(parameters: dict[str, Any], equity: float, entry_price: float, stop_price: float) -> float:
        if entry_price <= 0 or equity <= 0:
            return 0.0
        mode = parameters.get("sizing_mode", "fixed_quantity")
        max_leverage = max(0.0, float(parameters.get("max_leverage", 1.0)))
        max_notional = equity * max_leverage if max_leverage else float("inf")
        if mode == "fixed_notional_pct":
            target_pct = max(0.0, float(parameters.get("notional_pct", 1.0)))
            target_notional = min(equity * target_pct, max_notional)
            return target_notional / entry_price
        if mode == "fixed_risk_pct":
            risk_per_unit = abs(entry_price - stop_price)
            if risk_per_unit <= 0:
                return 0.0
            risk_pct = max(0.0, float(parameters.get("risk_pct", 0.005)))
            risk_quantity = (equity * risk_pct) / risk_per_unit
            leverage_quantity = max_notional / entry_price
            return min(risk_quantity, leverage_quantity)
        if mode == "mt5_fixed_risk_lot":
            risk_per_unit = abs(entry_price - stop_price)
            contract_size = max(0.0, float(parameters.get("contract_size", 100.0)))
            lot_step = max(0.0, float(parameters.get("lot_step", 0.01)))
            min_lot = max(0.0, float(parameters.get("min_lot", 0.01)))
            max_lot = max(0.0, float(parameters.get("max_lot", 100.0)))
            if risk_per_unit <= 0 or contract_size <= 0 or lot_step <= 0 or max_lot <= 0:
                return 0.0
            risk_pct = max(0.0, float(parameters.get("risk_pct", 0.005)))
            risk_per_lot = risk_per_unit * contract_size
            risk_lots = (equity * risk_pct) / risk_per_lot
            leverage_lots = max_notional / (entry_price * contract_size)
            raw_lots = min(risk_lots, leverage_lots, max_lot)
            stepped_lots = math.floor(raw_lots / lot_step) * lot_step
            if stepped_lots < min_lot:
                if parameters.get("skip_below_min_lot", True):
                    return 0.0
                stepped_lots = min_lot
            final_lots = min(max_lot, round(stepped_lots, 8))
            return final_lots * contract_size
        return max(0.0, float(parameters.get("quantity", 1.0)))

    @staticmethod
    def _entry_features(
        bars: list[Bar],
        index: int,
        direction: int,
        fast: list[float | None],
        slow: list[float | None],
        atr_values: list[float | None],
        cross_count: int,
        stop_price: float,
        entry_price: float,
    ) -> dict[str, Any]:
        bar = bars[index]
        lookback = min(index, 20)
        prior = bars[index - lookback : index + 1]
        prior_close = bars[index - lookback].close if lookback else bar.close
        prior_high = max(item.high for item in prior)
        prior_low = min(item.low for item in prior)
        prior_returns = [
            (bars[item].close - bars[item - 1].close) / bars[item - 1].close
            for item in range(max(1, index - lookback + 1), index + 1)
            if bars[item - 1].close
        ]
        current_fast = float(fast[index] or 0.0)
        current_slow = float(slow[index] or 0.0)
        previous_fast = float(fast[index - 1] or current_fast)
        previous_slow = float(slow[index - 1] or current_slow)
        current_atr = float(atr_values[index] or 0.0)
        stop_distance = abs(entry_price - stop_price)
        return {
            "side": "long" if direction == 1 else "short",
            "weekday": bar.ts.weekday(),
            "utc_hour": bar.ts.hour,
            "month": bar.ts.month,
            "fast_sma": round(current_fast, 6),
            "slow_sma": round(current_slow, 6),
            "fast_minus_slow": round(current_fast - current_slow, 6),
            "normalized_ma_distance": round((current_fast - current_slow) / bar.close, 8) if bar.close else 0.0,
            "fast_slope": round(current_fast - previous_fast, 6),
            "slow_slope": round(current_slow - previous_slow, 6),
            "atr": round(current_atr, 6),
            "atr_pct": round(current_atr / bar.close, 8) if bar.close else 0.0,
            "recent_return_20": round((bar.close - prior_close) / prior_close, 8) if prior_close else 0.0,
            "recent_range_20": round((prior_high - prior_low) / bar.close, 8) if bar.close else 0.0,
            "recent_volatility_20": round(math.sqrt(sum(item * item for item in prior_returns) / len(prior_returns)), 8)
            if prior_returns
            else 0.0,
            "recent_cross_count": cross_count,
            "stop_distance": round(stop_distance, 6),
            "stop_distance_atr": round(stop_distance / current_atr, 6) if current_atr else 0.0,
            "stop_distance_pct": round(stop_distance / entry_price, 8) if entry_price else 0.0,
        }

    @staticmethod
    def _update_excursion(position: Position, bar: Bar) -> None:
        if position.direction == 1:
            favorable = bar.high - position.entry_price
            adverse = bar.low - position.entry_price
        else:
            favorable = position.entry_price - bar.low
            adverse = position.entry_price - bar.high
        position.max_favorable_excursion = max(position.max_favorable_excursion, favorable)
        position.max_adverse_excursion = min(position.max_adverse_excursion, adverse)

    def _close_trade(
        self,
        position: Position,
        bar: Bar,
        index: int,
        price: float,
        reason: str,
        commission_pct: float,
        equity_before: float,
    ) -> dict[str, Any]:
        exit_commission = price * position.quantity * commission_pct
        if position.direction == 1:
            gross_pnl = (price - position.entry_price) * position.quantity
        else:
            gross_pnl = (position.entry_price - price) * position.quantity
        net_pnl = gross_pnl - position.entry_commission - exit_commission
        initial_risk = position.initial_risk_per_unit
        initial_risk_amount = initial_risk * position.quantity
        return {
            "trade_id": f"tr_{uuid.uuid4().hex[:12]}",
            "direction": "long" if position.direction == 1 else "short",
            "entry_ts": position.entry_ts.isoformat(),
            "exit_ts": bar.ts.isoformat(),
            "entry_price": round(position.entry_price, 4),
            "exit_price": round(price, 4),
            "stop_price": round(position.stop_price, 4),
            "quantity": round(position.quantity, 8),
            "entry_notional": round(position.entry_notional, 2),
            "entry_exposure_pct": round((position.entry_notional / position.entry_equity) * 100, 4)
            if position.entry_equity
            else 0.0,
            "initial_risk_amount": round(initial_risk_amount, 2),
            "initial_risk_pct": round((initial_risk_amount / position.entry_equity) * 100, 4)
            if position.entry_equity
            else 0.0,
            "gross_pnl": round(gross_pnl, 2),
            "net_pnl": round(net_pnl, 2),
            "bars_held": index - position.entry_index,
            "reason": reason,
            "mfe": round(position.max_favorable_excursion * position.quantity, 2),
            "mae": round(position.max_adverse_excursion * position.quantity, 2),
            "mfe_r": round(position.max_favorable_excursion / initial_risk, 4) if initial_risk else 0.0,
            "mae_r": round(position.max_adverse_excursion / initial_risk, 4) if initial_risk else 0.0,
            "return_on_equity_pct": round((net_pnl / equity_before) * 100, 4) if equity_before else 0.0,
            "time_decay_confirmation_suppressed": position.time_decay_confirmation_suppressed,
            "reverse_confirmation_suppressed": position.reverse_confirmation_suppressed,
            "entry_features": position.entry_features,
        }


def apply_patch_to_spec(spec: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(spec)
    path = patch["path"].split(".")
    cursor: dict[str, Any] = result
    for step in path[:-1]:
        next_value = cursor.get(step)
        if not isinstance(next_value, dict):
            next_value = {}
            cursor[step] = next_value
        cursor = next_value
    cursor[path[-1]] = patch["value"]
    return result
