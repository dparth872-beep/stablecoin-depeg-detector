# Changelog

## 2026-10-30 (06:08 MDT / 12:08 UTC)
- Fresh live verification via CoinGecko free API: all six stablecoins within $0.99–$1.01 (USDT $0.9991, USDC $0.9997, DAI $1.0000, FDUSD $0.9975, PYUSD $1.0000, TUSD $0.9989). No depegs or volume spikes.
- Updated VERIFY_RESULTS.md with current snapshot.
- All core features operational: REST + fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, professional zero-code dashboard.html, unit tests (14/14).

## 2026-10-30 (05:07 MDT / 11:07 UTC)
- Polished dashboard.html further: added overall health bar (OK/alerts counts), market cap display, dynamic peg-bar marker scaled to $0.98–$1.02, client-side price sparklines (localStorage), relative timestamps, local recent alerts log, depeg pulse animation, improved typography and spacing.
- Live verification at ~05:07 MDT: all six stablecoins within $0.99–$1.01 (USDT $0.9991, USDC $0.9996, DAI $1.0000, FDUSD $0.9972, PYUSD $1.0000, TUSD $0.9989). No depegs or volume spikes.
- Commits: feat: polish web dashboard... ; docs: update status...

## 2026-10-30 (04:08 UTC / ~22:08 MDT prior day)
- Replaced stub dashboard.html with full production-grade single-file client dashboard: dark fintech aesthetic (Bloomberg-meets-Apple), six large cards with live price / 24h change / status badge / peg bar, volume spike banners (localStorage median baseline), rate-limit resilience (last-good-data), auto-refresh every 30s via CoinGecko free API, mobile-responsive, plain-English how-to. Zero-code surface ready for clients.
- Commit: feat: production-grade zero-code web dashboard

## 2026-10-30 (early morning verification)
- Fresh live snapshot at ~03:07 MDT: all six stablecoins within $0.99–$1.01 (USDT $0.9985, USDC $1.0000, DAI $1.0000, FDUSD $0.9970, PYUSD $1.0000, TUSD $0.9984). No depegs.
- Confirmed detector snapshot, fallbacks, and 14/14 unit tests pass.
- Dashboard polish: refined peg-bar scaling to the $0.99–$1.01 band, added subtle initial loading state, version footer, and clearer rate-limit resilience messaging.
- Updated VERIFY_RESULTS.md and README status.

## 2026-10-30 (prior)
- Live verification at 01:08 / 02:06 MDT: all six stablecoins within band. No depegs or volume spikes.
- Updated README status and VERIFY_RESULTS.md.
- Confirmed 14/14 unit tests pass.
- Dashboard remains the primary zero-code client surface (polished dark fintech aesthetic).

## Earlier
- WebSocket (Binance combined stream + Coinbase ticker) with exponential backoff reconnection.
- Volume anomaly detection (3x median baseline, cooldown).
- CLI live dashboard.
- Multi-source price fallbacks (CoinGecko, Coinbase, DefiLlama).
- Professional single-file HTML dashboard as primary zero-code client surface.
- Telegram + email alerts.
