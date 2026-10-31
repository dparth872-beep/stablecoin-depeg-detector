## v2.3 — 2026-10-31 05:06 MDT
- Fresh live verification via CoinGecko: all six within $0.99–$1.01 (USDT $0.9992, USDC $0.9999, DAI $1.0000, FDUSD $0.9976, PYUSD $1.0000, TUSD $0.9986). No depegs or volume spikes.
- 14/14 unit tests pass. All core features operational. Zero-code dashboard.html (v2.3) is the primary client surface.
- No code changes this cycle — status confirmation only.

## v2.3 — 2026-10-31 02:06 MDT
- Dashboard polish: added live status indicator (blinking green dot), version bump to v2.3.
- Fresh live verification via CoinGecko: all six within $0.99–$1.01 (USDT $0.9992, USDC $0.9999, DAI $1.0000, FDUSD $0.9976, PYUSD $1.0000, TUSD $0.9988). No depegs or volume spikes.
- All core features operational. Unit tests 14/14. Zero-code dashboard is the primary client surface.

## v2.1 — 2026-10-31 01:07 MDT
- Fresh live verification via CoinGecko: all six within $0.99–$1.01 (USDT $0.9992, USDC $0.9998, DAI $1.0000, FDUSD $0.9975, PYUSD $1.0000, TUSD $0.9981). No depegs or volume spikes.
- All core features operational. Unit tests 14/14. Zero-code dashboard is the primary client surface.

## v2.1 — 2026-10-31 00:05 MDT
- Fresh live verification via CoinGecko: all six within $0.99–$1.01 (USDT $0.9992, USDC $0.9999, DAI $1.0000, FDUSD $0.9975, PYUSD $1.0000, TUSD $0.9984). No depegs or volume spikes.
- All core features operational. Unit tests 14/14. Zero-code dashboard is the primary client surface.

## v2.1 — 2026-10-30 22:07 MDT
- Fixed critical JS syntax error in dashboard.html (nested function / broken addToLog).
- Restored exact six stablecoins (USDT, USDC, DAI, FDUSD, PYUSD, TUSD) per product spec.
- Fresh live verification via CoinGecko: all six within $0.99–$1.01 (USDT $0.9992, USDC $0.9999, DAI $1.0000, FDUSD $0.9974, PYUSD $1.0000, TUSD $0.9988). No depegs or volume spikes.
- All core features operational. Unit tests 14/14. Zero-code dashboard is the primary client surface.

## v2.0 — 2026-10-31
- Expanded dashboard to 8 stablecoins: added Ethena USDe and USDD. (reverted in v2.1)
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

## Earlier entries preserved below (see full history in repo)
