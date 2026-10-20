# Price Verification Results

Run on 2026-10-20 ~22:03 UTC against CoinGecko free API (with retry on 429).

```
OK     USDT: $0.9992  (within band) [CoinGecko] vol=$51,550,796,041 24h=+0.00%
OK     USDC: $0.9997  (within band) [CoinGecko] vol=$15,769,926,258 24h=-0.01%
OK     DAI: $1.0000  (within band) [CoinGecko] vol=$211,135,680 24h=-0.00%
OK     FDUSD: $0.9981  (within band) [CoinGecko] vol=$108,386,256 24h=+0.06%
OK     PYUSD: $1.0000  (within band) [CoinGecko] vol=$47,498,881 24h=+0.01%
OK     TUSD: $0.9988  (within band) [CoinGecko] vol=$14,258,652 24h=-0.02%
```

All six stablecoins within $0.99-$1.01 band. Detector REST logic verified operational.
Multi-source fallback (Coinbase) available if CoinGecko rate-limits.
Note: Binance WebSocket may be geo-restricted depending on deployment location; REST and Coinbase WS modes remain fully functional.

Unit tests (14/14) also pass locally.
