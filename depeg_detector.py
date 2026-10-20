#!/usr/bin/env python3
"""
Stablecoin Depeg Detector
Monitors USDT, USDC, DAI, FDUSD, PYUSD, TUSD.
Supports CoinGecko REST, Binance WS, Coinbase WS, volume spikes, CLI dashboard.
"""

import argparse
import json
import os
import random
import smtplib
import statistics
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from email.mime.text import MIMEText

import requests
try:
    import websocket
except ImportError:
    websocket = None

CONFIG_PATH = "config.json"
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
    "coinbase_pairs": {
        "USDT": "USDT-USD",
        "USDC": "USDC-USD",
        "DAI": "DAI-USD",
        "PYUSD": "PYUSD-USD",
    },
    "lower_bound": 0.99,
    "upper_bound": 1.01,
    "volume_spike_multiplier": 3.0,
    "volume_window": 20,
    "divergence_threshold_bps": 50,
    "telegram": {"enabled": False, "bot_token": "", "chat_id": ""},
    "email": {"enabled": False, "smtp_host": "", "smtp_port": 587, "username": "", "password": "", "to_address": ""},
    "poll_interval_seconds": 30,
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
            # merge defaults
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
    return DEFAULT_CONFIG.copy()

def check_price_depeg(prices, symbol_map, lower, upper):
    """Return list of alert strings for depegs. Matches test expectations."""
    alerts = []
    for cg_id, symbol in symbol_map.items():
        data = prices.get(cg_id, {})
        price = data.get("usd")
        if price is None:
            alerts.append(f"NO DATA {symbol}")
            continue
        if price < lower:
            alerts.append(f"DEPEG DOWN {symbol}: ${price:.4f}")
        elif price > upper:
            alerts.append(f"DEPEG UP {symbol}: ${price:.4f}")
    return alerts

def check_divergence(prices_a, prices_b, symbol_map, threshold_bps=50):
    """Cross-source divergence alerts."""
    alerts = []
    for cg_id, symbol in symbol_map.items():
        pa = prices_a.get(cg_id, {}).get("usd")
        pb = prices_b.get(cg_id, {}).get("usd")
        if pa is None or pb is None:
            continue
        diff_bps = abs(pa - pb) / max(pa, pb) * 10000
        if diff_bps > threshold_bps:
            alerts.append(f"DIVERGENCE {symbol}: {pa:.4f} vs {pb:.4f} ({diff_bps:.0f} bps)")
    return alerts

class VolumeTracker:
    def __init__(self, window=20, multiplier=3.0, cooldown=300):
        self.window = window
        self.multiplier = multiplier
        self.cooldown = cooldown
        self.history = defaultdict(lambda: deque(maxlen=window))
        self.last_alert = {}

    def update(self, symbol, volume):
        if volume is None or volume <= 0:
            return None
        hist = self.history[symbol]
        min_samples = max(5, self.window // 2)
        if len(hist) < min_samples:
            hist.append(volume)
            return None
        baseline = statistics.median(hist)
        hist.append(volume)
        if baseline <= 0:
            return None
        if volume > self.multiplier * baseline:
            now = time.time()
            if symbol in self.last_alert and now - self.last_alert[symbol] < self.cooldown:
                return None
            self.last_alert[symbol] = now
            avg = statistics.mean(hist)
            return (f"VOLUME SPIKE {symbol}: ${volume:,.0f} > {self.multiplier}x "
                    f"baseline ${baseline:,.0f} (med=${baseline:,.0f}, avg=${avg:,.0f}, n={len(hist)})")
        return None

def send_telegram(cfg, msg):
    if not cfg["telegram"].get("enabled"):
        return
    token = cfg["telegram"].get("bot_token")
    chat = cfg["telegram"].get("chat_id")
    if not token or not chat:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": msg},
            timeout=10,
        )
    except Exception as e:
        print(f"Telegram error: {e}")

def send_email(cfg, subject, body):
    if not cfg["email"].get("enabled"):
        return
    e = cfg["email"]
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = e["username"]
        msg["To"] = e["to_address"]
        with smtplib.SMTP(e["smtp_host"], e["smtp_port"]) as s:
            s.starttls()
            s.login(e["username"], e["password"])
            s.send_message(msg)
    except Exception as ex:
        print(f"Email error: {ex}")

def alert(cfg, msg, console=True):
    if console:
        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}")
    send_telegram(cfg, msg)
    send_email(cfg, "Stablecoin Alert", msg)

def fetch_coingecko(ids):
    url = (f"https://api.coingecko.com/api/v3/simple/price?"
           f"ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true")
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

def fetch_coinbase_spot(symbol, pairs):
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

def rest_snapshot(cfg):
    """Fetch prices, prefer CoinGecko, fallback Coinbase."""
    symbols = cfg["stablecoins"]
    cg = fetch_coingecko(list(symbols.keys()))
    prices = {}
    for cg_id, symbol in symbols.items():
        data = {}
        if cg and cg_id in cg:
            data = cg[cg_id]
        if "usd" not in data:
            cb = fetch_coinbase_spot(symbol, cfg.get("coinbase_pairs", {}))
            if cb is not None:
                data = {"usd": cb}
        prices[cg_id] = data
    return prices

def print_snapshot(cfg):
    prices = rest_snapshot(cfg)
    lower, upper = cfg["lower_bound"], cfg["upper_bound"]
    print("Stablecoin Depeg Detector - Snapshot")
    print("=" * 70)
    for cg_id, symbol in cfg["stablecoins"].items():
        data = prices.get(cg_id, {})
        price = data.get("usd")
        vol = data.get("usd_24h_vol")
        chg = data.get("usd_24h_change")
        if price is None:
            print(f"NO DATA  {symbol}")
            continue
        status = "OK" if lower <= price <= upper else "ALERT"
        note = "within band" if status == "OK" else f"outside {lower}-{upper}"
        vol_s = f" vol=${vol:,.0f}" if vol else ""
        chg_s = f" 24h={chg:+.2f}%" if chg is not None else ""
        print(f"{status:6} {symbol}: ${price:.4f}  ({note}){vol_s}{chg_s}")
    print("=" * 70)
    alerts = check_price_depeg(prices, cfg["stablecoins"], lower, upper)
    for a in alerts:
        alert(cfg, a)
    return prices

def run_dashboard(cfg):
    vt = VolumeTracker(
        window=cfg.get("volume_window", 20),
        multiplier=cfg.get("volume_spike_multiplier", 3.0),
    )
    interval = cfg.get("poll_interval_seconds", 30)
    try:
        while True:
            prices = rest_snapshot(cfg)
            lower, upper = cfg["lower_bound"], cfg["upper_bound"]
            # clear screen
            print("\033[2J\033[H", end="")
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"Stablecoin Depeg Detector  |  Live Dashboard  |  {now}")
            print("-" * 80)
            print(f"{'Symbol':<10} {'Price':>10} {'24h%':>8} {'24h Volume':>18} Status")
            print("-" * 80)
            for cg_id, symbol in cfg["stablecoins"].items():
                data = prices.get(cg_id, {})
                price = data.get("usd")
                vol = data.get("usd_24h_vol")
                chg = data.get("usd_24h_change")
                if price is None:
                    status = "NO DATA"
                    color = "\033[33m"
                    price_s = chg_s = vol_s = "—"
                else:
                    if lower <= price <= upper:
                        status = "OK"
                        color = "\033[32m"
                    else:
                        status = "DEPEG"
                        color = "\033[31m"
                    price_s = f"${price:.4f}"
                    chg_s = f"{chg:+.2f}%" if chg is not None else "—"
                    vol_s = f"${vol:,.0f}" if vol else "—"
                    # volume track
                    if vol:
                        v_alert = vt.update(symbol, vol)
                        if v_alert:
                            alert(cfg, v_alert, console=False)
                            print(f"\033[33m{v_alert}\033[0m")
                print(f"{symbol:<10} {price_s:>10} {chg_s:>8} {vol_s:>18} {color}{status}\033[0m")
            print("-" * 80)
            print("Thresholds: $0.99–$1.01 | Volume spike: 3x median | Ctrl+C to exit")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nDashboard stopped.")

def run_loop(cfg, interval):
    vt = VolumeTracker(
        window=cfg.get("volume_window", 20),
        multiplier=cfg.get("volume_spike_multiplier", 3.0),
    )
    while True:
        prices = rest_snapshot(cfg)
        lower, upper = cfg["lower_bound"], cfg["upper_bound"]
        alerts = check_price_depeg(prices, cfg["stablecoins"], lower, upper)
        for a in alerts:
            alert(cfg, a)
        for cg_id, symbol in cfg["stablecoins"].items():
            vol = prices.get(cg_id, {}).get("usd_24h_vol")
            if vol:
                v_alert = vt.update(symbol, vol)
                if v_alert:
                    alert(cfg, v_alert)
        time.sleep(interval)

# WebSocket implementations
class BinanceWS:
    def __init__(self, cfg, on_ticker):
        self.cfg = cfg
        self.on_ticker = on_ticker
        self.streams = []
        for pair in cfg["binance_pairs"].values():
            if pair:
                self.streams.append(f"{pair}@ticker")
        self.url = "wss://stream.binance.com:9443/stream?streams=" + "/".join(self.streams)
        self.ws = None
        self.running = True

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if "data" in data:
                d = data["data"]
                symbol = d.get("s", "").replace("USDT", "")
                price = float(d.get("c", 0))
                vol = float(d.get("v", 0))
                self.on_ticker(symbol, price, vol)
        except Exception:
            pass

    def on_error(self, ws, error):
        print(f"Binance WS error: {error}")

    def on_close(self, ws, close_status, close_msg):
        print("Binance WS closed")

    def on_open(self, ws):
        print("Binance WS connected")

    def run(self):
        if not websocket:
            print("websocket-client not installed")
            return
        backoff = 1
        while self.running:
            try:
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open,
                )
                self.ws.run_forever(ping_interval=30, ping_timeout=10)
            except Exception as e:
                print(f"Binance WS exception: {e}")
            if not self.running:
                break
            jitter = random.uniform(0, 1)
            wait = min(60, backoff + jitter)
            print(f"Reconnecting in {wait:.1f}s...")
            time.sleep(wait)
            backoff = min(60, backoff * 2)

class CoinbaseWS:
    def __init__(self, cfg, on_ticker):
        self.cfg = cfg
        self.on_ticker = on_ticker
        self.pairs = list(cfg.get("coinbase_pairs", {}).values())
        self.url = "wss://ws-feed.exchange.coinbase.com"
        self.running = True

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data.get("type") == "ticker":
                product = data.get("product_id", "")
                symbol = product.split("-")[0]
                price = float(data.get("price", 0))
                vol = float(data.get("volume_24h", 0) or 0)
                self.on_ticker(symbol, price, vol)
        except Exception:
            pass

    def on_error(self, ws, error):
        print(f"Coinbase WS error: {error}")

    def on_close(self, ws, *args):
        print("Coinbase WS closed")

    def on_open(self, ws):
        sub = {
            "type": "subscribe",
            "product_ids": self.pairs,
            "channels": ["ticker"],
        }
        ws.send(json.dumps(sub))
        print("Coinbase WS subscribed")

    def run(self):
        if not websocket:
            print("websocket-client not installed")
            return
        backoff = 1
        while self.running:
            try:
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open,
                )
                self.ws.run_forever(ping_interval=30, ping_timeout=10)
            except Exception as e:
                print(f"Coinbase WS exception: {e}")
            if not self.running:
                break
            jitter = random.uniform(0, 1)
            wait = min(60, backoff + jitter)
            print(f"Reconnecting in {wait:.1f}s...")
            time.sleep(wait)
            backoff = min(60, backoff * 2)

def run_ws(cfg, use_coinbase=False):
    vt = VolumeTracker(
        window=cfg.get("volume_window", 20),
        multiplier=cfg.get("volume_spike_multiplier", 3.0),
    )
    lower, upper = cfg["lower_bound"], cfg["upper_bound"]
    symbol_to_cg = {v: k for k, v in cfg["stablecoins"].items()}

    def on_ticker(symbol, price, vol):
        cg_id = symbol_to_cg.get(symbol)
        if not cg_id:
            return
        status = "OK" if lower <= price <= upper else "ALERT"
        print(f"{status:6} {symbol}: ${price:.4f}")
        if status == "ALERT":
            direction = "DOWN" if price < lower else "UP"
            alert(cfg, f"DEPEG {direction} {symbol}: ${price:.4f}")
        if vol:
            v_alert = vt.update(symbol, vol)
            if v_alert:
                alert(cfg, v_alert)

    if use_coinbase:
        client = CoinbaseWS(cfg, on_ticker)
    else:
        client = BinanceWS(cfg, on_ticker)
    client.run()

def main():
    parser = argparse.ArgumentParser(description="Stablecoin Depeg Detector")
    parser.add_argument("--loop", type=int, help="Poll every N seconds")
    parser.add_argument("--dashboard", action="store_true", help="Live CLI dashboard")
    parser.add_argument("--ws", action="store_true", help="Binance WebSocket")
    parser.add_argument("--ws-coinbase", action="store_true", help="Coinbase WebSocket")
    args = parser.parse_args()
    cfg = load_config()

    if args.ws or args.ws_coinbase:
        run_ws(cfg, use_coinbase=args.ws_coinbase)
    elif args.dashboard:
        run_dashboard(cfg)
    elif args.loop:
        run_loop(cfg, args.loop)
    else:
        print_snapshot(cfg)

if __name__ == "__main__":
    main()
