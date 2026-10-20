# Price Verification Results

Run on 2026-10-20 ~19:03 UTC against CoinGecko free API.

```
OK     USDT: $0.9992  vol=$50,794,557,898  24h=-0.01%
OK     USDC: $0.9998  vol=$16,169,326,494  24h=-0.01%
OK     DAI: $1.0000  vol=$265,011,840  24h=-0.03%
OK     FDUSD: $0.9978  vol=$105,890,637  24h=+0.03%
OK     PYUSD: $1.0000  vol=$44,667,130  24h=+0.02%
OK     TUSD: $0.9986  vol=$17,501,124  24h=-0.03%
```

All six stablecoins within $0.99-$1.01 band. Detector REST logic verified operational.
Multi-source fallback (Coinbase) available if CoinGecko rate-limits.
Note: Binance WebSocket may be geo-restricted depending on deployment location (HTTP 451 from certain regions); REST modes remain fully functional.
