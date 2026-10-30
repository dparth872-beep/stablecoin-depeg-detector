# Changelog

## 2026-10-30
- Live verification at 01:08 MDT: all six stablecoins within $0.99–$1.01 (USDT $0.9987, USDC $0.9993, DAI $1.0000, FDUSD $0.9965, PYUSD $0.9980, TUSD $0.9975). No depegs or volume spikes.
- Updated README status and VERIFY_RESULTS.md with current prices.
- Confirmed 14/14 unit tests pass.
- Dashboard remains the primary zero-code client surface (polished dark fintech aesthetic).

## Prior (same day)
- Polished dashboard.html: added summary stats (OK / Depegs / No Data / Avg BPS), median-based volume spike detection, depeg card pulse animation, refined mobile layout.

## Earlier
- WebSocket (Binance combined stream + Coinbase ticker) with exponential backoff reconnection.
- Volume anomaly detection (3x median baseline, cooldown).
- CLI live dashboard.
- Multi-source price fallbacks (CoinGecko, Coinbase, DefiLlama).
- Professional single-file HTML dashboard as primary zero-code client surface.
- Telegram + email alerts.
