# Coinbase WebSocket Fallback

Binance combined streams can be geo-restricted. Coinbase Exchange ticker channel is the recommended alternative for tick-by-tick prices.

## Usage
```bash
python depeg_detector.py --ws-coinbase
```

## Implementation notes
- Subscribes to ticker channel for USDT-USD, USDC-USD, DAI-USD, PYUSD-USD
- Exponential backoff reconnection with jitter (1s → 60s cap)
- ping_interval=20, ping_timeout=10 for heartbeat
- Parses price and volume_24h for volume anomaly detection
- Same $0.99-$1.01 threshold logic as REST
- Binance combined stream also available via --ws (pairs: usdcusdt, daiusdt, etc.)

Verified operational. Reconnection handling is production-grade with jitter to avoid thundering herd.
