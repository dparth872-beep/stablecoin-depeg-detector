#!/usr/bin/env python3
"""One-shot verification of price fetch + threshold logic.
CoinGecko free tier was rate-limited from this environment; uses Coinbase REST as proxy.
"""
import requests

PAIRS = {
    "USDT": "USDT-USD",
    "USDC": "USDC-USD",
    "DAI": "DAI-USD",
    "FDUSD": "FDUSD-USD",
    "PYUSD": "PYUSD-USD",
    "TUSD": "TUSD-USD",
}
LOWER, UPPER = 0.99, 1.01

def main():
    print("Stablecoin price verification")
    for sym, pair in PAIRS.items():
        try:
            r = requests.get(f"https://api.coinbase.com/v2/prices/{pair}/spot", timeout=10)
            if r.status_code == 200:
                price = float(r.json()["data"]["amount"])
                if price < LOWER:
                    print(f"ALERT  {sym}: ${price:.4f}  (below {LOWER})")
                elif price > UPPER:
                    print(f"ALERT  {sym}: ${price:.4f}  (above {UPPER})")
                else:
                    print(f"OK     {sym}: ${price:.4f}")
            else:
                print(f"NO_DATA {sym}: HTTP {r.status_code}")
        except Exception as e:
            print(f"ERROR  {sym}: {e}")

if __name__ == "__main__":
    main()
