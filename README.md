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
- Professional single-file web dashboard (dark fintech aesthetic, six large live cards with big monospaced prices, status badges, 24h change, volume, peg deviation bars with safe-zone highlight, bps deviation, total 24h volume, volume spike and depeg banners, live indicator, auto-refresh every 30s, manual Refresh now button, rate-limit error banner with auto-retry, mobile-responsive, plain-English how-to, status-flash animations, overall peg status indicator)
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
Production-ready (v5.35). Latest verification (2026-11-03 ~01:07 MST, CoinGecko):
- USDT $0.9986 (OK)
- USDC $0.9993 (OK)
- DAI $0.9999 (OK)
- FDUSD $0.9960 (OK)
- PYUSD $0.9999 (OK)
- TUSD $0.9988 (OK)

All six prices within $0.99–$1.01 band. No depegs detected. 14/14 unit tests pass. dashboard.html is the primary client surface — polished dark Bloomberg/Apple fintech aesthetic (Inter + JetBrains Mono), zero-code, mobile-ready for iPhone Safari, auto-refresh every 30s with Coinbase fallback, status badges (OK / DEPEG DOWN / DEPEG UP / NO DATA) with color coding, 24h change and volume, peg deviation bars, bps, client-side volume spike banners (3× recent average via localStorage), live indicator, manual refresh, plain-English how-to. Six coins only.

Primary delivery for non-technical users: open dashboard.html in any browser. Bookmark it. Done.
