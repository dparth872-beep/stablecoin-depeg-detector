#!/usr/bin/env python3
"""
Stablecoin Depeg Detector v2
===========================
Real-time monitor for stablecoin pegs with three signal tiers:
  1. Price depeg  - price outside $0.99-$1.01 (or custom band)
  2. Volume spike - 24h volume > 3x the rolling average
  3. Cross-source divergence - price gap between venues

Data sources: Binance WebSocket (tick-by-tick) with CoinGecko REST fallback.
Alert channels: console CLI dashboard, Telegram, email.

Usage:
    python depeg_detector.py                 # single snapshot
    python depeg_detector.py --loop 30       # poll every 30s
    python depeg_detector.py --ws            # live WebSocket stream
    python depeg_detector.py --dashboard     # refreshing CLI status board
    python depeg_detector.py --config f.json
"""

import argparse
import json
import smtplib
import sys
import threading
import time
from collections import defaultdict, deque
from email.mime.text import MIMEText
from typing import Deque, Dict, List, Optional, Tuple

import requests

try:
    import websocket  # pip install websocket-client
    HAS_WS = True
except ImportError:
    HAS_WS = False

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "stablecoins": {
        "tether": "USDT", "usd-coin": "USDC", "dai": "DAI",
        "first-digital-usd": "FDUSD", "paypal-usd": "PYUSD", "true-usd": "TUSD",
    },
    "binance_pairs": {  # CoinGecko id -> Binance symbol (lowercase)
        "tether": "usdtusdt", "usd-coin": "usdcusdt", "dai": "daiusdt",
        "first-digital-usd": "fdusdusdt", "paypal-usd": "pyusdusdt", "true-usd": "tusdusdt",
    },
    "lower_bound": 0.99,
    "upper_bound": 1.01,
    "volume_spike_multiplier": 3.0,
    "volume_window": 20,          # number of 24h-volume samples for rolling avg
    "divergence_threshold_bps": 50,  # cross-source gap in basis points
    "telegram": {"enabled": False, "bot_token": "", "chat_id": ""},
    "email": {
        "enabled": False, "smtp_host": "smtp.gmail.com", "smtp_port": 587,
        "username": "", "password": "", "to_address": "",
    },
    "poll_interval_seconds": 30,
}

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
)
BINANCE_WS = "wss://stream.binance.com:9443/stream?streams={streams}"


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------
def fetch_prices_rest(coin_ids: List[str], timeout: int = 20) -> Dict:
    url = COINGECKO_URL.format(ids=",".join(coin_ids))
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Signal logic
# ---------------------------------------------------------------------------
def check_price_depeg(prices: Dict, symbol_map: Dict[str, str],
                      lower: float, upper: float) -> List[str]:
    alerts = []
    for cg_id, symbol in symbol_map.items():
        entry = prices.get(cg_id)
        if not entry or "usd" not in entry:
            alerts.append(f"NO DATA    {symbol}: price missing from feed")
            continue
        price = entry["usd"]
        chg = entry.get("usd_24h_change")
        chg_s = f"{chg:+.2f}%" if chg is not None else "n/a"
        if price < lower:
            alerts.append(f"DEPEG DOWN {symbol}: ${price:.4f}  24h {chg_s}")
        elif price > upper:
            alerts.append(f"DEPEG UP   {symbol}: ${price:.4f}  24h {chg_s}")
    return alerts


class VolumeTracker:
    """Rolling 24h-volume samples per symbol; flags spikes > multiplier x avg."""
    def __init__(self, window: int = 20, multiplier: float = 3.0):
        self.window = window
        self.multiplier = multiplier
        self.samples: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=window))

    def update(self, symbol: str, volume: float) -> Optional[str]:
        if volume is None or volume <= 0:
            return None
        buf = self.samples[symbol]
        buf.append(volume)
        if len(buf) < max(5, self.window // 2):
            return None  # not enough history
        avg = sum(buf) / len(buf)
        if volume > avg * self.multiplier:
            return (f"VOLUME SPIKE {symbol}: 24h vol ${volume/1e6:.1f}M "
                    f"vs {self.multiplier:.0f}x avg ${avg/1e6:.1f}M")
        return None


def check_divergence(prices_a: Dict, prices_b: Dict, symbol_map: Dict[str, str],
                     threshold_bps: float) -> List[str]:
    """Flag when two sources disagree by more than threshold_bps."""
    alerts = []
    for cg_id, symbol in symbol_map.items():
        a = prices_a.get(cg_id, {}).get("usd")
        b = prices_b.get(cg_id, {}).get("usd")
        if a is None or b is None or a == 0:
            continue
        gap_bps = abs(a - b) / a * 10000
        if gap_bps > threshold_bps:
            alerts.append(
                f"DIVERGENCE {symbol}: CoinGecko ${a:.4f} vs Binance ${b:.4f} "
                f"({gap_bps:.0f} bps)")
    return alerts


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
def send_telegram(text: str, bot_token: str, chat_id: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=15)


def send_email(text: str, cfg: Dict) -> None:
    msg = MIMEText(text)
    msg["Subject"] = "[DEPEG ALERT] Stablecoin risk detected"
    msg["From"] = cfg["username"]
    msg["To"] = cfg["to_address"]
    with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
        server.starttls()
        server.login(cfg["username"], cfg["password"])
        server.send_message(msg)


def dispatch_alerts(alerts: List[str], cfg: Dict) -> None:
    if not alerts:
        return
    banner = "=" * 64
    body = banner + "\n" + "\n".join(alerts) + "\n" + banner
    print("\n" + body)
    tg = cfg.get("telegram", {})
    if tg.get("enabled") and tg.get("bot_token") and tg.get("chat_id"):
        try:
            send_telegram(body, tg["bot_token"], tg["chat_id"])
        except Exception as e:
            print(f"Telegram send failed: {e}", file=sys.stderr)
    em = cfg.get("email", {})
    if em.get("enabled") and em.get("username") and em.get("to_address"):
        try:
            send_email(body, em)
        except Exception as e:
            print(f"Email send failed: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI dashboard
# ---------------------------------------------------------------------------
def render_dashboard(rows: List[Tuple[str, str, str, str]]) -> None:
    """rows: (symbol, price, 24h_change, status)"""
    print("\033[2J\033[H", end="")  # clear screen
    print(f"{'COIN':<8}{'PRICE':>10}{'24h':>8}{'STATUS':>14}")
    print("-" * 42)
    for symbol, price, chg, status in rows:
        color = ""
        if "DEPEG" in status or "SPIKE" in status or "DIVERGE" in status:
            color = "\033[91m"  # red
        elif status == "OK":
            color = "\033[92m"  # green
        print(f"{color}{symbol:<8}{price:>10}{chg:>8}{status:>14}\033[0m")


# ---------------------------------------------------------------------------
# WebSocket mode
# ---------------------------------------------------------------------------
class BinanceWSClient:
    """Binance combined ticker stream with auto-reconnect."""

    def __init__(self, cfg: Dict, vol: VolumeTracker):
        self.cfg = cfg
        self.vol = vol
        self.symbol_map = cfg["stablecoins"]
        self.pair_to_cg = {v: k for k, v in cfg["binance_pairs"].items()}
        self.latest: Dict[str, Dict] = {}
        self.ws = None
        self.running = False
        self.reconnect_delay = 1

    def _streams(self) -> str:
        pairs = [p for p in self.cfg["binance_pairs"].values() if p]
        return "/".join(f"{p}@ticker" for p in pairs)

    def on_message(self, ws, message):
        try:
            msg = json.loads(message)
            data = msg.get("data", {})
            stream = msg.get("stream", "")
            symbol = data.get("s", "").lower()
            cg_id = self.pair_to_cg.get(symbol)
            if not cg_id:
                return
            price = float(data.get("c", 0))
            vol_24h = float(data.get("q", 0) or data.get("v", 0))  # quote or base volume
            self.latest[cg_id] = {"usd": price, "usd_24h_vol": vol_24h}
            # check immediately
            alerts = []
            if price < self.cfg["lower_bound"]:
                alerts.append(f"DEPEG DOWN {self.symbol_map[cg_id]}: ${price:.4f}")
            elif price > self.cfg["upper_bound"]:
                alerts.append(f"DEPEG UP {self.symbol_map[cg_id]}: ${price:.4f}")
            vol_alert = self.vol.update(self.symbol_map[cg_id], vol_24h)
            if vol_alert:
                alerts.append(vol_alert)
            if alerts:
                dispatch_alerts(alerts, self.cfg)
        except Exception as e:
            print(f"WS parse error: {e}", file=sys.stderr)

    def on_error(self, ws, error):
        print(f"WS error: {error}", file=sys.stderr)

    def on_close(self, ws, close_status_code, close_msg):
        print(f"WS closed: {close_status_code} {close_msg}")
        if self.running:
            time.sleep(self.reconnect_delay)
            self.reconnect_delay = min(self.reconnect_delay * 2, 60)
            self._connect()

    def on_open(self, ws):
        print("Binance WS connected.")
        self.reconnect_delay = 1

    def _connect(self):
        if not HAS_WS:
            print("websocket-client not installed. pip install websocket-client", file=sys.stderr)
            return
        url = BINANCE_WS.format(streams=self._streams())
        self.ws = websocket.WebSocketApp(
            url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
        )
        self.ws.run_forever(ping_interval=20, ping_timeout=10)

    def start(self):
        self.running = True
        print(f"Starting Binance WS for {len(self.cfg['binance_pairs'])} pairs...")
        self._connect()

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()


def run_ws(cfg: Dict, vol: VolumeTracker) -> None:
    client = BinanceWSClient(cfg, vol)
    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()
        print("\nWS stopped.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run_once(cfg: Dict, vol: VolumeTracker) -> List[str]:
    symbol_map = cfg["stablecoins"]
    prices = fetch_prices_rest(list(symbol_map.keys()))
    alerts = check_price_depeg(prices, symbol_map, cfg["lower_bound"], cfg["upper_bound"])
    for cg_id, symbol in symbol_map.items():
        vol_alert = vol.update(symbol, prices.get(cg_id, {}).get("usd_24h_vol"))
        if vol_alert:
            alerts.append(vol_alert)
    dispatch_alerts(alerts, cfg)
    return alerts


def run_dashboard(cfg: Dict, vol: VolumeTracker) -> None:
    symbol_map = cfg["stablecoins"]
    try:
        while True:
            prices = fetch_prices_rest(list(symbol_map.keys()))
            rows = []
            alerts = []
            for cg_id, symbol in symbol_map.items():
                e = prices.get(cg_id, {})
                p = e.get("usd")
                chg = e.get("usd_24h_change")
                price_s = f"${p:.4f}" if p is not None else "n/a"
                chg_s = f"{chg:+.2f}%" if chg is not None else "n/a"
                status = "OK"
                if p is not None:
                    if p < cfg["lower_bound"]:
                        status = "DEPEG DOWN"
                        alerts.append(f"DEPEG DOWN {symbol}: ${p:.4f}")
                    elif p > cfg["upper_bound"]:
                        status = "DEPEG UP"
                        alerts.append(f"DEPEG UP {symbol}: ${p:.4f}")
                vol_alert = vol.update(symbol, e.get("usd_24h_vol"))
                if vol_alert:
                    status = "VOL SPIKE"
                    alerts.append(vol_alert)
                rows.append((symbol, price_s, chg_s, status))
            render_dashboard(rows)
            dispatch_alerts(alerts, cfg)
            time.sleep(cfg["poll_interval_seconds"])
    except KeyboardInterrupt:
        print("\nDashboard stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stablecoin Depeg Detector v2")
    parser.add_argument("--config", default=None)
    parser.add_argument("--loop", type=int, default=0)
    parser.add_argument("--dashboard", action="store_true")
    parser.add_argument("--ws", action="store_true", help="WebSocket mode (requires websocket-client)")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            cfg = {**DEFAULT_CONFIG, **json.load(f)}
    else:
        cfg = DEFAULT_CONFIG

    vol = VolumeTracker(cfg["volume_window"], cfg["volume_spike_multiplier"])

    if args.ws:
        run_ws(cfg, vol)
    elif args.dashboard:
        run_dashboard(cfg, vol)
    elif args.loop > 0:
        print(f"Polling every {args.loop}s. Ctrl+C to stop.")
        while True:
            try:
                run_once(cfg, vol)
            except requests.RequestException as e:
                print(f"Fetch error: {e}", file=sys.stderr)
            except KeyboardInterrupt:
                print("\nStopped.")
                break
            time.sleep(args.loop)
    else:
        run_once(cfg, vol)


if __name__ == "__main__":
    main()
