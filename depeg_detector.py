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
VERSION = "1.8.0"
# Dry-run delivery is limited to this address. It is the owner's own inbox.
PARTH_EMAIL = "dparth872@gmail.com"
DRY_RUN_MARKER = "[TEST/DRY RUN]"
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
    "lower_bound": 0.995,
    "upper_bound": 1.005,
    "volume_spike_multiplier": 3.0,
    "volume_window": 20,
    # 5-minute volume vs the median of prior 5-minute bars. Alerts even if price is inside the band.
    "volume_velocity_enabled": True,
    "volume_velocity_multiplier": 3.0,
    "volume_velocity_window": 12,
    "volume_velocity_min_samples": 5,
    "volume_velocity_cooldown": 300,
    "volume_velocity_bar_seconds": 300,
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

class VolumeVelocityTracker:
    """Alert when the current 5-minute volume is at least `multiplier` times the median of prior bars.

    Price is not an input. A breach alerts even if the peg is still inside the band.
    `update` treats each call as one completed bar (tests and pre-bucketed samples).
    `observe_bar` is for live polls: the open bar is rechecked in place and committed once, when it rolls.
    """

    def __init__(self, window=12, multiplier=3.0, min_samples=5, cooldown=300, bar_seconds=300, enabled=True):
        self.window = window
        self.multiplier = multiplier
        self.min_samples = min_samples
        self.cooldown = cooldown
        self.bar_seconds = bar_seconds
        self.enabled = enabled
        self.history = defaultdict(lambda: deque(maxlen=window))
        self.open_bar = {}
        self.last_alert = {}
        self.seeded = set()

    def commit_bar(self, symbol, volume):
        if volume is None or volume <= 0:
            return
        self.history[symbol].append(volume)

    def _alert_if_breach(self, symbol, volume, now):
        if not self.enabled or volume is None or volume <= 0:
            return None
        hist = self.history[symbol]
        if len(hist) < self.min_samples:
            return None
        baseline = statistics.median(hist)
        if baseline <= 0:
            return None
        if volume < self.multiplier * baseline:
            return None
        if symbol in self.last_alert and now - self.last_alert[symbol] < self.cooldown:
            return None
        self.last_alert[symbol] = now
        return (f"VOLUME VELOCITY {symbol}: 5m ${volume:,.0f} >= {self.multiplier}x "
                f"median baseline ${baseline:,.0f} (n={len(hist)}, bar={self.bar_seconds}s)")

    def update(self, symbol, volume_5m, now=None):
        if now is None:
            now = time.time()
        if not self.enabled or volume_5m is None or volume_5m <= 0:
            return None
        msg = self._alert_if_breach(symbol, volume_5m, now)
        self.commit_bar(symbol, volume_5m)
        return msg

    def observe_bar(self, symbol, volume_5m, bar_open_ts, now=None):
        if now is None:
            now = time.time()
        if not self.enabled or volume_5m is None or volume_5m <= 0 or bar_open_ts is None:
            return None
        prev = self.open_bar.get(symbol)
        if prev is not None and prev[0] != bar_open_ts:
            self.commit_bar(symbol, prev[1])
        self.open_bar[symbol] = (bar_open_ts, volume_5m)
        return self._alert_if_breach(symbol, volume_5m, now)

def make_velocity_tracker(cfg):
    return VolumeVelocityTracker(
        window=cfg.get("volume_velocity_window", 12),
        multiplier=cfg.get("volume_velocity_multiplier", 3.0),
        min_samples=cfg.get("volume_velocity_min_samples", 5),
        cooldown=cfg.get("volume_velocity_cooldown", 300),
        bar_seconds=cfg.get("volume_velocity_bar_seconds", 300),
        enabled=cfg.get("volume_velocity_enabled", True),
    )

def _channel_status(channel, status, reason):
    return {"channel": channel, "status": status, "reason": reason}

def send_telegram(cfg, msg, dry_run=False):
    tg = cfg.get("telegram") or {}
    if not tg.get("enabled"):
        return _channel_status(
            "telegram",
            "unverified",
            "telegram.enabled is false, so no Telegram message was sent.",
        )
    token = tg.get("bot_token") or ""
    chat = str(tg.get("chat_id") or "")
    if (not token or not chat or token == "YOUR_BOT_TOKEN" or chat == "YOUR_CHAT_ID"):
        return _channel_status("telegram", "unverified", "Telegram bot token or chat id is missing.")
    if dry_run:
        # No confirmed owner chat id is stored in this repo, so a dry run must not message an unknown chat.
        return _channel_status(
            "telegram",
            "unverified",
            "Dry run did not send. This environment has no confirmed Parth chat id to check the configured chat against.",
        )
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": msg},
            timeout=10,
        )
        if r.status_code == 200:
            return _channel_status("telegram", "sent", "Telegram accepted the message.")
        return _channel_status("telegram", "failed", f"Telegram HTTP {r.status_code}.")
    except Exception as e:
        print(f"Telegram error: {e}")
        return _channel_status("telegram", "failed", f"Telegram error: {e}")

def send_email(cfg, subject, body, dry_run=False):
    email_cfg = cfg.get("email") or {}
    if not email_cfg.get("enabled"):
        return _channel_status(
            "email",
            "unverified",
            "email.enabled is false, so no SMTP message was sent.",
        )
    required = ("smtp_host", "smtp_port", "username", "password", "to_address")
    if any(not email_cfg.get(k) for k in required) or email_cfg.get("password") == "your_app_password":
        return _channel_status("email", "unverified", "SMTP settings are incomplete.")
    recipient = str(email_cfg.get("to_address") or "").strip().lower()
    if dry_run and recipient != PARTH_EMAIL:
        return _channel_status(
            "email",
            "unverified",
            f"Dry run did not send. Recipient {recipient or '(empty)'} is not {PARTH_EMAIL}.",
        )
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = email_cfg["username"]
        msg["To"] = email_cfg["to_address"]
        with smtplib.SMTP(email_cfg["smtp_host"], email_cfg["smtp_port"]) as s:
            s.starttls()
            s.login(email_cfg["username"], email_cfg["password"])
            s.send_message(msg)
        return _channel_status("email", "sent", f"SMTP accepted the message for {email_cfg['to_address']}.")
    except Exception as ex:
        print(f"Email error: {ex}")
        return _channel_status("email", "failed", f"Email error: {ex}")

def alert(cfg, msg, console=True, dry_run=False):
    if console:
        print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}")
    telegram_status = send_telegram(cfg, msg, dry_run=dry_run)
    subject = f"{DRY_RUN_MARKER} Stablecoin Alert" if dry_run else "Stablecoin Alert"
    email_status = send_email(cfg, subject, msg, dry_run=dry_run)
    return {"telegram": telegram_status, "email": email_status}

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

def fetch_defillama(ids):
    llama_ids = ",".join(f"coingecko:{i}" for i in ids)
    try:
        r = requests.get(f"https://coins.llama.fi/prices/current/{llama_ids}", timeout=15)
        if r.status_code == 200:
            return r.json().get("coins", {})
    except Exception:
        pass
    return {}

def _binance_5m_bars(pair, limit):
    r = requests.get(
        "https://api.binance.com/api/v3/klines",
        params={"symbol": pair.upper(), "interval": "5m", "limit": limit},
        timeout=8,
    )
    if r.status_code != 200:
        return None
    bars = []
    for row in r.json():
        # [open time ms, ..., quote volume at index 7]
        bars.append((int(row[0]) // 1000, float(row[7])))
    return bars

def _coinbase_5m_bars(product, limit):
    end = int(time.time())
    start = end - limit * 300
    r = requests.get(
        f"https://api.exchange.coinbase.com/products/{product}/candles",
        params={"granularity": 300, "start": start, "end": end},
        timeout=8,
    )
    if r.status_code != 200:
        return None
    rows = r.json()
    if not isinstance(rows, list):
        return None
    bars = []
    for row in rows:
        ts, _low, _high, _open, close, vol = row
        bars.append((int(ts), float(vol) * float(close)))
    bars.sort(key=lambda item: item[0])
    return bars[-limit:]

def fetch_5m_bars(cg_id, symbol, cfg, limit=None):
    """Oldest-first (bar_open_ts, quote volume) including the in-progress 5-minute bar."""
    if limit is None:
        limit = int(cfg.get("volume_velocity_window", 12)) + 1
    pair = (cfg.get("binance_pairs") or {}).get(cg_id) or ""
    if pair:
        try:
            bars = _binance_5m_bars(pair, limit)
            if bars:
                return bars
        except Exception:
            pass
    product = (cfg.get("coinbase_pairs") or {}).get(symbol)
    if product:
        try:
            bars = _coinbase_5m_bars(product, limit)
            if bars:
                return bars
        except Exception:
            pass
    return []

def velocity_alerts_for_symbol(tracker, symbol, bars, now=None):
    """Seed prior closed bars once, then alert on the current bar if it breaches."""
    if not bars or not tracker.enabled:
        return []
    if symbol not in tracker.seeded:
        for _ts, vol in bars[:-1]:
            tracker.commit_bar(symbol, vol)
        tracker.seeded.add(symbol)
    ts, vol = bars[-1]
    msg = tracker.observe_bar(symbol, vol, ts, now=now)
    return [msg] if msg else []

def check_volume_velocity(cfg, tracker, now=None):
    if not cfg.get("volume_velocity_enabled", True):
        return []
    alerts = []
    limit = int(cfg.get("volume_velocity_window", 12)) + 1
    for cg_id, symbol in cfg["stablecoins"].items():
        bars = fetch_5m_bars(cg_id, symbol, cfg, limit=limit)
        alerts.extend(velocity_alerts_for_symbol(tracker, symbol, bars, now=now))
    return alerts

def synthetic_dry_run_prices(cfg):
    """USDC at $0.97; every other configured coin sits on the peg. No network."""
    prices = {cg_id: {"usd": 1.0} for cg_id in cfg["stablecoins"]}
    if "usd-coin" in prices:
        prices["usd-coin"] = {"usd": 0.97}
    return prices

def format_dry_run_alerts(cfg):
    prices = synthetic_dry_run_prices(cfg)
    raw = check_price_depeg(prices, cfg["stablecoins"], cfg["lower_bound"], cfg["upper_bound"])
    return [f"{DRY_RUN_MARKER} {item}" for item in raw]

def run_dry_run(cfg):
    """Push a fake USDC print of $0.97 through the same alert path as a live depeg."""
    alerts = format_dry_run_alerts(cfg)
    print(f"{DRY_RUN_MARKER} Simulated USDC price $0.9700 through the alert pipeline.")
    print(f"{DRY_RUN_MARKER} This is not a live market event.")
    deliveries = []
    if not alerts:
        print(f"{DRY_RUN_MARKER} No alert was produced.")
    for item in alerts:
        print(item)
        delivery = alert(cfg, item, console=False, dry_run=True)
        deliveries.append(delivery)
        for channel in ("telegram", "email"):
            result = delivery[channel]
            print(f"{DRY_RUN_MARKER} {channel}: {result['status']} — {result['reason']}")
    print(f"{DRY_RUN_MARKER} Dashboard check: open dashboard.html?dry_run=1")
    return {"alerts": alerts, "deliveries": deliveries}

def rest_snapshot(cfg):
    """Fetch prices, prefer CoinGecko, fallback Coinbase then DefiLlama."""
    symbols = cfg["stablecoins"]
    ids = list(symbols.keys())
    cg = fetch_coingecko(ids)
    llama = fetch_defillama(ids)
    prices = {}
    for cg_id, symbol in symbols.items():
        data = {}
        if cg and cg_id in cg:
            data = cg[cg_id]
        if "usd" not in data:
            cb = fetch_coinbase_spot(symbol, cfg.get("coinbase_pairs", {}))
            if cb is not None:
                data = {"usd": cb}
        if "usd" not in data:
            llama_key = f"coingecko:{cg_id}"
            if llama_key in llama and "price" in llama[llama_key]:
                data = {"usd": llama[llama_key]["price"]}
        prices[cg_id] = data
    return prices

def snapshot_to_json(cfg, prices):
    """Structured JSON output for integration."""
    lower, upper = cfg["lower_bound"], cfg["upper_bound"]
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": VERSION,
        "thresholds": {"lower": lower, "upper": upper},
        "coins": []
    }
    for cg_id, symbol in cfg["stablecoins"].items():
        data = prices.get(cg_id, {})
        price = data.get("usd")
        status = "NO_DATA"
        if price is not None:
            status = "OK" if lower <= price <= upper else "DEPEG"
        result["coins"].append({
            "symbol": symbol,
            "cg_id": cg_id,
            "price": price,
            "usd_24h_vol": data.get("usd_24h_vol"),
            "usd_24h_change": data.get("usd_24h_change"),
            "status": status,
        })
    return result

def print_snapshot(cfg, as_json=False):
    prices = rest_snapshot(cfg)
    if as_json:
        print(json.dumps(snapshot_to_json(cfg, prices), indent=2))
        return prices
    lower, upper = cfg["lower_bound"], cfg["upper_bound"]
    print(f"Stablecoin Depeg Detector v{VERSION} - Snapshot")
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
    velocity = make_velocity_tracker(cfg)
    for a in check_volume_velocity(cfg, velocity):
        alert(cfg, a)
    return prices

def run_dashboard(cfg):
    vt = VolumeTracker(
        window=cfg.get("volume_window", 20),
        multiplier=cfg.get("volume_spike_multiplier", 3.0),
    )
    velocity = make_velocity_tracker(cfg)
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
            for v_alert in check_volume_velocity(cfg, velocity):
                alert(cfg, v_alert, console=False)
                print(f"\033[33m{v_alert}\033[0m")
            print("-" * 80)
            vmul = cfg.get("volume_velocity_multiplier", 3.0)
            print(f"Thresholds: ${lower:.3f}–${upper:.3f} | 24h volume spike: "
                  f"{cfg.get('volume_spike_multiplier', 3.0)}x median | "
                  f"5m velocity: {vmul}x median | Ctrl+C to exit")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nDashboard stopped.")

def run_loop(cfg, interval):
    vt = VolumeTracker(
        window=cfg.get("volume_window", 20),
        multiplier=cfg.get("volume_spike_multiplier", 3.0),
    )
    velocity = make_velocity_tracker(cfg)
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
        for v_alert in check_volume_velocity(cfg, velocity):
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
            print("websocket-client not installed; pip install websocket-client")
            return
        backoff = 1
        reconnects = 0
        while self.running:
            try:
                print(f"Connecting Binance WS (attempt {reconnects+1})...")
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open,
                )
                self.ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as e:
                print(f"Binance WS exception: {e}")
            if not self.running:
                break
            reconnects += 1
            jitter = random.uniform(0, 2)
            wait = min(60, backoff + jitter)
            print(f"[WS] Binance reconnect #{reconnects} in {wait:.1f}s (backoff {backoff}s)")
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
            print("websocket-client not installed; pip install websocket-client")
            return
        backoff = 1
        reconnects = 0
        while self.running:
            try:
                print(f"Connecting Coinbase WS (attempt {reconnects+1})...")
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open,
                )
                self.ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as e:
                print(f"Coinbase WS exception: {e}")
            if not self.running:
                break
            reconnects += 1
            jitter = random.uniform(0, 2)
            wait = min(60, backoff + jitter)
            print(f"[WS] Coinbase reconnect #{reconnects} in {wait:.1f}s (backoff {backoff}s)")
            time.sleep(wait)
            backoff = min(60, backoff * 2)

def run_ws(cfg, use_coinbase=False):
    vt = VolumeTracker(
        window=cfg.get("volume_window", 20),
        multiplier=cfg.get("volume_spike_multiplier", 3.0),
    )
    velocity = make_velocity_tracker(cfg)
    lower, upper = cfg["lower_bound"], cfg["upper_bound"]
    symbol_to_cg = {v: k for k, v in cfg["stablecoins"].items()}
    last_velocity_check = {"t": 0.0}

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
        now = time.time()
        # Same poll cadence as the REST loop. Do not change poll_interval_seconds itself.
        if now - last_velocity_check["t"] >= cfg.get("poll_interval_seconds", 30):
            last_velocity_check["t"] = now
            for v_alert in check_volume_velocity(cfg, velocity):
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
    parser.add_argument("--json", action="store_true", help="Output snapshot as JSON")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulate a USDC print of $0.97 and mark every alert as a test")
    args = parser.parse_args()
    cfg = load_config()

    if args.dry_run:
        result = run_dry_run(cfg)
        failed = any(not item.startswith(DRY_RUN_MARKER) or "DEPEG DOWN" not in item or "USDC" not in item
                     for item in result["alerts"]) or not result["alerts"]
        sys.exit(1 if failed else 0)
    if args.ws or args.ws_coinbase:
        run_ws(cfg, use_coinbase=args.ws_coinbase)
    elif args.dashboard:
        run_dashboard(cfg)
    elif args.loop:
        run_loop(cfg, args.loop)
    else:
        print_snapshot(cfg, as_json=args.json)

if __name__ == "__main__":
    main()
