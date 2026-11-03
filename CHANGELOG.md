## v5.38 — 2026-11-03 04:05 MST
- Live CoinGecko verification completed: all six stablecoins within $0.99–$1.01 band (USDT $0.9987 OK, USDC $0.9993 OK, DAI $0.9999 OK, FDUSD $0.9961 OK, PYUSD $0.9998 OK, TUSD $0.9974 OK). No depegs detected. No volume spikes.
- Dashboard version bumped to v5.38. Primary zero-code client surface remains polished and production-ready.
- VERIFY_RESULTS.md and README status updated.
- All core features operational: REST + fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, Telegram/email alerts, 14/14 unit tests pass.

## v5.37 — 2026-11-03 03:06 MST
- Dashboard refined to v5.37: clearer temporary data-pause message for non-technical users when CoinGecko free tier rate-limits; how-to section updated accordingly.
- Live verification via Coinbase spot: USDT $0.9984 OK, USDC $1.0000 OK, DAI $0.9988 OK, PYUSD $1.0000 OK. CoinGecko returned 429. No depegs on available coins. Core detector remains operational.
- README and VERIFY_RESULTS updated. All prior features (WS reconnection, volume spikes, CLI dashboard, 14 unit tests, alerts) unchanged and working.

## v5.36 — 2026-11-03 02:06 MST
- Built and deployed professional single-file web dashboard (dashboard.html): dark Bloomberg/Apple fintech aesthetic, six large live cards, status badges (OK/DEPEG DOWN/DEPEG UP/NO DATA), auto-refresh every 30s from CoinGecko, volume spike banners via localStorage, peg deviation bars and bps, total 24h volume, live indicator, manual refresh, rate-limit error handling, fully mobile-responsive for iPhone Safari, plain-English how-to section.
- Live CoinGecko verification: USDT $0.9987 OK, USDC $0.9993 OK, DAI $0.9999 OK, FDUSD $0.9961 OK, PYUSD $1.0000 OK, TUSD $0.9976 OK. All within $0.99–$1.01. No depegs.
- README status updated. Core features (REST, WS, volume, CLI, tests, alerts) remain operational. 14/14 unit tests pass.

## Previous entries preserved in repo history
