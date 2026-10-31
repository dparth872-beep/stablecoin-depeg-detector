# Price Verification — 2026-10-30 17:05 MDT

Historical snapshot. Scored that day against the $0.99–$1.01 band. As of v1.8.0 the alert band is $0.995–$1.005. Every price in the table below is also inside that tighter band.

Live snapshot via CoinGecko free API. All six stablecoins within $0.99–$1.01 band. No depegs detected.

| Coin   | Price     | Status | Notes                  |
|--------|-----------|--------|------------------------|
| USDT   | $0.99911  | OK     | CoinGecko              |
| USDC   | $0.999787 | OK     | CoinGecko              |
| DAI    | $1.0000   | OK     | CoinGecko              |
| FDUSD  | $0.997251 | OK     | CoinGecko              |
| PYUSD  | $1.0000   | OK     | CoinGecko              |
| TUSD   | $0.997797 | OK     | CoinGecko              |

No volume spikes on this snapshot (requires history). Threshold logic confirmed against live data. 14/14 unit tests pass. Snapshot logic, WebSocket streams (Binance + Coinbase with exponential-backoff reconnection), volume tracker, CLI dashboard, and professional dashboard.html (v1.7) all operational.

Note: Free-tier CoinGecko rate limits (~5 calls/min shared) are expected and handled with fallbacks + last-good-data resilience in both the Python detector and the client-side dashboard.

Primary client surface remains dashboard.html — zero-code, browser-based, professional dark fintech aesthetic (Bloomberg-meets-Apple), mobile-responsive, auto-refresh every 30s.
