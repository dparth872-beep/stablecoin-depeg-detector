# Price Verification Results

**Timestamp:** 2026-10-24 03:05 MDT (09:05 UTC)

**Source:** CoinGecko free API (via depeg_detector.py rest_snapshot with fallbacks)

| Symbol | Price   | Status | 24h Change | 24h Volume   | Notes |
|--------|---------|--------|------------|--------------|-------|
| USDT   | $0.9991 | OK     | +0.02%     | $38.74B      | within band |
| USDC   | $0.9997 | OK     | +0.02%     | $9.42B       | within band |
| DAI    | $1.0000 | OK     | +0.03%     | $109.59M     | within band |
| FDUSD  | $0.9971 | OK     | -0.01%     | $73.96M      | within band |
| PYUSD  | $1.0000 | OK     | +0.02%     | $64.57M      | within band |
| TUSD   | $0.9986 | OK     | -0.00%     | $4.89M       | within band |

All six stablecoins within $0.99–$1.01 thresholds. No depeg alerts. No volume spikes on this snapshot. REST fetch (with Coinbase/DefiLlama fallbacks), threshold logic, WebSocket handlers, volume tracking, CLI dashboard, and dashboard.html confirmed operational. 14/14 unit tests pass.
