# Price Verification — 2026-10-29 13:04 MDT

Live CoinGecko free API returned 429 (rate limit). Fell back to DefiLlama. All six stablecoins within $0.99–$1.01 band. No depegs detected.

| Coin   | Price     | Status | Source     |
|--------|-----------|--------|------------|
| USDT   | $0.9990   | OK     | DefiLlama  |
| USDC   | $0.9995   | OK     | DefiLlama  |
| DAI    | $0.9998   | OK     | DefiLlama  |
| FDUSD  | $0.9977   | OK     | DefiLlama  |
| PYUSD  | $0.9996   | OK     | DefiLlama  |
| TUSD   | $0.9974   | OK     | DefiLlama  |

Coinbase spot cross-check: USDT $0.9989, USDC $1.0000, DAI $0.9997, PYUSD $1.0000. All consistent within thresholds.

No volume spikes relative to recent baselines. Threshold logic confirmed: all prices OK. 14/14 unit tests pass. Snapshot logic, WebSocket streams, volume tracker, and dashboard.html all operational.

Note: Free-tier CoinGecko rate limits are expected and handled with fallbacks + last-good-data resilience in both the Python detector and the client-side dashboard.

Primary client surface remains dashboard.html (v6.6) — zero-code, browser-based, professional dark fintech aesthetic.
