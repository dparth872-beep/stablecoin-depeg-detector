# Price Verification — 2026-10-25 ~14:03 MDT

CoinGecko free API responding normally (no rate limit):

| Coin   | Price     | 24h Vol       | 24h Change | Status |
|--------|-----------|---------------|------------|--------|
| USDT   | $0.998989 | $23.6B        | -0.02%     | OK     |
| USDC   | $0.999606 | $4.86B        | -0.00%     | OK     |
| DAI    | $0.999978 | $41.4M        | -0.03%     | OK     |
| FDUSD  | $0.997042 | $56.5M        | -0.01%     | OK     |
| PYUSD  | $1.000000 | $8.23M        | -0.02%     | OK     |
| TUSD   | $0.999149 | $2.21M        | +0.03%     | OK     |

All six coins inside $0.99–$1.01 band. No depegs. No volume spikes. Divergence checks available via Coinbase fallback in dashboard and detector.

Dashboard (v3.30) and depeg_detector.py both operational. 14/14 unit tests pass. Primary client surface remains dashboard.html — zero-code, browser-based.
