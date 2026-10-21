# CLI Dashboard

Live one-line-per-coin status board that refreshes in place.

## Usage
```bash
python depeg_detector.py --dashboard
```

## Features
- Clears screen and redraws every poll_interval (default 30s)
- Columns: Symbol, Price, 24h%, 24h Volume, Status
- ANSI colors: green OK, red DEPEG, yellow NO DATA / volume spikes
- Timestamp in UTC
- Integrates VolumeTracker for live spike alerts
- Thresholds displayed at bottom
- Ctrl+C to exit cleanly

Verified operational: run_dashboard function uses rest_snapshot + VolumeTracker + ANSI control codes.
