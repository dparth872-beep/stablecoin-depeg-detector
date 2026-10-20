#!/usr/bin/env python3
"""Unit tests for threshold logic using synthetic price data."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from depeg_detector import check_price_depeg, VolumeTracker, check_divergence


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
    alert = vt.update("USDT", 400)  # 4x average
    assert alert is not None and "VOLUME SPIKE" in alert
    print("PASS test_volume_spike")


def test_volume_no_spike():
    vt = VolumeTracker(window=10, multiplier=3.0)
    for v in [100, 110, 105, 95, 100, 102, 98, 101, 103, 99]:
        vt.update("USDT", v)
    alert = vt.update("USDT", 150)  # 1.5x average
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
    # baseline with outlier
    for v in [100, 105, 98, 102, 1000, 99, 101, 97, 103, 100]:
        vt.update("USDC", v)
    # median should ignore the 1000
    alert = vt.update("USDC", 350)
    assert alert is not None and "VOLUME SPIKE" in alert
    print("PASS test_volume_median_robust")


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


if __name__ == "__main__":
    test_clean_prices_no_alerts()
    test_depeg_down()
    test_depeg_up()
    test_missing_data()
    test_boundary_lower()
    test_boundary_upper()
    test_volume_spike()
    test_volume_no_spike()
    test_volume_zero_skipped()
    test_volume_median_robust()
    test_divergence()
    test_divergence_within_band()
    test_multi_coin_depeg()
    print("\nAll 13 tests passed.")
