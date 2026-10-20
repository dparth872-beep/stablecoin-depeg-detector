# Price Verification Results

Run on 2026-10-20 ~18:03 UTC against CoinGecko free API (with Coinbase fallback ready).

```
OK     USDT: $0.9993  vol=$51,205,225,019  24h=-0.00%
OK     USDC: $0.9998  vol=$16,362,494,735  24h=-0.01%
OK     DAI: $1.0000  vol=$282,362,551  24h=-0.02%
OK     FDUSD: $0.9980  vol=$105,195,441  24h=+0.05%
OK     PYUSD: $1.0000  vol=$39,301,941  24h=+0.02%
OK     TUSD: $0.9989  vol=$14,538,734  24h=-0.02%
```

All six stablecoins within $0.99-$1.01 band. Detector REST logic verified operational.
Multi-source fallback (Coinbase) available if CoinGecko rate-limits.
Note: Binance WebSocket may be geo-restricted depending on deployment location (HTTP 451 from certain regions); REST modes remain fully functional.
