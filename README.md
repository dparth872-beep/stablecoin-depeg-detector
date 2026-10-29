# Stablecoin Depeg Detector

Real-time stablecoin peg monitor for funds, prop desks, and fintech teams.

**Stablecoin Depeg Intelligence** — minutes matter when a peg breaks.

## Why this exists

Stablecoin depegs (USDT, USDC, DAI, etc.) have wiped out billions. Most tools are either free-and-slow or institutional-and-expensive. This sits in the gap: fast, cheap, trader-grade signals with a zero-code dashboard a non-technical buyer can open in a browser.

Sell to people already swimming in stablecoin volume. First client = a few hundred $/month. Distribution is the product.

## Signals

| Tier | Trigger | Meaning |
|------|---------|---------|
| DEPEG | Price outside $0.99–$1.01 | Peg break — incident mode |
| VOLUME SPIKE | 24h vol > 3x recent median baseline | Liquidity stress building |
| DIVERGENCE | Cross-venue gap > 50 bps | One source is stale or manipulated |

## Quick start

### Zero-code (recommended for clients)
1. Download `dashboard.html`
2. Open it in any modern browser (including iPhone Safari)
3. Bookmark it. Done.

No install. No login. No code.

### Technical
```bash
pip install -r requirements.txt
cp config.json.example config.json   # optional Telegram/email
python depeg_detector.py              # one-shot snapshot
python depeg_detector.py --json       # structured JSON
python depeg_detector.py --loop 30    # poll every 30s
python depeg_detector.py --dashboard  # live CLI board
python depeg_detector.py --ws         # Binance WebSocket
python depeg_detector.py --ws-coinbase # Coinbase WebSocket (recommended fallback)
python verify_prices.py               # multi-source verification
python tests/test_depeg_logic.py      # 14 unit tests
```

## Features
- CoinGecko REST with Coinbase + DefiLlama fallbacks
- Binance and Coinbase WebSocket streams with exponential-backoff reconnection
- Volume anomaly detection (median baseline, cooldown)
- CLI dashboard that refreshes in place
- Professional single-file web dashboard (dark fintech aesthetic with radial gradient, six large live cards, status badges with glow, overall health bar, bps-from-peg indicators, visual peg deviation bar with $1.00 center mark, price sparklines, volume spike + Coinbase divergence banners, price flash animation, localStorage volume + price history, market cap display, auto-refresh every 30s, manual refresh button, relative timestamps, mobile-responsive, plain-English how-to, rate-limit resilience that keeps last good data, subtle alert card glow, local recent alerts log)
- Telegram + email alerts (config.json)
- JSON output for integration
- Comprehensive unit tests

## Tracked coins
USDT, USDC, DAI, FDUSD, PYUSD, TUSD

## Sales pitch
Target: prop desks, market makers, fintech ops teams, funds with stablecoin exposure.
Pitch: “When a stablecoin depegs, every minute costs money. This gives you a clean, always-on view and alerts without the six-figure compliance suite.”
Price: $300–$800/month for the first few clients. Dashboard is the demo that closes.

## Status
Production-ready. Live verification (2026-10-29 ~16:10 MDT via DefiLlama + Coinbase fallbacks; CoinGecko free tier currently rate-limited): 
- USDT $0.9987 (OK)
- USDC $0.9992 (OK)
- DAI $0.9998 (OK)
- FDUSD $0.9964 (OK)
- PYUSD $0.9985 (OK)
- TUSD $0.9985 (OK)

All within $0.99–$1.01 band. No depegs. No volume spikes detected. 14/14 unit tests pass. dashboard.html (v6.8) is the primary client surface — polished dark fintech aesthetic (Bloomberg-meets-Apple), zero-code, mobile-ready, with volume spike and cross-source divergence banners, status glow, market cap, peg bar center mark, monospaced prices, price sparklines, relative timestamps, alert card highlight, local recent alerts log, plus graceful handling of free-tier rate limits.

Primary delivery for non-technical users: open dashboard.html in any browser. Bookmark it. Done.
