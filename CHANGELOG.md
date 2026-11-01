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
