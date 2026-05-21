# Production Backtest Engine

Mutation Lab should be treated as a strategy research and execution-simulation system, not as a charting toy that happens to calculate PnL. The central rule is simple: a strategy is only useful if the backtest can be translated into forward orders under realistic execution constraints. If a result depends on same-close fills, current-bar hindsight, impossible position sizes, unmodeled stop replacement, or full-sample overfitting, then the result is not alpha. It is a simulator artifact.

The current direction of the engine is therefore MetaTrader-style bar execution first. This does not mean the engine is a full MetaTrader terminal, and it does not mean bar data can reproduce tick-level execution perfectly. It means Mutation Lab should prefer the most realistic deterministic bar proxy we have: completed-bar signals, next executable fills, same-entry-bar protective stop eligibility when the model explicitly says the order would be live, broker-style stop-modification rejection, mark-to-market equity, explicit costs, and exchange-feasibility constraints before any paper-trading claim.

## Canonical Execution Model

The canonical production-comparable execution model is `mt5_bar_proxy`. It exists because the older research model was too generous: it could let a strategy detect a signal and behave as if execution happened under cleaner conditions than a real order path would allow. In contrast, `mt5_bar_proxy` treats signal formation and execution as separate states. A completed bar may create intent, the next executable price proxy fills the order, and protective logic is evaluated according to whether a real broker-style position and stop would already exist.

Diagnostic execution models remain internal regression tools. They are not operator-facing mutation levers. The app should present `mt5_bar_proxy` as the execution contract for strategy research, optimization, robustness review, and paper-trading routing. If a comparison needs `research_same_close` or `next_bar_open`, run it deliberately in code or a diagnostic script and label it as non-promotional evidence.

## Current Engine Coverage

The MA cross / ATR stop engine uses `mt5_bar_proxy` as its operator-facing execution path. Under the MT5 proxy it uses completed-bar signals, pending next-open entries, same-entry-bar stop eligibility, breakeven stop movement with invalid-modification rejection, time-decay exits, reverse-exit confirmation, exposure caps, broker-lot fixed-risk sizing, and mark-to-market equity. This is the most mature execution path in the app and should be the reference behavior when hardening other engines.

The Gann HiLo / Donchian breakout fork has been merged as `ghl_dc_breakout_v1`, not as a wholesale replacement of the existing app. That was deliberate. The fork adds useful execution and sizing concepts, but Mutation Lab already has multiple strategy families that should not be deleted just to import one stronger engine. The correct integration pattern is explicit: each strategy family declares an `engine_id`, and the backtest router maps that id to a deterministic engine implementation with tests for signal formation, fills, exits, diagnostics, and artifacts.

The ASM/Fibonacci and BOS pullback engines now accept the MT5 execution model as a first-class mode. They still need deeper parity work before being treated as mature as the MA path, because their setups involve pending limit-style orders, context bars, structural confirmation, and ambiguous OHLC ordering. The important rule is that these engines must not silently fall back into same-bar fantasy execution. If an order was not already live before a bar, the engine cannot use that bar's full high/low path to pretend it knew both signal and fill sequence.

## Sizing And Broker Feasibility

Production-comparable strategy evaluation uses the broker-aware `mt5_fixed_risk_lot` model. Fixed quantity, fixed notional, and non-lot fixed-risk sizing are diagnostic internals only; they should not appear as normal mutation levers because they let the operator accidentally compare strategies under old capital assumptions.

`mt5_fixed_risk_lot` converts a risk budget into broker-style lots through `contract_size`, `min_lot`, `lot_step`, `max_lot`, and `skip_below_min_lot`. This matters because small accounts and wide stops can produce theoretical quantities that no broker or exchange will accept. The engine must report invalid-lot skips instead of pretending those trades were executable. A strategy that performs only because impossible micro-positions are allowed is not deployable.

Initial capital is not just a cosmetic reporting value. In percentage-based research, it mainly scales absolute PnL, but in execution research it controls whether minimum order size, contract value, margin, and risk budget make a trade legal. This is why a production report should emphasize return percent, drawdown percent, daily Sharpe, daily Sortino, Calmar, risk percent, exposure percent, and feasibility diagnostics rather than headline currency PnL.

## Metrics That Matter

The engine must measure portfolio-period behavior, not only closed-trade behavior. Trade-level profit factor and trade-level Sharpe are useful diagnostics, but production claims require mark-to-market daily or periodic returns. Open adverse movement must be visible while a trade is still alive. Otherwise the strategy can look smooth simply because unrealized drawdown is hidden until the position closes.

The minimum production dashboard should include net return, max drawdown, daily Sharpe, daily Sortino, worst daily return, Calmar, trade count, win rate, profit factor, average exposure, max exposure, average initial risk, max initial risk, buy-and-hold return, buy-and-hold drawdown, and Calmar delta versus buy-and-hold. A strategy does not have to beat buy-and-hold in raw return for every asset, but if it underperforms raw passive exposure, it must justify itself through substantially better risk efficiency, lower drawdown, smoother equity, or complementary regime behavior.

Drawdown is account-level peak-to-trough equity loss, not per-trade loss. Risk percent is the intended loss budget to the initial stop for a single trade before slippage and gap effects. Exposure percent is not the same as risk percent: a trade can use 100% notional exposure while risking 0.5% to a stop if the stop is close, but that still creates liquidation, margin, and gap-risk questions. Quant-style evaluation must show both.

## Optimization Rules

Optimization is discovery, not proof. Research optimization may search broadly to determine whether a family has life. Production optimization must be stricter: it should reject candidates that violate production sizing, minimum trade evidence, exposure caps, risk caps, execution model requirements, or robustness gates. It must not fall back to a high-scoring diagnostic candidate when no production-eligible candidate exists.

The optimizer should prefer enough trades, stable drawdown, robust return, daily risk-adjusted performance, and survival under costs over raw profit factor. A tiny-sample candidate with a beautiful profit factor is usually noise. The app already penalizes or rejects insufficient trade evidence; that principle must remain non-negotiable as new engines are added.

A saved candidate should pass anchored train/test or walk-forward logic before being described as robust. Full-history optimization can find a promising configuration, but it cannot validate it. A robust candidate must show that parameters selected on earlier data continue to behave acceptably on later unseen windows. If the strategy only works when the optimizer can see the entire historical period, it is overfit.

## Required Hardening Gates

Before paper trading, every serious candidate should pass these gates:

1. The strategy runs under `mt5_bar_proxy` or a stricter execution model.
2. The strategy uses `mt5_fixed_risk_lot` sizing with explicit risk budget, broker lot constraints, max exposure, and max leverage.
3. The report includes mark-to-market daily metrics, drawdown, exposure, risk, buy-and-hold comparison, side decomposition, exit decomposition, and period decomposition.
4. The candidate passes cost stress, including increased commission and slippage. Futures/perpetual strategies should later add funding and spread stress.
5. The candidate passes chronological robustness, either walk-forward or anchored train/test validation.
6. The candidate passes exchange feasibility: legal quantity rounding, tick rounding, minimum order size, minimum notional, stop trigger mapping, reduce-only behavior, and margin sanity.
7. Only after those gates should the strategy move to paper trading, where real order acknowledgements, fills, rejections, stop updates, and reconciliation can be measured.

## Phase-Flow Implications

Phase 1 and Phase 2 can still translate and baseline strategies quickly, but they must not promote a baseline because it looks good under a loose execution model. Phase 2 should produce both research evidence and production-comparable evidence. If a baseline cannot survive realistic execution after optimization, it should go to the graveyard or return to translation rather than be rescued with premature complex mutations.

Phase 3 and Phase 4 mutations must be judged under the same execution contract as the parent. A white-box or hybrid mutation that improves profit only by exploiting unrealistic fills is not an improvement. Mutation reports should explicitly state whether the candidate preserved the production execution model, production sizing mode, trade evidence, drawdown constraints, and robustness gates.

Phase 5 is the missing operational gate. TradingView or signal-bot tests can be useful as low-friction signal visibility checks, but the serious path is a native runner that uses the same Python strategy state on closed live candles, sends legal exchange orders, and reconciles intended state against broker or exchange responses. Backtesting answers whether a rule family deserves forward testing. Paper trading answers whether the executable implementation survives reality.

## Development Rule

New engines must not be added as vague strategy scripts. A new engine must declare its `engine_id`, supported execution models, sizing assumptions, warmup logic, signal timing, order timing, stop timing, diagnostics, and tests. If the engine cannot explain when information becomes available and when an order becomes executable, it is not ready for Mutation Lab.

The fork integration establishes the current priority: preserve existing useful families, but make the MetaTrader-style execution path the default standard. The system should become stricter over time, not more permissive. Better backtests are often less flattering at first, but they are more valuable because they reduce the distance between research results and paper-trading reality.
