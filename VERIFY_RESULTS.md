# Price Verification — 2026-10-27 ~15:04 MDT

CoinGecko free API returned 429 (rate limit) on this check. Used DefiLlama primary + Coinbase spot for cross-check.

| Coin   | Price     | Status | Source     |
|--------|-----------|--------|------------|
| USDT   | $0.9988   | OK     | DefiLlama  |
| USDC   | $0.9995   | OK     | DefiLlama  |
| DAI    | $0.9997   | OK     | DefiLlama  |
| FDUSD  | $0.9972   | OK     | DefiLlama  |
| PYUSD  | $0.9999   | OK     | DefiLlama  |
| TUSD   | $0.9977   | OK     | DefiLlama  |

Coinbase spot cross-check: USDT $0.9986, USDC $1.0000, DAI $0.9999. All within band. No depegs.

Dashboard v3.48 and depeg_detector.py both operational. Primary client surface remains dashboard.html — zero-code, browser-based, rate-limit resilient with last-good-data fallback.
