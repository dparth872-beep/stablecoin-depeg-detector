# CLI Dashboard

Live one-line-per-coin status board that refreshes in place.

## Usage
```bash
python depeg_detector.py --dashboard
```

## Features
- Clears screen (\033[2J\033[H) and redraws every poll_interval (default 30s)
- Columns: Symbol, Price, 24h%, 24h Volume, Status
- ANSI colors: green OK, red DEPEG, yellow NO DATA / volume spikes
- Timestamp in UTC
- Integrates VolumeTracker for live spike alerts printed above the board
- Thresholds and exit instructions displayed at bottom
- Ctrl+C to exit cleanly

Verified operational against live multi-source REST prices. Provides at-a-glance monitoring for desks without needing external dashboards.
