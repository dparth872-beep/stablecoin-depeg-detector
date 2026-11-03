## v5.29 — 2026-11-02 19:03 MST
- Professional web dashboard (dashboard.html) confirmed and polished as primary zero-code client surface: dark Bloomberg/Apple fintech aesthetic (Inter + JetBrains Mono), six large live cards with big monospaced prices, status badges (OK / DEPEG DOWN / DEPEG UP / NO DATA) with color coding, 24h change, volume, peg deviation bars with safe-zone highlight, bps, total 24h volume, volume spike and depeg banners, live indicator, auto-refresh every 30s, manual Refresh now button, rate-limit error banner with auto-retry, mobile-responsive for iPhone Safari, plain-English how-to. Version bumped to v5.29.
- Live CoinGecko verification completed: all six stablecoins within $0.99–$1.01 band (USDT $0.9987, USDC $0.9993, DAI $1.0000, FDUSD $0.9957, PYUSD $0.9998, TUSD $0.9988). No depegs or volume spikes detected.
- All prior features operational: REST + multi-source fallbacks, Binance/Coinbase WS with exponential-backoff reconnection, volume anomaly detection, CLI dashboard, Telegram/email alerts, 14/14 unit tests pass.

## v5.28 — 2026-11-02 18:05 MST
- Live CoinGecko verification completed: all six stablecoins within $0.99–$1.01 band (USDT $0.9987, USDC $0.9993, DAI $0.9999, FDUSD $0.9958, PYUSD $0.9999, TUSD $0.9988). No depegs or volume spikes detected.
- Unit tests confirmed: 14/14 pass covering depeg thresholds, volume spikes (median/cooldown), divergence, boundaries, and multi-coin.
- Dashboard.html remains the primary zero-code client surface (dark fintech aesthetic, live cards, status badges, peg bars, volume spike banners, auto-refresh 30s, mobile-responsive for iPhone Safari).
- All prior features operational: REST + multi-source fallbacks, Binance/Coinbase WS with exponential-backoff reconnection, volume anomaly detection, CLI dashboard, Telegram/email alerts.

## v5.27 — 2026-11-02 16:05 MST
- Dashboard.html upgraded to v5.27: added live pulsing indicator, overall peg status summary (All N within peg / X DEPEG), total 24h volume display, peg deviation in bps, visual peg bar with safe-zone highlight and marker, manual Refresh now button, improved error handling with auto-retry on rate limits, refined typography and spacing. Still pure client-side, zero-code, mobile-responsive for iPhone Safari.
- Live CoinGecko verification: all six coins within $0.99–$1.01 (USDT $0.998586, USDC $0.999268, DAI $0.999841, FDUSD $0.995685, PYUSD $0.999837, TUSD $0.997695). No depegs.
- README status updated. All prior features (REST + multi-source fallbacks, Binance/Coinbase WS with reconnection, volume anomaly detection, CLI dashboard, 14 unit tests) operational.

## Previous entries preserved in repo history
