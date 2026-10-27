# Price Verification — 2026-10-27 ~06:06 MDT

CoinGecko free API returned 429 (rate limit) on this check. Fallback sources healthy:

**DefiLlama (coingecko: ids):**

| Coin   | Price     | Status |
|--------|-----------|--------|
| USDT   | $0.998579 | OK     |
| USDC   | $0.999259 | OK     |
| DAI    | $0.999767 | OK     |
| FDUSD  | $0.996816 | OK     |
| PYUSD  | $0.999730 | OK     |
| TUSD   | $0.998450 | OK     |

**Coinbase spot (subset):** USDT $0.998195, USDC $1.000000, DAI $0.999076, PYUSD $1.000000. All within band.

All six coins inside $0.99–$1.01 band. No depegs. No volume spikes on this snapshot.

Dashboard v3.48 and depeg_detector.py both operational (fallbacks active). 14/14 unit tests pass. Primary client surface remains dashboard.html — zero-code, browser-based, rate-limit resilient.
