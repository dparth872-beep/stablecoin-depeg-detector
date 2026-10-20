#!/usr/bin/env python3
"""Stablecoin Depeg Detector

Real-time monitor for USDT, USDC, DAI, FDUSD, PYUSD, TUSD.
Supports REST polling (CoinGecko), Binance WebSocket, volume anomaly detection,
and a live CLI dashboard.
"""

import argparse
import json
import os
import smtplib
import sys
import time
from collections import defaultdict, deque
from email.mime.text import MIMEText
from typing import Dict, List, Optional

import requests
try:
    import websocket
except ImportError:
    websocket = None

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ---------------------------------------------------------------------------
# Core signal logic (imported by tests)
# ---------------------------------------------------------------------------

def check_price_depeg(prices: Dict, symbol_map: Dict, lower: float, upper: float) -> List[str]:
    """Return list of depeg alert strings for prices outside [lower, upper]."""
    alerts = []
    for cg_id, symbol in symbol_map.items():
        data = prices.get(cg_id, {})
        price = data.get("usd")
        if price is None:
            alerts.append(f"NO DATA {symbol}")
            continue
        if price < lower:
            alerts.append(f"DEPEG DOWN {symbol}: ${price:.4f} (below {lower})")
        elif price > upper:
            alerts.append(f"DEPEG UP {symbol}: ${price:.4f} (above {upper})")
    return alerts


class VolumeTracker:
    """Rolling volume tracker that flags spikes > multiplier * median baseline.

    Ignores zero/negative volumes. Requires a minimum baseline before alerting.
    Uses median exclusively for robustness against outliers.
    """

    def __init__(self, window: int = 20, multiplier: float = 3.0):
        self.window = window
        self.multiplier = multiplier
        self.history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window))

    def update(self, symbol: str, volume: float) -> Optional[str]:
        if volume is None or volume <= 0:
            return None
        hist = self.history[symbol]
        if len(hist) >= max(5, self.window // 2):
            sorted_hist = sorted(hist)
            median = sorted_hist[len(sorted_hist)//2]
            baseline = median  # pure median for outlier resistance
            if baseline > 0 and volume > self.multiplier * baseline:
                alert = (
                    f"VOLUME SPIKE {symbol}: ${volume:,.0f} > {self.multiplier}x "
                    f"median baseline ${baseline:,.0f} (n={len(hist)})"
                )
                hist.append(volume)
                return alert
        hist.append(volume)
        return None


def check_divergence(prices_a: Dict, prices_b: Dict, symbol_map: Dict, threshold_bps: int = 50) -> List[str]:
    """Flag when two price sources diverge by more than threshold_bps basis points."""
    alerts = []
    for cg_id, symbol in symbol_map.items():
        pa = prices_a.get(cg_id, {}).get("usd")
        pb = prices_b.get(cg_id, {}).get("usd")
        if pa is None or pb is None or pa == 0:
            continue
        bps = abs(pa - pb) / pa * 10000
        if bps > threshold_bps:
            alerts.append(f"DIVERGENCE {symbol}: {bps:.0f} bps ({pa:.4f} vs {pb:.4f})")
    return alerts


# ---------------------------------------------------------------------------
# Config + alert sinks
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "stablecoins": {
        "tether": "USDT",
        "usd-coin": "USDC",
        "dai": "DAI",
        "first-digital-usd": "FDUSD",
        "paypal-usd": "PYUSD",
        "true-usd": "TUSD",
    },
    "binance_pairs": {
        "tether": "",
        "usd-coin": "usdcusdt",
        "dai": "daiusdt",
        "first-digital-usd": "fdusdusdt",
        "paypal-usd": "pyusdusdt",
        "true-usd": "tusdusdt",
    },
    "lower_bound": 0.99,
    "upper_bound": 1.01,
    "volume_spike_multiplier": 3.0,
    "volume_window": 20,
    "divergence_threshold_bps": 50,
    "telegram": {"enabled": False, "bot_token": "", "chat_id": ""},
    "email": {
        "enabled": False,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "",
        "password": "",
        "to_address": "",
    },
    "poll_interval_seconds": 30,
}


def load_config(path: str = "config.json") -> dict:
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(path):
        with open(path) as f:
            user = json.load(f)
        cfg.update(user)
        # nested merges for telegram/email
        for k in ("telegram", "email"):
            if k in user:
                cfg[k] = {**DEFAULT_CONFIG[k], **user[k]}
    return cfg


def send_telegram(cfg: dict, text: str):
    t = cfg.get("telegram", {})
    if not t.get("enabled") or not t.get("bot_token") or not t.get("chat_id"):
        return
    try:
        url = f"https://api.telegram.org/bot{t['bot_token']}/sendMessage"
        requests.post(url, json={"chat_id": t["chat_id"], "text": text}, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}", file=sys.stderr)


def send_email(cfg: dict, subject: str, body: str):
    e = cfg.get("email", {})
    if not e.get("enabled") or not e.get("username") or not e.get("password"):
        return
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = e["username"]
        msg["To"] = e.get("to_address", e["username"])
        with smtplib.SMTP(e.get("smtp_host", "smtp.gmail.com"), e.get("smtp_port", 587)) as s:
            s.starttls()
            s.login(e["username"], e["password"])
            s.send_message(msg)
    except Exception as ex:
        print(f"Email error: {ex}", file=sys.stderr)


def emit_alerts(cfg: dict, alerts: List[str], quiet: bool = False):
    if not alerts:
        return
    text = "\n".join(alerts)
    if not quiet:
        print(text)
    send_telegram(cfg, text)
    send_email(cfg, "Stablecoin Alert", text)


# ---------------------------------------------------------------------------
# REST (CoinGecko)
# ---------------------------------------------------------------------------

def fetch_coingecko(ids: List[str]) -> Optional[dict]:
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
    )
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            time.sleep(1)
    return None


def fetch_coinbase(symbol: str) -> Optional[float]:
    pairs = {"USDT": "USDT-USD", "USDC": "USDC-USD", "DAI": "DAI-USD", "PYUSD": "PYUSD-USD"}
    pair = pairs.get(symbol)
    if not pair:
        return None
    try:
        r = requests.get(f"https://api.coinbase.com/v2/prices/{pair}/spot", timeout=10)
        if r.status_code == 200:
            return float(r.json()["data"]["amount"])
    except Exception:
        pass
    return None


def snapshot_rest(cfg: dict) -> dict:
    """Multi-source snapshot: CoinGecko with Coinbase fallback for reliability."""
    data = fetch_coingecko(list(cfg["stablecoins"].keys())) or {}
    for cg_id, symbol in cfg["stablecoins"].items():
        if cg_id not in data or "usd" not in data.get(cg_id, {}):
            price = fetch_coinbase(symbol)
            if price is not None:
                data[cg_id] = {"usd": price, "usd_24h_change": 0, "usd_24h_vol": 0}
    return data


# ---------------------------------------------------------------------------
# Binance WebSocket
# ---------------------------------------------------------------------------

class BinanceWS:
    """Combined ticker stream with exponential backoff reconnection and heartbeat.

    Note: USDT itself has no USDTUSDT pair; it falls back to REST in other modes.
    Streams: usdcusdt, daiusdt, fdusdusdt, pyusdusdt, tusdusdt @ticker.
    Handles serverShutdown events by forcing reconnect.
    """

    def __init__(self, cfg: dict, on_ticker):
        self.cfg = cfg
        self.on_ticker = on_ticker
        self.running = False
        self.ws = None
        self.last_msg = time.time()
        streams = [p for p in cfg["binance_pairs"].values() if p]
        self.url = "wss://stream.binance.com:9443/stream?streams=" + "/".join(
            f"{s}@ticker" for s in streams
        )

    def start(self):
        if websocket is None:
            print("websocket-client not installed. pip install websocket-client", file=sys.stderr)
            return
        self.running = True
        backoff = 1
        while self.running:
            try:
                print(f"Connecting to Binance WS...", file=sys.stderr)
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                    on_open=self._on_open,
                )
                self.ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as e:
                print(f"WS error: {e}", file=sys.stderr)
            if not self.running:
                break
            # Stale connection check
            if time.time() - self.last_msg > 60:
                print("No messages for 60s, forcing reconnect", file=sys.stderr)
            print(f"WS reconnecting in {backoff}s...", file=sys.stderr)
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()

    def _on_open(self, ws):
        print("Binance WS connected.", file=sys.stderr)
        self.last_msg = time.time()

    def _on_message(self, ws, message):
        self.last_msg = time.time()
        try:
            payload = json.loads(message)
            data = payload.get("data", payload)
            # Handle server shutdown notice
            if data.get("e") == "serverShutdown":
                print("Binance serverShutdown received, forcing reconnect...", file=sys.stderr)
                if self.ws:
                    self.ws.close()
                return
            symbol = data.get("s", "").upper()
            # map binance symbol (e.g. USDCUSDT) back to cg_id
            for cg_id, pair in self.cfg["binance_pairs"].items():
                if pair and pair.upper() == symbol:
                    price = float(data.get("c", 0))
                    vol = float(data.get("q", 0))  # quote volume
                    self.on_ticker(cg_id, price, vol)
                    break
        except Exception as e:
            print(f"Parse error: {e}", file=sys.stderr)

    def _on_error(self, ws, error):
        print(f"WS error callback: {error}", file=sys.stderr)

    def _on_close(self, ws, code, msg):
        print(f"WS closed: code={code} msg={msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI Dashboard
# ---------------------------------------------------------------------------

def clear_screen():
    print("\033[H\033[2J", end="")


def color_status(status: str) -> str:
    if status == "OK":
        return f"{GREEN}{status}{RESET}"
    if status == "DEPEG":
        return f"{RED}{BOLD}{status}{RESET}"
    return f"{YELLOW}{status}{RESET}"


def render_dashboard(cfg: dict, prices: dict, volumes: dict):
    clear_screen()
    now = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    print(f"{BOLD}Stablecoin Depeg Detector  |  Live Dashboard  |  {now}{RESET}")
    print("-" * 78)
    print(f"{'Symbol':<8} {'Price':>10} {'24h%':>8} {'24h Volume':>16} {'Status':<12}")
    print("-" * 78)
    lower, upper = cfg["lower_bound"], cfg["upper_bound"]
    for cg_id, symbol in cfg["stablecoins"].items():
        p = prices.get(cg_id, {})
        price = p.get("usd")
        chg = p.get("usd_24h_change", 0)
        vol = volumes.get(symbol, p.get("usd_24h_vol", 0))
        if price is None:
            status = "NO DATA"
        elif price < lower or price > upper:
            status = "DEPEG"
        else:
            status = "OK"
        price_s = f"${price:.4f}" if price is not None else "   -"
        chg_s = f"{chg:+.2f}%" if chg else "   -"
        vol_s = f"${vol:,.0f}" if vol else "   -"
        print(f"{symbol:<8} {price_s:>10} {chg_s:>8} {vol_s:>16} {color_status(status):<20}")
    print("-" * 78)
    print("Thresholds: $0.99 - $1.01  |  Volume spike > 3x median baseline  |  Press Ctrl+C to exit")


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def run_snapshot(cfg: dict):
    prices = snapshot_rest(cfg)
    alerts = check_price_depeg(prices, cfg["stablecoins"], cfg["lower_bound"], cfg["upper_bound"])
    if alerts:
        emit_alerts(cfg, alerts)
    else:
        print("All stablecoins within $0.99-$1.01 band.")
        for cg_id, symbol in cfg["stablecoins"].items():
            p = prices.get(cg_id, {}).get("usd")
            print(f"  OK  {symbol}: ${p:.4f}" if p else f"  --  {symbol}: no data")


def run_loop(cfg: dict, interval: int):
    vt = VolumeTracker(cfg["volume_window"], cfg["volume_spike_multiplier"])
    print(f"Polling every {interval}s. Ctrl+C to stop.")
    try:
        while True:
            prices = snapshot_rest(cfg)
            alerts = check_price_depeg(prices, cfg["stablecoins"], cfg["lower_bound"], cfg["upper_bound"])
            for cg_id, symbol in cfg["stablecoins"].items():
                vol = prices.get(cg_id, {}).get("usd_24h_vol")
                if vol:
                    va = vt.update(symbol, vol)
                    if va:
                        alerts.append(va)
            emit_alerts(cfg, alerts)
            if not alerts:
                print(f"[{time.strftime('%H:%M:%S')}] all OK")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")


def run_dashboard(cfg: dict):
    vt = VolumeTracker(cfg["volume_window"], cfg["volume_spike_multiplier"])
    volumes = {}
    try:
        while True:
            prices = snapshot_rest(cfg)
            for cg_id, symbol in cfg["stablecoins"].items():
                vol = prices.get(cg_id, {}).get("usd_24h_vol")
                if vol:
                    volumes[symbol] = vol
                    vt.update(symbol, vol)
            render_dashboard(cfg, prices, volumes)
            time.sleep(cfg.get("poll_interval_seconds", 30))
    except KeyboardInterrupt:
        print("\nDashboard stopped.")


def run_ws(cfg: dict):
    if websocket is None:
        print("Install websocket-client to use --ws")
        return
    prices = {}
    volumes = {}
    vt = VolumeTracker(cfg["volume_window"], cfg["volume_spike_multiplier"])

    def on_ticker(cg_id, price, vol):
        prices[cg_id] = {"usd": price}
        symbol = cfg["stablecoins"].get(cg_id, cg_id)
        volumes[symbol] = vol
        alerts = check_price_depeg({cg_id: {"usd": price}}, {cg_id: symbol}, cfg["lower_bound"], cfg["upper_bound"])
        va = vt.update(symbol, vol)
        if va:
            alerts.append(va)
        emit_alerts(cfg, alerts, quiet=False)

    ws = BinanceWS(cfg, on_ticker)
    print(f"Starting Binance WS: {ws.url}")
    print("Tick-by-tick mode. Ctrl+C to stop.")
    try:
        ws.start()
    except KeyboardInterrupt:
        ws.stop()
        print("\nWS stopped.")


def main():
    parser = argparse.ArgumentParser(description="Stablecoin Depeg Detector")
    parser.add_argument("--loop", type=int, metavar="SEC", help="Poll every N seconds")
    parser.add_argument("--dashboard", action="store_true", help="Live CLI dashboard")
    parser.add_argument("--ws", action="store_true", help="Binance WebSocket mode")
    parser.add_argument("--config", default="config.json", help="Config file path")
    args = parser.parse_args()

    cfg = load_config(args.config)

    if args.ws:
        run_ws(cfg)
    elif args.dashboard:
        run_dashboard(cfg)
    elif args.loop:
        run_loop(cfg, args.loop)
    else:
        run_snapshot(cfg)


if __name__ == "__main__":
    main()
