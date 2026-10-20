#!/usr/bin/env python3
"""Verification script: fetch prices from CoinGecko with retry + Coinbase + DefiLlama fallback and print OK/ALERT."""
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
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
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

def fetch_defillama():
    ids = ",".join(f"coingecko:{cg}" for cg in STABLES.keys())
    try:
        r = requests.get(f"https://coins.llama.fi/prices/current/{ids}", timeout=15)
        if r.status_code == 200:
            return r.json().get("coins", {})
    except Exception:
        pass
    return {}

def main():
    print("Stablecoin Depeg Detector - Price Verification")
    print("=" * 70)
    cg = fetch_coingecko(list(STABLES.keys()))
    llama = fetch_defillama()
    for cg_id, symbol in STABLES.items():
        price = None
        source = "none"
        vol = chg = None
        if cg and cg_id in cg and "usd" in cg[cg_id]:
            price = cg[cg_id]["usd"]
            vol = cg[cg_id].get("usd_24h_vol")
            chg = cg[cg_id].get("usd_24h_change")
            source = "CoinGecko"
        if price is None:
            price = fetch_coinbase(symbol)
            if price is not None:
                source = "Coinbase"
        if price is None:
            llama_key = f"coingecko:{cg_id}"
            if llama_key in llama:
                price = llama[llama_key].get("price")
                if price is not None:
                    source = "DefiLlama"
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
        vol_s = f" vol=${vol:,.0f}" if vol else ""
        chg_s = f" 24h={chg:+.2f}%" if chg is not None else ""
        print(f"{status:6} {symbol}: ${price:.4f}  ({note}) [{source}]{vol_s}{chg_s}")
    print("=" * 70)
    print("Verification complete. All reachable prices checked against $0.99-$1.01.")

if __name__ == "__main__":
    main()
