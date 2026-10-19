#!/usr/bin/env python3
"""Tests for depeg threshold and volume spike logic."""
import unittest
from collections import deque

import sys
sys.path.insert(0, ".")
from depeg_detector import check_thresholds, check_volume_spike, CoinState

class TestDepegLogic(unittest.TestCase):
    def test_ok_within_band(self):
        self.assertEqual(check_thresholds(1.0000, 0.99, 1.01), "OK")
        self.assertEqual(check_thresholds(0.9950, 0.99, 1.01), "OK")
        self.assertEqual(check_thresholds(1.0050, 0.99, 1.01), "OK")

    def test_depeg_down(self):
        self.assertEqual(check_thresholds(0.9890, 0.99, 1.01), "DEPEG_DOWN")
        self.assertEqual(check_thresholds(0.9800, 0.99, 1.01), "DEPEG_DOWN")

    def test_depeg_up(self):
        self.assertEqual(check_thresholds(1.0110, 0.99, 1.01), "DEPEG_UP")
        self.assertEqual(check_thresholds(1.0200, 0.99, 1.01), "DEPEG_UP")

    def test_volume_spike(self):
        st = CoinState("USDT", "USDT-USD")
        for v in [1000, 1100, 900, 1050, 950]:
            st.volumes.append(v)
        st.volume_24h = 1000
        self.assertFalse(check_volume_spike(st, 3.0))
        st.volume_24h = 4000
        self.assertTrue(check_volume_spike(st, 3.0))

    def test_volume_insufficient_data(self):
        st = CoinState("USDC", "USDC-USD")
        st.volumes.append(1000)
        st.volume_24h = 5000
        self.assertFalse(check_volume_spike(st, 3.0))

if __name__ == "__main__":
    unittest.main()
