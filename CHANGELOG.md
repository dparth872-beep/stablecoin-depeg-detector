## v5.97 — 2026-11-07 ~15:07 MST
- Restored full polished single-file dashboard.html after placeholder regression. Dark Bloomberg/Apple fintech aesthetic: six large cards (USDT, USDC, DAI, FDUSD, PYUSD, TUSD) with big monospaced prices, status badges (OK / DEPEG DOWN / DEPEG UP / NO DATA), 24h change, volume, color-coded accent bars, auto-refresh every 30s via CoinGecko free API, last-updated timestamp, volume/divergence banners, mobile-responsive, plain-English how-to section. Zero-code: open in any browser.
- Live verification (CoinGecko): all six within $0.99–$1.01 (USDT ~0.9991 OK, USDC ~0.9997 OK, DAI 1.0000 OK, FDUSD ~0.9969 OK, PYUSD 1.0000 OK, TUSD ~0.9984 OK). No depegs.
- All prior features (REST + Coinbase/DefiLlama fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, Telegram/email, 14 unit tests) remain operational.

## v5.96 — 2026-11-07 ~14:05 MST
- Live verification (CoinGecko primary): all six stablecoins within $0.99–$1.01 band (USDT $0.9992 OK, USDC $0.9996 OK, DAI $1.0000 OK, FDUSD $0.9969 OK, PYUSD $1.0000 OK, TUSD $1.0000 OK). No depegs detected. No volume spikes or divergences.
- Dashboard upgraded to v5.96: added client-side price sparklines (localStorage history, last 20 samples, canvas mini-charts on each card), status-colored top accent bars on cards, refined spacing and hover. DefiLlama fallback and Coinbase cross-check retained. Professional single-file HTML dashboard remains the primary zero-code product.
- 14/14 unit tests pass. All core features (REST + fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, Telegram/email alerts, professional web dashboard) operational.

## v5.95 — 2026-11-07 ~13:06 MST
- Live verification (CoinGecko primary): all six stablecoins within $0.99–$1.01 band (USDT $0.9992 OK, USDC $0.9997 OK, DAI $1.0000 OK, FDUSD $0.9971 OK, PYUSD $1.0000 OK, TUSD $0.9984 OK). No depegs detected. No volume spikes or divergences.
- Dashboard version bumped to v5.95. Updated last-verified timestamp and current prices in footer. DefiLlama fallback and Coinbase cross-check retained. Professional single-file HTML dashboard remains the primary zero-code product.
- 14/14 unit tests pass. All core features (REST + fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, Telegram/email alerts, professional web dashboard) operational.

## Previous entries preserved in repo history
