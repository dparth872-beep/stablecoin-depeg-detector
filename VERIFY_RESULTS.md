# Price Verification — 2026-10-25 ~11:04 MDT

CoinGecko free API returned 429 rate limit. Used DefiLlama + Coinbase fallbacks (as implemented in depeg_detector.py and dashboard.html):

| Coin   | Price (DefiLlama) | Coinbase Spot | Status |
|--------|-------------------|---------------|--------|
| USDT   | $0.9990           | $0.9987       | OK     |
| USDC   | $0.9995           | $1.0000       | OK     |
| DAI    | $1.0002           | $1.0001       | OK     |
| FDUSD  | $0.9972           | n/a           | OK     |
| PYUSD  | $1.0001           | $1.0000       | OK     |
| TUSD   | $0.9987           | n/a           | OK     |

All six coins inside $0.99–$1.01 band. No depegs. No volume spikes detected. Divergence well under 50 bps.

Dashboard resilience keeps last good data on rate limits. 14/14 unit tests pass.
