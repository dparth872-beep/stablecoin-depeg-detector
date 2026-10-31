# Unit Test Results

Run on 2026-10-31 with `python tests/test_depeg_logic.py`.

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
PASS test_default_band_half_percent
PASS test_half_percent_depeg_down
PASS test_half_percent_depeg_up
PASS test_half_percent_boundaries_ok
PASS test_half_percent_inside_no_alert
PASS test_one_percent_move_now_alerts
PASS test_volume_velocity_spike_price_inside_band
PASS test_volume_velocity_below_threshold
PASS test_volume_velocity_exact_3x
PASS test_volume_velocity_custom_multiplier
PASS test_volume_velocity_zero_and_short_history
PASS test_volume_velocity_cooldown
PASS test_volume_velocity_observe_bar_dedupe
PASS test_volume_velocity_disabled
PASS test_volume_velocity_from_bars_ignores_price
PASS test_dry_run_usdc_097

30/30 tests passed.
```

`python test_depeg.py` prints a deprecation notice and exits 0. It does not re-run the suite.

Covers the previous cases plus the $0.995–$1.005 band, 5-minute volume velocity (including a spike while price is inside the band, exact 3x, a custom multiplier, cooldown, and open-bar dedupe), and the synthetic USDC $0.97 dry-run alert. Synthetic data only; no network calls.
