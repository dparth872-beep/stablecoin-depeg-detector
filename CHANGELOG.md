# Changelog

## 2026-10-30
- Polished dashboard.html: added summary stats (OK / Depegs / No Data / Avg BPS), median-based volume spike detection, depeg card pulse animation, refined mobile layout.
- Updated README with latest live verification (all six coins OK, no alerts).
- Confirmed 14/14 unit tests pass.

## Prior
- WebSocket (Binance combined stream + Coinbase ticker) with exponential backoff reconnection.
- Volume anomaly detection (3x median baseline, cooldown).
- CLI live dashboard.
- Multi-source price fallbacks (CoinGecko, Coinbase, DefiLlama).
- Professional single-file HTML dashboard as primary zero-code client surface.
- Telegram + email alerts.
