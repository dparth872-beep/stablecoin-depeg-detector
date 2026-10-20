#!/usr/bin/env python3
"""Verification script: fetch prices from CoinGecko with retry + Coinbase fallback and print OK/ALERT."""
import time
import requests

STABLES = {
    "tether": "USDT",
    "usd-coin": "USDC",
    "dai": "DAI",
    "first-digital-usd": "FDUSD",
    "paypal-usd": "PYUSD",
    "true-usd": "TUSD",
}
COINBASE_PAIRS = {
    "USDT": "USDT-USD",
    "USDC": "USDC-USD",
    "DAI": "DAI-USD",
    "PYUSD": "PYUSD-USD",
}
LOWER, UPPER = 0.99, 1.01

def fetch_coingecko(ids):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd"
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                wait = 2 ** attempt
                print(f"  CoinGecko 429, retrying in {wait}s...")
                time.sleep(wait)
                continue
            else:
                print(f"  CoinGecko HTTP {r.status_code}")
                return None
        except Exception as e:
            print(f"  CoinGecko error: {e}")
            time.sleep(1)
    return None

def fetch_coinbase(sym):
    pair = COINBASE_PAIRS.get(sym)
    if not pair:
        return None
    try:
        r = requests.get(f"https://api.coinbase.com/v2/prices/{pair}/spot", timeout=10)
        if r.status_code == 200:
            return float(r.json()["data"]["amount"])
    except Exception:
        pass
    return None

def main():
    print("Stablecoin Depeg Detector - Price Verification")
    print("=" * 60)
    cg = fetch_coingecko(list(STABLES.keys()))
    for cg_id, symbol in STABLES.items():
        price = None
        source = "none"
        if cg and cg_id in cg and "usd" in cg[cg_id]:
            price = cg[cg_id]["usd"]
            source = "CoinGecko"
        if price is None:
            price = fetch_coinbase(symbol)
            if price is not None:
                source = "Coinbase"
        if price is None:
            print(f"NO DATA  {symbol}: unable to fetch")
            continue
        if price < LOWER:
            status = "ALERT"
            note = f"below {LOWER}"
        elif price > UPPER:
            status = "ALERT"
            note = f"above {UPPER}"
        else:
            status = "OK"
            note = "within band"
        print(f"{status:6} {symbol}: ${price:.4f}  ({note}) [{source}]")
    print("=" * 60)
    print("Verification complete. All reachable prices checked against $0.99-$1.01.")

if __name__ == "__main__":
    main()
