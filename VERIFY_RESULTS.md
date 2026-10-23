# Verification Results

**Timestamp:** 2026-10-22 18:05 MDT

## Live Multi-Source Snapshot

CoinGecko free API returned 429 (rate limited). Using Coinbase spot + DefiLlama (CoinGecko-sourced) fallbacks.

### Coinbase Spot
- USDT-USD: $0.998725
- USDC-USD: $1.000000
- DAI-USD: $0.999781
- PYUSD-USD: $1.000000

### DefiLlama (coingecko:*)
- USDT: $0.998939
- USDC: $0.999519
- DAI: $1.000026
- FDUSD: $0.997091
- PYUSD: $1.000035
- TUSD: $0.997908

**All six coins within $0.99–$1.01 band. No depeg alerts. No volume spikes or divergences observed in this snapshot.**

Threshold logic verified via `python tests/test_depeg_logic.py` → 14/14 PASS.

WebSocket clients (Binance combined ticker stream + Coinbase ticker channel) present with exponential backoff reconnection.

Volume anomaly detection uses rolling median baseline with cooldown.

CLI dashboard (`--dashboard`) and JSON output (`--json`) operational.

Primary client surface: `dashboard.html` (v1.3) — dark fintech aesthetic, mobile-responsive, localStorage alerts, Coinbase divergence checks, volume banners, sparklines, health summary. Zero-code: open in any browser.

Last verified by autonomous agent at 18:05 MDT on 2026-10-22.
