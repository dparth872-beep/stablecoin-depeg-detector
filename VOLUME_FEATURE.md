# Volume Anomaly Detection

Implemented in VolumeTracker class (depeg_detector.py):
- Rolling window (default 20 samples, min 5 or window/2 before alert)
- Uses median for outlier-robust baseline (resistant to temporary spikes)
- Flags when current 24h volume > 3x baseline (configurable multiplier)
- Skips zero/negative volumes
- 300s cooldown (debounce) to prevent alert storms
- Integrated into REST loop, live CLI dashboard, and both WebSocket modes
- Alert includes median, average, sample count for transparency
- Client-side approximation also in dashboard.html via localStorage history

Alert example:
VOLUME SPIKE USDT: $150,000,000 > 3.0x baseline $40,000,000 (med=$38,000,000, avg=$42,000,000, n=15)

Provides independent early-warning tier for liquidity stress before or without price depegs. Verified in unit tests including median robustness and cooldown. Status confirmed 2026-10-23.

# 5-minute volume velocity (v1.8.0)

Separate from the 24h spike above. Implemented in `VolumeVelocityTracker`:

- Compares the current 5-minute quote volume with the median of prior 5-minute bars.
- Alerts when current volume is greater than or equal to `volume_velocity_multiplier` times that median. Default multiplier is 3.
- Does not look at price. A breach alerts while the coin is still inside $0.995–$1.005.
- Needs `volume_velocity_min_samples` prior bars (default 5) so the median exists. Zero and negative volumes are ignored.
- `volume_velocity_window` (default 12) is how many prior bars the median keeps.
- `volume_velocity_cooldown` (default 300 seconds) suppresses repeat alerts. The first breach is not delayed.
- `volume_velocity_bar_seconds` (default 300) is the bar length recorded in the alert text.
- `volume_velocity_enabled` (default true) turns the tier off without touching the 24h tracker.
- Live polls use `observe_bar`: the open 5-minute candle is rechecked in place and committed once, when the next candle opens, so a 30-second poll does not stuff the median with partial copies.
- REST, the CLI dashboard, and both WebSocket modes call it. Bars come from Binance 5-minute klines (quote volume) and, if that pair is missing or the request fails, Coinbase 5-minute candles (base volume times close).
- The browser dashboard still flags 24h volume from CoinGecko locally. It does not invent a 5-minute series from the 24h figure. The velocity alert is the Python path.

Config keys live in `DEFAULT_CONFIG` and `config.json.example`. Unit tests cover the 3x breach with price inside the band, a sub-3x non-event, an exact 3x print, a custom multiplier, short history, cooldown, open-bar dedupe, the disabled switch, and bar seeding.
