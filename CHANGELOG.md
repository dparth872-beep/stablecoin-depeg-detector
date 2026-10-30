# Changelog

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
