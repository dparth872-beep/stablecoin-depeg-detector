#!/usr/bin/env python3
"""
Stablecoin Depeg Detector v2
============================
Real-time WebSocket monitor for stablecoin prices + volume anomalies.
Uses Coinbase Exchange WebSocket for tick-by-tick data with automatic reconnection.
Falls back to REST for coins without direct USD pairs.
Threshold logic: $0.99 - $1.01 default. Volume spike > 3x recent average.
CLI dashboard refreshes in place.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional

import requests
import websockets

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "stablecoins": {
        "USDT": "USDT-USD",
        "USDC": "USDC-USD",
        "DAI": "DAI-USD",
        "FDUSD": "FDUSD-USD",
        "PYUSD": "PYUSD-USD",
        "TUSD": "TUSD-USD",
    },
    "lower_bound": 0.99,
    "upper_bound": 1.01,
    "volume_spike_multiplier": 3.0,
    "volume_window": 20,
    "telegram": {"enabled": False, "bot_token": "", "chat_id": ""},
    "email": {"enabled": False, "smtp_host": "smtp.gmail.com", "smtp_port": 587,
              "username": "", "password": "", "to_address": ""},
}

COINBASE_WS = "wss://ws-feed.exchange.coinbase.com"
COINBASE_REST = "https://api.coinbase.com/v2/prices/{pair}/spot"

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
class CoinState:
    def __init__(self, symbol: str, pair: str):
        self.symbol = symbol
        self.pair = pair
        self.price: Optional[float] = None
        self.volume_24h: Optional[float] = None
        self.volumes: deque = deque(maxlen=50)
        self.last_update: float = 0.0
        self.status: str = "INIT"

states: Dict[str, CoinState] = {}

# ---------------------------------------------------------------------------
# Price / volume helpers
# ---------------------------------------------------------------------------
def check_thresholds(price: float, lower: float, upper: float) -> str:
    if price < lower:
        return "DEPEG_DOWN"
    if price > upper:
        return "DEPEG_UP"
    return "OK"

def check_volume_spike(state: CoinState, multiplier: float) -> bool:
    if len(state.volumes) < 5 or state.volume_24h is None:
        return False
    avg = sum(state.volumes) / len(state.volumes)
    return state.volume_24h > avg * multiplier

def fetch_rest_price(pair: str) -> Optional[float]:
    try:
        url = COINBASE_REST.format(pair=pair)
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return float(r.json()["data"]["amount"])
    except Exception:
        pass
    return None

# ---------------------------------------------------------------------------
# WebSocket client with reconnection
# ---------------------------------------------------------------------------
async def ws_listener(cfg: Dict, product_ids: List[str]):
    while True:
        try:
            async with websockets.connect(COINBASE_WS, ping_interval=20) as ws:
                sub = {
                    "type": "subscribe",
                    "product_ids": product_ids,
                    "channels": ["ticker"],
                }
                await ws.send(json.dumps(sub))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] WS connected. Subscribed to {product_ids}")
                async for raw in ws:
                    msg = json.loads(raw)
                    if msg.get("type") == "ticker":
                        pid = msg["product_id"]
                        for sym, st in states.items():
                            if st.pair == pid:
                                st.price = float(msg["price"])
                                st.volume_24h = float(msg.get("volume_24h", 0))
                                st.volumes.append(st.volume_24h)
                                st.last_update = time.time()
                                break
        except Exception as e:
            print(f"WS error: {e}. Reconnecting in 5s...", file=sys.stderr)
            await asyncio.sleep(5)

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def render_dashboard(cfg: Dict):
    os.system("clear" if os.name != "nt" else "cls")
    print(f"Stablecoin Depeg Detector  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    print(f"{'Symbol':<8} {'Price':>10} {'Status':<12} {'24h Vol':>15} {'Vol Alert':<10}")
    print("-" * 70)
    for sym, st in states.items():
        price_str = f"{st.price:.4f}" if st.price else "n/a"
        status = check_thresholds(st.price, cfg["lower_bound"], cfg["upper_bound"]) if st.price else "NO_DATA"
        vol_str = f"{st.volume_24h:,.0f}" if st.volume_24h else "n/a"
        vol_alert = "SPIKE" if check_volume_spike(st, cfg["volume_spike_multiplier"]) else ""
        print(f"{sym:<8} {price_str:>10} {status:<12} {vol_str:>15} {vol_alert:<10}")
    print("-" * 70)
    print("Ctrl+C to exit")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main_async(cfg: Dict):
    product_ids = []
    for sym, pair in cfg["stablecoins"].items():
        states[sym] = CoinState(sym, pair)
        product_ids.append(pair)

    for sym, st in states.items():
        p = fetch_rest_price(st.pair)
        if p:
            st.price = p
            st.last_update = time.time()

    ws_task = asyncio.create_task(ws_listener(cfg, product_ids))

    try:
        while True:
            render_dashboard(cfg)
            alerts = []
            for st in states.values():
                if st.price:
                    status = check_thresholds(st.price, cfg["lower_bound"], cfg["upper_bound"])
                    if status != "OK":
                        alerts.append(f"{status} {st.symbol}: ${st.price:.4f}")
                    if check_volume_spike(st, cfg["volume_spike_multiplier"]):
                        alerts.append(f"VOLUME_SPIKE {st.symbol}: {st.volume_24h:,.0f}")
            if alerts:
                print("\nALERTS:", " | ".join(alerts))
            await asyncio.sleep(2)
    except KeyboardInterrupt:
        ws_task.cancel()
        print("\nStopped.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None)
    args = parser.parse_args()
    cfg = DEFAULT_CONFIG.copy()
    if args.config:
        with open(args.config) as f:
            cfg.update(json.load(f))
    asyncio.run(main_async(cfg))

if __name__ == "__main__":
    main()
