#!/usr/bin/env python3
"""Unit tests for threshold logic using synthetic price data."""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from depeg_detector import (
    DEFAULT_CONFIG,
    DRY_RUN_MARKER,
    VolumeTracker,
    VolumeVelocityTracker,
    check_divergence,
    check_price_depeg,
    format_dry_run_alerts,
    velocity_alerts_for_symbol,
)


def test_clean_prices_no_alerts():
    prices = {
        "tether": {"usd": 1.0001, "usd_24h_change": 0.01},
        "usd-coin": {"usd": 0.9998, "usd_24h_change": -0.02},
        "dai": {"usd": 1.0003, "usd_24h_change": 0.03},
    }
    symbol_map = {"tether": "USDT", "usd-coin": "USDC", "dai": "DAI"}
    alerts = check_price_depeg(prices, symbol_map, 0.99, 1.01)
    assert alerts == [], f"Expected no alerts, got {alerts}"
    print("PASS test_clean_prices_no_alerts")


def test_depeg_down():
    prices = {"tether": {"usd": 0.985, "usd_24h_change": -1.5}}
    symbol_map = {"tether": "USDT"}
    alerts = check_price_depeg(prices, symbol_map, 0.99, 1.01)
    assert len(alerts) == 1 and "DEPEG DOWN" in alerts[0]
    assert "USDT" in alerts[0] and "0.9850" in alerts[0]
    print("PASS test_depeg_down")


def test_depeg_up():
    prices = {"dai": {"usd": 1.015, "usd_24h_change": 1.5}}
    symbol_map = {"dai": "DAI"}
    alerts = check_price_depeg(prices, symbol_map, 0.99, 1.01)
    assert len(alerts) == 1 and "DEPEG UP" in alerts[0]
    print("PASS test_depeg_up")


def test_missing_data():
    prices = {"tether": {}}
    symbol_map = {"tether": "USDT"}
    alerts = check_price_depeg(prices, symbol_map, 0.99, 1.01)
    assert len(alerts) == 1 and "NO DATA" in alerts[0]
    print("PASS test_missing_data")


def test_boundary_lower():
    prices = {"tether": {"usd": 0.99}}
    symbol_map = {"tether": "USDT"}
    alerts = check_price_depeg(prices, symbol_map, 0.99, 1.01)
    assert alerts == [], "Exactly lower bound should be OK"
    print("PASS test_boundary_lower")


def test_boundary_upper():
    prices = {"dai": {"usd": 1.01}}
    symbol_map = {"dai": "DAI"}
    alerts = check_price_depeg(prices, symbol_map, 0.99, 1.01)
    assert alerts == [], "Exactly upper bound should be OK"
    print("PASS test_boundary_upper")


def test_volume_spike():
    vt = VolumeTracker(window=10, multiplier=3.0)
    # build baseline
    for v in [100, 110, 105, 95, 100, 102, 98, 101, 103, 99]:
        vt.update("USDT", v)
    alert = vt.update("USDT", 400)  # 4x median
    assert alert is not None and "VOLUME SPIKE" in alert
    print("PASS test_volume_spike")


def test_volume_no_spike():
    vt = VolumeTracker(window=10, multiplier=3.0)
    for v in [100, 110, 105, 95, 100, 102, 98, 101, 103, 99]:
        vt.update("USDT", v)
    alert = vt.update("USDT", 150)  # ~1.5x
    assert alert is None
    print("PASS test_volume_no_spike")


def test_volume_zero_skipped():
    vt = VolumeTracker(window=10, multiplier=3.0)
    for v in [100, 110, 105, 95, 100]:
        vt.update("USDT", v)
    alert = vt.update("USDT", 0)
    assert alert is None
    alert2 = vt.update("USDT", -10)
    assert alert2 is None
    print("PASS test_volume_zero_skipped")


def test_volume_median_robust():
    vt = VolumeTracker(window=10, multiplier=3.0)
    # baseline with outlier - median ignores 1000
    for v in [100, 105, 98, 102, 1000, 99, 101, 97, 103, 100]:
        vt.update("USDC", v)
    # median ~101, 350 > 3*101
    alert = vt.update("USDC", 350)
    assert alert is not None and "VOLUME SPIKE" in alert
    print("PASS test_volume_median_robust")


def test_volume_cooldown():
    vt = VolumeTracker(window=10, multiplier=3.0, cooldown=1)
    for v in [100, 110, 105, 95, 100, 102, 98, 101, 103, 99]:
        vt.update("USDT", v)
    alert1 = vt.update("USDT", 400)
    assert alert1 is not None
    alert2 = vt.update("USDT", 450)  # within cooldown
    assert alert2 is None
    time.sleep(1.1)
    alert3 = vt.update("USDT", 500)
    assert alert3 is not None
    print("PASS test_volume_cooldown")


def test_divergence():
    a = {"tether": {"usd": 1.0000}}
    b = {"tether": {"usd": 0.9940}}
    symbol_map = {"tether": "USDT"}
    alerts = check_divergence(a, b, symbol_map, threshold_bps=50)
    assert len(alerts) == 1 and "DIVERGENCE" in alerts[0]
    print("PASS test_divergence")


def test_divergence_within_band():
    a = {"tether": {"usd": 1.0000}}
    b = {"tether": {"usd": 0.9960}}
    symbol_map = {"tether": "USDT"}
    alerts = check_divergence(a, b, symbol_map, threshold_bps=50)
    assert alerts == []
    print("PASS test_divergence_within_band")


def test_multi_coin_depeg():
    prices = {
        "tether": {"usd": 0.98},
        "usd-coin": {"usd": 1.02},
        "dai": {"usd": 1.00},
    }
    symbol_map = {"tether": "USDT", "usd-coin": "USDC", "dai": "DAI"}
    alerts = check_price_depeg(prices, symbol_map, 0.99, 1.01)
    assert len(alerts) == 2
    print("PASS test_multi_coin_depeg")


def test_default_band_half_percent():
    assert DEFAULT_CONFIG["lower_bound"] == 0.995
    assert DEFAULT_CONFIG["upper_bound"] == 1.005
    assert DEFAULT_CONFIG["volume_velocity_multiplier"] == 3.0
    assert DEFAULT_CONFIG["volume_velocity_bar_seconds"] == 300
    assert DEFAULT_CONFIG["volume_velocity_enabled"] is True
    print("PASS test_default_band_half_percent")


def test_half_percent_depeg_down():
    prices = {"tether": {"usd": 0.994}}
    alerts = check_price_depeg(prices, {"tether": "USDT"}, 0.995, 1.005)
    assert len(alerts) == 1 and "DEPEG DOWN" in alerts[0] and "0.9940" in alerts[0]
    print("PASS test_half_percent_depeg_down")


def test_half_percent_depeg_up():
    prices = {"dai": {"usd": 1.006}}
    alerts = check_price_depeg(prices, {"dai": "DAI"}, 0.995, 1.005)
    assert len(alerts) == 1 and "DEPEG UP" in alerts[0] and "1.0060" in alerts[0]
    print("PASS test_half_percent_depeg_up")


def test_half_percent_boundaries_ok():
    symbol_map = {"tether": "USDT", "dai": "DAI"}
    prices = {"tether": {"usd": 0.995}, "dai": {"usd": 1.005}}
    alerts = check_price_depeg(prices, symbol_map, 0.995, 1.005)
    assert alerts == []
    print("PASS test_half_percent_boundaries_ok")


def test_half_percent_inside_no_alert():
    prices = {"tether": {"usd": 0.996}, "dai": {"usd": 1.004}}
    alerts = check_price_depeg(prices, {"tether": "USDT", "dai": "DAI"}, 0.995, 1.005)
    assert alerts == []
    print("PASS test_half_percent_inside_no_alert")


def test_one_percent_move_now_alerts():
    # $0.99 was inside the old 1% band and is outside the 0.5% band.
    alerts = check_price_depeg({"tether": {"usd": 0.99}}, {"tether": "USDT"}, 0.995, 1.005)
    assert len(alerts) == 1 and "DEPEG DOWN" in alerts[0]
    print("PASS test_one_percent_move_now_alerts")


def _velocity_with_baseline(multiplier=3.0, cooldown=300):
    vt = VolumeVelocityTracker(window=12, multiplier=multiplier, min_samples=5, cooldown=cooldown, bar_seconds=300)
    for vol in (100, 110, 90, 100, 100):
        assert vt.update("USDC", vol, now=1_000) is None
    return vt


def test_volume_velocity_spike_price_inside_band():
    price_alerts = check_price_depeg({"usd-coin": {"usd": 1.0}}, {"usd-coin": "USDC"}, 0.995, 1.005)
    assert price_alerts == []
    vt = _velocity_with_baseline()
    alert = vt.update("USDC", 400, now=1_300)
    assert alert is not None and alert.startswith("VOLUME VELOCITY USDC:")
    assert "5m" in alert and "3.0x" in alert
    print("PASS test_volume_velocity_spike_price_inside_band")


def test_volume_velocity_below_threshold():
    vt = _velocity_with_baseline()
    assert vt.update("USDC", 299, now=1_300) is None
    print("PASS test_volume_velocity_below_threshold")


def test_volume_velocity_exact_3x():
    vt = _velocity_with_baseline()
    alert = vt.update("USDC", 300, now=1_300)
    assert alert is not None and "VOLUME VELOCITY" in alert
    print("PASS test_volume_velocity_exact_3x")


def test_volume_velocity_custom_multiplier():
    vt = _velocity_with_baseline(multiplier=2.0, cooldown=0)
    alert = vt.update("USDC", 200, now=1_300)
    assert alert is not None and "2.0x" in alert
    assert vt.update("USDC", 199, now=1_400) is None
    print("PASS test_volume_velocity_custom_multiplier")


def test_volume_velocity_zero_and_short_history():
    vt = VolumeVelocityTracker(window=12, multiplier=3.0, min_samples=5)
    assert vt.update("USDT", 0, now=1) is None
    assert vt.update("USDT", -10, now=1) is None
    assert len(vt.history["USDT"]) == 0
    short = VolumeVelocityTracker(window=12, multiplier=3.0, min_samples=5)
    for vol in (100, 100, 100, 100):
        assert short.update("USDT", vol, now=1) is None
    assert short.update("USDT", 10_000, now=2) is None
    print("PASS test_volume_velocity_zero_and_short_history")


def test_volume_velocity_cooldown():
    vt = _velocity_with_baseline(cooldown=300)
    assert vt.update("USDC", 400, now=2_000) is not None
    assert vt.update("USDC", 500, now=2_100) is None
    assert vt.update("USDC", 500, now=2_300) is not None
    print("PASS test_volume_velocity_cooldown")


def test_volume_velocity_observe_bar_dedupe():
    vt = VolumeVelocityTracker(window=12, multiplier=3.0, min_samples=5, cooldown=300, bar_seconds=300)
    for vol in (100, 100, 100, 100, 100):
        vt.commit_bar("USDC", vol)
    assert vt.observe_bar("USDC", 100, bar_open_ts=1_000, now=1_000) is None
    assert vt.observe_bar("USDC", 120, bar_open_ts=1_000, now=1_010) is None
    assert len(vt.history["USDC"]) == 5
    alert = vt.observe_bar("USDC", 350, bar_open_ts=1_000, now=1_020)
    assert alert is not None and "VOLUME VELOCITY" in alert
    assert vt.observe_bar("USDC", 360, bar_open_ts=1_000, now=1_030) is None
    assert len(vt.history["USDC"]) == 5
    assert vt.observe_bar("USDC", 360, bar_open_ts=1_300, now=1_040) is None
    assert len(vt.history["USDC"]) == 6
    print("PASS test_volume_velocity_observe_bar_dedupe")


def test_volume_velocity_disabled():
    vt = VolumeVelocityTracker(enabled=False, min_samples=5)
    for vol in (100, 100, 100, 100, 100):
        vt.commit_bar("USDC", vol)
    assert vt.update("USDC", 9_999, now=1) is None
    assert vt.observe_bar("USDC", 9_999, bar_open_ts=5, now=1) is None
    print("PASS test_volume_velocity_disabled")


def test_volume_velocity_from_bars_ignores_price():
    vt = VolumeVelocityTracker(window=12, multiplier=3.0, min_samples=5, cooldown=300)
    bars = [(i * 300, 100) for i in range(5)] + [(1_500, 450)]
    alerts = velocity_alerts_for_symbol(vt, "DAI", bars, now=10_000)
    assert len(alerts) == 1 and "VOLUME VELOCITY DAI:" in alerts[0]
    # Same open bar on the next poll must not duplicate history or re-alert inside cooldown.
    again = velocity_alerts_for_symbol(vt, "DAI", bars, now=10_010)
    assert again == []
    assert len(vt.history["DAI"]) == 5
    print("PASS test_volume_velocity_from_bars_ignores_price")


def test_dry_run_usdc_097():
    cfg = {
        "stablecoins": DEFAULT_CONFIG["stablecoins"],
        "lower_bound": 0.995,
        "upper_bound": 1.005,
    }
    alerts = format_dry_run_alerts(cfg)
    assert len(alerts) == 1
    assert alerts[0].startswith(DRY_RUN_MARKER)
    assert "DEPEG DOWN" in alerts[0] and "USDC" in alerts[0] and "0.9700" in alerts[0]
    assert "USDT" not in alerts[0]
    print("PASS test_dry_run_usdc_097")


if __name__ == "__main__":
    tests = [
        test_clean_prices_no_alerts,
        test_depeg_down,
        test_depeg_up,
        test_missing_data,
        test_boundary_lower,
        test_boundary_upper,
        test_volume_spike,
        test_volume_no_spike,
        test_volume_zero_skipped,
        test_volume_median_robust,
        test_volume_cooldown,
        test_divergence,
        test_divergence_within_band,
        test_multi_coin_depeg,
        test_default_band_half_percent,
        test_half_percent_depeg_down,
        test_half_percent_depeg_up,
        test_half_percent_boundaries_ok,
        test_half_percent_inside_no_alert,
        test_one_percent_move_now_alerts,
        test_volume_velocity_spike_price_inside_band,
        test_volume_velocity_below_threshold,
        test_volume_velocity_exact_3x,
        test_volume_velocity_custom_multiplier,
        test_volume_velocity_zero_and_short_history,
        test_volume_velocity_cooldown,
        test_volume_velocity_observe_bar_dedupe,
        test_volume_velocity_disabled,
        test_volume_velocity_from_bars_ignores_price,
        test_dry_run_usdc_097,
    ]
    failed = 0
    for test in tests:
        try:
            test()
        except Exception as exc:
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
    passed = len(tests) - failed
    print(f"\n{passed}/{len(tests)} tests passed.")
    if failed:
        sys.exit(1)
# Covers depeg thresholds (including the 0.5% band), 24h volume spikes, 5-minute volume velocity, divergence, and the USDC $0.97 dry run.
