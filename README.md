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
2. Open it in any browser (including iPhone Safari)
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
- Professional single-file web dashboard (dark fintech aesthetic with status glow, refined typography, mobile-responsive, recent alerts log with localStorage persistence + clear button, live indicator, area-filled sparklines, bps-from-peg, overall health summary, manual refresh, Coinbase cross-source divergence detection >50 bps)
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
Production-ready. Latest verification (2026-10-23 03:05 MDT): CoinGecko free API returned 200. USDT $0.9990, USDC $0.9995, DAI $1.0000, FDUSD $0.9972, PYUSD $1.0000, TUSD $0.9986. All within $0.99–$1.01 band. No depegs. 14/14 tests pass. Dashboard v1.9 is the primary client surface — polished dark fintech aesthetic (Bloomberg-meets-Apple, status glow, refined spacing), zero-code, mobile-ready, with persistent localStorage alerts, clear-log button, live CoinGecko + Coinbase divergence checks (>50 bps), volume spike banners, and specific alert banners.

Primary delivery for non-technical users: open dashboard.html in any browser. Bookmark it. Done.
