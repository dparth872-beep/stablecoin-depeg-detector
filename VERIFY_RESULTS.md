# Price Verification — 2026-10-25 ~18:05 MDT

CoinGecko free API responding normally (no rate limit):

| Coin   | Price     | 24h Vol       | 24h Change | Status |
|--------|-----------|---------------|------------|--------|
| USDT   | $0.999102 | $33.7B        | +0.01%     | OK     |
| USDC   | $0.999607 | $6.55B        | -0.01%     | OK     |
| DAI    | $1.000000 | $48.3M        | +0.00%     | OK     |
| FDUSD  | $0.997003 | $87.7M        | -0.01%     | OK     |
| PYUSD  | $1.000000 | $8.79M        | +0.00%     | OK     |
| TUSD   | $0.999056 | $6.82M        | +0.04%     | OK     |

All six coins inside $0.99–$1.01 band. No depegs. No volume spikes. Divergence checks available via Coinbase fallback in dashboard and detector.

Dashboard (v3.34) and depeg_detector.py both operational. 14/14 unit tests pass. Primary client surface remains dashboard.html — zero-code, browser-based.
