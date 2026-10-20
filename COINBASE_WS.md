# Coinbase WebSocket Support

Binance combined stream may return HTTP 451 in some regions.

Use Coinbase Exchange public WebSocket as fallback:

```bash
python depeg_detector.py --ws-coinbase
```

- Endpoint: wss://ws-feed.exchange.coinbase.com
- Channel: ticker
- Pairs: USDT-USD, USDC-USD, DAI-USD, PYUSD-USD
- Same reconnection logic (exponential backoff + jitter, stale detection)
- FDUSD and TUSD fall back to REST or Binance where available

This provides tick-by-tick prices without geo-blocks for most deployments.
