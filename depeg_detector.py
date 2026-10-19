#!/usr/bin/env python3
"""
Stablecoin Depeg Detector v1
===========================
Monitors major stablecoins in real time and fires alerts when any price
slips outside the safe band (default: $0.99 - $1.01).

Data source: CoinGecko free API (no key required)
Alert channels: console, Telegram bot, email (SMTP)

Usage:
    python depeg_detector.py              # single run
    python depeg_detector.py --loop 30    # poll every 30 seconds
    python depeg_detector.py --config config.json

Upgrade path: swap the REST poll for a Binance/Coinbase WebSocket for
tick-by-tick data, then layer on volume anomaly detection.
"""

import argparse
import json
import smtplib
import sys
import time
from email.mime.text import MIMEText
from typing import Dict, List, Optional

import requests

# ---------------------------------------------------------------------------
# Config defaults
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
    "lower_bound": 0.99,
    "upper_bound": 1.01,
    "telegram": {
        "enabled": False,
        "bot_token": "",
        "chat_id": "",
    },
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

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids={ids}&vs_currencies=usd&include_24hr_change=true"
)


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------
def fetch_prices(coin_ids: List[str], timeout: int = 20) -> Dict:
    """Pull USD prices + 24h change for the given CoinGecko IDs."""
    url = COINGECKO_URL.format(ids=",".join(coin_ids))
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Alert logic
# ---------------------------------------------------------------------------
def check_depegs(
    prices: Dict,
    symbol_map: Dict[str, str],
    lower: float,
    upper: float,
) -> List[str]:
    """Return alert strings for any stablecoin outside [lower, upper]."""
    alerts = []
    for cg_id, symbol in symbol_map.items():
        entry = prices.get(cg_id)
        if not entry or "usd" not in entry:
            alerts.append(f"NO DATA   {symbol}: price missing from feed")
            continue
        price = entry["usd"]
        change = entry.get("usd_24h_change")
        change_str = f"{change:+.2f}%" if change is not None else "n/a"
        if price < lower:
            alerts.append(
                f"DEPEG DOWN  {symbol}: ${price:.4f}  24h {change_str}"
            )
        elif price > upper:
            alerts.append(
                f"DEPEG UP    {symbol}: ${price:.4f}  24h {change_str}"
            )
        else:
            print(f"OK          {symbol}: ${price:.4f}  24h {change_str}")
    return alerts


# ---------------------------------------------------------------------------
# Notification channels
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
    banner = "=" * 60
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
# Main loop
# ---------------------------------------------------------------------------
def run_once(cfg: Dict) -> List[str]:
    symbol_map = cfg["stablecoins"]
    prices = fetch_prices(list(symbol_map.keys()))
    alerts = check_depegs(
        prices, symbol_map, cfg["lower_bound"], cfg["upper_bound"]
    )
    dispatch_alerts(alerts, cfg)
    return alerts


def main() -> None:
    parser = argparse.ArgumentParser(description="Stablecoin Depeg Detector")
    parser.add_argument("--config", default=None, help="Path to config.json")
    parser.add_argument(
        "--loop", type=int, default=0,
        help="Poll every N seconds (0 = single run)",
    )
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            cfg = {**DEFAULT_CONFIG, **json.load(f)}
    else:
        cfg = DEFAULT_CONFIG

    if args.loop > 0:
        print(f"Polling every {args.loop}s. Ctrl+C to stop.")
        while True:
            try:
                run_once(cfg)
            except requests.RequestException as e:
                print(f"Fetch error: {e}", file=sys.stderr)
            except KeyboardInterrupt:
                print("\nStopped.")
                break
            time.sleep(args.loop)
    else:
        run_once(cfg)


if __name__ == "__main__":
    main()
