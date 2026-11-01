## v3.7 — 2026-11-01 01:06 MDT
- Fresh live verification via CoinGecko free API: all six within $0.99–$1.01 (USDT $0.9995, USDC $1.0000, DAI $1.0000, FDUSD $0.9977, PYUSD $1.0000, TUSD $0.9992). No depegs or volume spikes.
- dashboard.html polished to v3.7 (footer updated with exact verification timestamp). Primary zero-code client surface remains production-ready.
- All core features (REST + WS, volume anomaly, CLI dashboard, unit tests, multi-source fallbacks) operational.

## Previous
## v3.6 — 2026-11-01 00:05 MDT
- Fresh live verification via DefiLlama: all six within $0.99–$1.01 (USDT $0.9995, USDC $1.0000, DAI $1.0005, FDUSD $0.9975, PYUSD $1.0001, TUSD $0.9992). No depegs or volume spikes.
- All core features operational. Primary client surface remains dashboard.html (v3.5/v3.6 polish: dark fintech aesthetic, zero-code, mobile-ready, rate-limit resilient with source indicator, peg bars, sparklines, banners).
- CoinGecko free API remains rate-limited for heavy polling; DefiLlama + Coinbase serve as reliable fallbacks in the Python detector.

## Earlier entries preserved below (see full history in repo)
