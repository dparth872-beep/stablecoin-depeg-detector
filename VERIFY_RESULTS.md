# Price Verification Results

Run on 2026-10-20 ~20:05 UTC against CoinGecko free API (with retry on 429).

```
OK     USDT: $0.9991  vol=$50,817,490,848  24h=-0.014%
OK     USDC: $0.9998  vol=$16,165,048,878  24h=-0.016%
OK     DAI: $1.0000  vol=$253,781,679  24h=-0.018%
OK     FDUSD: $0.9978  vol=$105,625,752  24h=+0.027%
OK     PYUSD: $1.0000  vol=$47,940,445  24h=-0.005%
OK     TUSD: $0.9986  vol=$17,379,239  24h=-0.053%
```

All six stablecoins within $0.99-$1.01 band. Detector REST logic verified operational.
Multi-source fallback (Coinbase) available if CoinGecko rate-limits.
Note: Binance WebSocket may be geo-restricted depending on deployment location (HTTP 451 from certain regions); REST modes remain fully functional.

Unit tests (14/14) also pass locally.
