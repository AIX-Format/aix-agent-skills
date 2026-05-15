# Skill: Aggressive Scalper

## Purpose

Executes aggressive scalping trades on crypto markets using RSI extremes (oversold/overbought) with 2:1 reward-to-risk ratio. Built for AlphaAxiom Money Machine.

## Constitutional Alignment

- **Serve Humanity**: Scalping provides liquidity to markets
- **Risk Accountability**: Max 2% per trade, strict stop-losses
- **No Deception**: All trading logic is deterministic and auditable

## Operational Flow

1. Agent receives market data (OHLCV) for a symbol
2. Analyzes RSI: <30 oversold (BUY), >70 overbought (SELL)
3. Confirms with volume > 20-day average
4. Calculates position size: 2% of portfolio max
5. Sets Stop Loss: 1% below entry, Take Profit: 2% above entry
6. Executes via CCXT exchange adapter
7. Logs trade to TrustChain

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Insufficient balance | Portfolio check | HOLD, log warning |
| Exchange API down | Timeout or error | Retry, then escalate |
| Invalid signal | RSI out of range | Skip, wait for next interval |
