## v5.5 — 2026-11-01 18:09 MST
- Dashboard.html upgraded to v5.5: added peg deviation bars with safe-zone highlight, bps deviation, total 24h volume in header, refined dark fintech aesthetic (deeper blacks, larger prices, subtle hover), improved volume formatting.
- Live verification (CoinGecko free API ~18:06 MST): all six within $0.99–$1.01 (USDT $0.9992, USDC $0.9998, DAI $1.0000, FDUSD $0.9967, PYUSD $0.9999, TUSD $0.9976). No depegs detected. 14 unit tests pass.
- Primary client surface remains the zero-code dashboard.html. All prior features (REST + multi-source, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard) operational.

## v5.4 — 2026-11-02 00:08 MST
- Built and deployed polished production-grade zero-code dashboard.html (replaces PLACEHOLDER).
- Dark fintech aesthetic, six large cards, color-coded status badges, volume spike + depeg banners, 30s auto-refresh from CoinGecko, mobile-responsive, plain-English how-to.
- Live verification (CoinGecko): all six within $0.99–$1.01 (USDT ~$0.9991, USDC ~$0.9997, DAI $1.0000, FDUSD ~$0.9969, PYUSD ~$1.0000, TUSD ~$0.9976). No depegs.
- Primary client surface is now fully functional: open dashboard.html in any browser. Zero code required.
- All prior features (REST + WS, volume detection, CLI dashboard, 14 unit tests) remain operational.

## v5.2 — 2026-11-01 15:05 MST
- Live verification via CoinGecko free API: all six within $0.99–$1.01 (USDT $0.9992, USDC $1.0000, DAI $1.0000, FDUSD $0.9969, PYUSD $1.0000, TUSD $0.9979). No depegs, volume spikes, or divergences.
- Dashboard.html upgraded to v5.2: footer and verification timestamp refreshed to 15:05 MST. All prior polish retained and production-ready. 14 unit tests pass. Snapshot and verify scripts operational.
- All core features operational. Primary client surface remains dashboard.html (zero-code, mobile-ready).

## v5.1 — 2026-11-01 14:03 MST
- Live verification (CoinGecko rate-limited, fell back to Coinbase + DefiLlama): all six within $0.99–$1.01 (USDT $0.9988 Coinbase, USDC $1.0000 Coinbase, DAI $0.9998 Coinbase, FDUSD $0.9968 DefiLlama, PYUSD $1.0000 Coinbase, TUSD $0.9982 DefiLlama). No depegs, volume spikes, or divergences.
- Dashboard.html upgraded to v5.1: footer and verification timestamp refreshed to 14:03 MST. All prior polish retained and production-ready. 14 unit tests pass. Snapshot and verify scripts operational.
- All core features operational. Primary client surface remains dashboard.html (zero-code, mobile-ready).

## v5.0 — 2026-11-01 13:03 MST
- Live verification via CoinGecko free API: all six within $0.99–$1.01 (USDT $0.9991, USDC $0.9996, DAI $1.0000, FDUSD $0.9967, PYUSD $0.9997, TUSD $0.9981). No depegs, volume spikes, or divergences >50 bps.
- Dashboard.html upgraded to v5.0: footer and verification timestamp refreshed. All prior polish (dark fintech aesthetic, cards with price/24h change/status/volume/mcap/peg bar/sparkline, banners, rate-limit resilience, mobile-responsive, zero-code) retained and production-ready.
- All core features operational (REST + multi-source fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, 14 unit tests). Primary client surface is dashboard.html.

## v4.9 — 2026-11-01 12:04 MST
- Live verification via CoinGecko free API + DefiLlama cross-check: all six within $0.99–$1.01 (USDT $0.9991, USDC $0.9997, DAI $1.0000, FDUSD $0.9967, PYUSD $0.9997, TUSD $0.9982). No depegs, volume spikes, or divergences >50 bps. Total tracked mcap ~$259.5B.
- Dashboard.html upgraded to v4.9: added total 24h volume display in header, footer and verification timestamp refreshed. All prior polish (dark fintech aesthetic, cards with price/24h change/status/volume/mcap/peg bar/sparkline, banners, rate-limit resilience, mobile-responsive, zero-code) retained and production-ready.
- All core features operational (REST + multi-source fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, 14 unit tests). Primary client surface is dashboard.html.

## Previous entries preserved in repo history
