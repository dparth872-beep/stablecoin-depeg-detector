# Price Verification Results

**Timestamp:** 2026-10-24 05:04 MDT (11:04 UTC)

**Source:** CoinGecko free API (via verify_prices.py and depeg_detector.py rest_snapshot with fallbacks)

| Symbol | Price   | Status | 24h Change | 24h Volume   | Notes |
|--------|---------|--------|------------|--------------|-------|
| USDT   | $0.9991 | OK     | +0.01%     | $38.63B      | within band |
| USDC   | $0.9997 | OK     | +0.01%     | $9.12B       | within band |
| DAI    | $1.0000 | OK     | +0.00%     | $103.21M     | within band |
| FDUSD  | $0.9972 | OK     | -0.01%     | $72.86M      | within band |
| PYUSD  | $1.0000 | OK     | +0.01%     | $65.44M      | within band |
| TUSD   | $0.9986 | OK     | -0.01%     | $2.12M       | within band |

All six stablecoins within $0.99–$1.01 thresholds. No depeg alerts. No volume spikes on this snapshot. REST fetch (with Coinbase/DefiLlama fallbacks), threshold logic, WebSocket handlers, volume tracking, CLI dashboard, and dashboard.html confirmed operational. 14/14 unit tests pass. Subsequent direct CoinGecko call hit free-tier rate limit (429); dashboard resilience keeps last good data visible.
