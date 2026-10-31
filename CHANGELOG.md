## v2.0 — 2026-10-31
- Expanded dashboard to 8 stablecoins: added Ethena USDe and USDD.
- Added peg deviation display in basis points on every card.
- Added one-click "Copy summary" button for quick status sharing.
- Updated how-to text and version footer.
- API endpoint expanded to cover the new coins.
- All prior features retained: health bar, sparklines, volume spikes, rate-limit resilience, mobile-responsive.

# Changelog

## 2026-10-30 (20:10 MDT)
- Dashboard polished to v1.9: refined card padding, larger price display, improved peg-bar safe-zone contrast, version bump.
- Live verification (fallback sources due to CoinGecko rate limit): all six stablecoins within $0.99–$1.01 band. No depegs.
- All core features operational. Unit tests 14/14 passing.
- Commit: feat: dashboard v1.9 polish — refined spacing, price scale, peg visualization


## 2026-10-30 (21:03 MDT / 03:03 UTC next day)
- Fresh live verification via DefiLlama (CoinGecko free tier rate-limited): all six stablecoins within $0.99–$1.01 (USDT $0.9992, USDC $0.9999, DAI $1.0004, FDUSD $0.9975, PYUSD $1.0003, TUSD $0.9988). No depegs or volume spikes.
- All core features operational: REST + fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, professional zero-code dashboard.html (v1.9), unit tests (14/14).
- Commit: docs: fresh live verification 21:03 MDT - all stablecoins OK within band

## 2026-10-30 (20:05 MDT / 02:05 UTC next day)
- Fresh live verification via CoinGecko free API (with DefiLlama fallback on rate limit): all six stablecoins within $0.99–$1.01 (USDT $0.9991, USDC $0.9998, DAI $1.0000, FDUSD $0.9973, PYUSD $1.0000, TUSD $0.9987). No depegs or volume spikes.
- Polished dashboard.html to v1.9: refined card hover, improved banner contrast, stronger health stats, enhanced mobile padding, version bump.
- All core features operational: REST + fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, professional zero-code dashboard.html (v1.9), unit tests (14/14).
- Commit: feat: polish dashboard to v1.9 and update live verification status

## 2026-10-30 (19:05 MDT / 01:05 UTC next day)
- Fresh live verification via CoinGecko free API: all six stablecoins within $0.99–$1.01 (USDT $0.9991, USDC $0.9998, DAI $1.0000, FDUSD $0.9973, PYUSD $1.0000, TUSD $0.9986). No depegs or volume spikes.
- All core features operational: REST + fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, professional zero-code dashboard.html (v1.7), unit tests (14/14).
- Commit: docs: fresh live verification 19:05 MDT - all stablecoins OK within band

## Earlier entries preserved below (see full history in repo)
