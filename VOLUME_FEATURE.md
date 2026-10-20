# Volume Anomaly Detection

Implemented in VolumeTracker class:
- Rolling window (default 20 samples)
- Uses median for robust baseline (resistant to outliers)
- Flags when current 24h volume > 3x baseline
- Skips zero/negative volumes
- Requires minimum history (half window) before alerting
- Integrated into REST loop, dashboard, and WebSocket modes

Alert example:
VOLUME SPIKE USDT: $150,000,000 > 3.0x baseline $40,000,000 (med=$38,000,000, avg=$42,000,000, n=15)

This provides early warning of liquidity stress before price depegs.
