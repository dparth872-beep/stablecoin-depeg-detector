# Volume Anomaly Detection

Implemented in VolumeTracker class (depeg_detector.py):
- Rolling window (default 20 samples, min 5 or window/2 before alert)
- Uses median for outlier-robust baseline (resistant to temporary spikes)
- Flags when current 24h volume > 3x baseline (configurable multiplier)
- Skips zero/negative volumes
- 300s cooldown (debounce) to prevent alert storms
- Integrated into REST loop, live dashboard, and both WebSocket modes
- Alert includes median, average, sample count for transparency

Alert example:
VOLUME SPIKE USDT: $150,000,000 > 3.0x baseline $40,000,000 (med=$38,000,000, avg=$42,000,000, n=15)

Provides independent early-warning tier for liquidity stress before or without price depegs. Verified in 14 unit tests including median robustness and cooldown. Live-verified against current CoinGecko 24h volumes.
