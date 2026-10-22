# Unit Test Results

Run on 2026-10-21 by builder agent. Confirmed still passing.

```
PASS test_clean_prices_no_alerts
PASS test_depeg_down
PASS test_depeg_up
PASS test_missing_data
PASS test_boundary_lower
PASS test_boundary_upper
PASS test_volume_spike
PASS test_volume_no_spike
PASS test_volume_zero_skipped
PASS test_volume_median_robust
PASS test_volume_cooldown
PASS test_divergence
PASS test_divergence_within_band
PASS test_multi_coin_depeg

All 14 tests passed.
```

Covers:
- Clean prices within 0.99-1.01 produce no alerts
- Down and up depegs correctly flagged
- Missing data handled
- Exact boundary values accepted as OK
- Volume spikes (3x median), no-spikes, zero-skipping, median robustness, cooldown
- Cross-source divergence above/below 50 bps
- Multi-coin simultaneous alerts

Synthetic data only; no network calls. Ready for CI.
