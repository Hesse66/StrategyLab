# Production Backtest Engine Audit

Mutation Lab is useful as a research and mutation-discovery engine, but the current backtest/optimization stack should not be treated as an institutional production simulator yet. It has several good safeguards already: explicit capital models, fixed-risk sizing, exposure caps, daily portfolio metrics, buy-and-hold comparison, production optimization mode, chronological fold checks, cost-stress checks, production-style next-bar execution defaults, and mark-to-market equity metrics. Those controls are necessary, but they are not sufficient for a Jim Simons / quant-firm standard because the simulator still lacks exchange-order reconciliation and the optimizer can still learn from the same history used for evaluation.

The practical conclusion is direct: pause any claim that a strategy is ready for real capital until the engine has a production execution layer and a Phase 5 exchange feasibility gate. A saved strategy may be a research survivor, production-comparable candidate, or production robustness candidate, but it is not production-ready until it survives forward paper execution with the same decision logic and realistic exchange constraints.

## Current Engine Status

The current engine is production-comparable for bar-level research, not production-complete. It is acceptable for translating strategy ideas, finding whether a rule family has life, comparing parameter sensitivity, and generating mutation hypotheses under stricter assumptions. It is not yet sufficient as the final authority for paper trading or live deployment.

The MA cross/ATR engine now defaults to `execution_model=next_bar_open`. It detects signals on the completed bar and fills the resulting market action at the next bar open with slippage. The older `research_same_close` model remains available only as an explicit diagnostic mode for comparison.

The ASM/Fibonacci engine now defaults to placing a pending order after the setup is ready, then filling on a later executable bar/open or future limit touch. Same-bar exits remain possible only after a pending order was already active before the bar. This is stricter than the first research version, but it is still a bar-level approximation rather than order-book proof.

The equity curve now records mark-to-market equity and realized equity. Daily Sharpe, Sortino, drawdown, and worst-day metrics use the mark-to-market equity field, so open-position adverse movement is no longer hidden from portfolio-period metrics.

The optimizer runs sequential parameter searches on the selected dataset. This is useful for research climbing, but it is not a production validation method by itself because it optimizes and evaluates on the same history. The robustness gate now has three layers: chronological fold checks on the frozen candidate, anchored train/test checks where parameters are selected only on earlier bars and judged on later unseen bars, and execution-cost stress checks. This is production-comparable research evidence, not live proof.

Costs are simplified to commission percentage and slippage ticks. A production-grade futures/perpetual test also needs spread assumptions, maker/taker distinction when relevant, funding, borrow/shorting constraints where relevant, latency/slippage stress, liquidity caps, order-size impact, and exchange rounding.

Sizing is now better than the original fixed-quantity model, but account size must be treated correctly. Initial capital is partly a reporting scale and partly an exchange-feasibility constraint. Return percent, drawdown percent, risk percent, exposure percent, Calmar, daily Sharpe, and daily Sortino should drive strategy comparison. Absolute PnL from a `100000` account should never be used as the main reason to promote a strategy. Account size matters when min order size, contract value, tick size, margin, and risk budget make a trade impossible or distorted.

## Production Backtest Contract

A production-comparable engine must make each decision using only information available at that point in time. A closed-candle strategy may read the completed candle only after it closes. Any market order caused by that candle should fill at the next executable price proxy, normally next bar open plus slippage in bar data, or at the next tick in tick data. Same-bar fills are allowed only for orders that were already resting before that bar.

The simulator must have an order ledger, not just trade rows. It should model intent, order creation, legal rounding, accepted order, fill, partial fill when supported, cancellation, stop placement, stop replacement, breakeven move, time-decay exit, reverse exit, and final reconciliation. Strategy code should produce intended orders; the execution layer should decide whether those orders are legal and how they fill.

The equity curve must include mark-to-market equity, realized equity, margin exposure, and initial-risk exposure. Portfolio-period metrics must come from mark-to-market equity, not only closed trades. Trade-level Sharpe and profit factor can remain diagnostic, but production claims require daily or period portfolio returns.

The simulator must include exchange constraints for the intended venue. For OKX-style perpetual trading this means instrument id, tick size, lot size, contract value, minimum order size, minimum notional, leverage/margin mode, trigger-order rules, reduce-only behavior, funding assumptions, and rounding. A strategy that cannot be converted into legal exchange orders is not deployable even if the backtest is profitable.

The optimizer must separate discovery from proof. Research optimization may use the full selected history to find whether a strategy family has life. Production validation must then use chronological train/test logic: select parameters on past data, freeze them, and evaluate on later unseen windows. Anchored or rolling walk-forward with an embargo is the correct next standard. A candidate that only works after full-sample optimization is a research artifact.

Mutation phases must be constrained by this contract. Phase 3 and Phase 4 mutations should not be promoted because they improve full-history profit. They should survive the executable fill model, mark-to-market metrics, cost stress, train/test splits, and exchange-feasibility audit. Any mutation that depends on future bars, same-close fills, unmodeled stop replacement, or unrealistically perfect execution must be rejected even if headline metrics improve.

## Recommended Next Implementation Block

The next engineering priority is not more strategy mutation. It is a production execution layer and feasibility gate.

Implement the changes in this order:

1. Keep anchored train/test validation mandatory in robustness checks where each fold selects parameters only from the training segment and evaluates only on the later test segment.
2. Keep the saved-run exchange feasibility audit mandatory before paper trading: legal quantity rounding, tick rounding, minimum order size, notional exposure, stop trigger mapping, breakeven stop replacement, and margin sanity.
3. Add cost/funding scenarios beyond the current fee/slippage stresses: funding stress for perpetuals, spread stress, and liquidity/impact caps.
4. Add Phase 5 to the workflow: TradingView/OKX Signal Bot can be Phase 5-lite for alert executability, but Phase 5-full should be a native runner that uses the same Python strategy state against closed live candles and reconciles intended orders against exchange responses.

## Routing Rule

Until the production execution layer exists, treat current Mutation Lab results as research evidence. A result that passes current production gates and robustness checks can be called a production robustness candidate only in the research sense: it deserves execution-feasibility work and paper trading preparation, not real capital.

Do not discard the whole app. The translation, mutation, report, and optimization workflow is valuable. The correction is to stop using the current backtest as the final truth and make the next layer explicitly executable.
