# CLI Dashboard

Live status board that refreshes in place (ANSI clear screen).

Columns: Symbol | Price | 24h% | 24h Volume | Status (colored: green OK / red DEPEG / yellow NO DATA)

Volume spike detection runs in the background; alerts appear in console when thresholds hit.

Run with:
```
python depeg_detector.py --dashboard
```

Refreshes every poll_interval_seconds (default 30s). Shows timestamp, thresholds, and Ctrl+C exit.

Example output:
```
Stablecoin Depeg Detector  |  Live Dashboard  |  2026-10-20 17:05:00 UTC
------------------------------------------------------------------------------
Symbol       Price     24h%      24h Volume Status
------------------------------------------------------------------------------
USDT      $0.9992   -0.01%  $51,420,246,699 OK
USDC      $0.9998   -0.01%  $16,621,227,981 OK
... 
```
