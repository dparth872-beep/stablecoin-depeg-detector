# Stablecoin Depeg Detector v3.2

Real-time stablecoin peg monitor with three signal tiers: price depegs, volume spikes, and cross-source price divergence. Built for funds, prop desks, and fintech treasury teams who need lead time when billions move.

## Zero-code product: Professional Web Dashboard

The primary user-facing deliverable is `dashboard.html` — a single-file, dark-themed, mobile-responsive dashboard with a modern fintech aesthetic (Bloomberg terminal meets clean product design).

- Open `dashboard.html` in any browser (Safari, Chrome, Firefox). No install, no login, no terminal.
- Six large cards (USDT, USDC, DAI, FDUSD, PYUSD, TUSD) showing live price (big bold), 24h change, volume, deviation in bps, mini sparklines from local history, and color-coded status badges (OK / DEPEG DOWN / DEPEG UP / NO DATA).
- Overall health bar at the top (ALL PEGGED / DEPEG count) plus total 24h volume across tracked coins.
- Auto-refreshes every 30 seconds via CoinGecko free API with automatic DefiLlama fallback on rate limits + manual Refresh now button + live countdown.
- Volume spike detection uses browser localStorage as a rolling baseline (3x median) — banner lists specific coins when triggered.
- Left-border color coding, status-change flash animation, refined spacing, tabular numbers, subtle hover, and peg deviation visual bar.
- Color legend for status meanings.
- Error banner for rate limits or network issues.
- Last-updated timestamp + data source indicator (CoinGecko / DefiLlama) in the corner.
- Version badge (v3.2).
- Plain-English “How to use” section at the bottom.

This is the demo you show a client on an iPhone or laptop. It looks like something a professional trading firm would be proud to present.

## Why this exists

Stablecoin depegs cascade into billions in losses within hours (USDC/SVB March 2023, UST May 2022). The free tools are basic. The institutional suites (TRM, Elliptic, Range) are compliance-priced. This sits in the gap: fast, cheap, trader-grade depeg intelligence.

## Quick start (technical)

```bash
pip install -r requirements.txt
cp config.json.example config.json   # optional: enable Telegram/email
python depeg_detector.py                      # single snapshot (CoinGecko REST)
python depeg_detector.py --json               # structured JSON snapshot for integration
python depeg_detector.py --loop 30            # poll every 30 seconds
python depeg_detector.py --dashboard          # live refreshing CLI board with colors
python depeg_detector.py --ws                 # Binance WebSocket (may be geo-restricted)
python depeg_detector.py --ws-coinbase        # Coinbase WebSocket (recommended fallback)
python verify_prices.py                       # one-shot verification with 24h vol/change
python tests/test_depeg_logic.py              # run unit tests (14 cases)
```

For non-technical users: just open dashboard.html.

## Signals

| Tier | Trigger | Meaning |
| --- | --- | --- |
| DEPEG | Price outside $0.99-$1.01 | Peg break - incident mode |
| VOLUME SPIKE | 24h vol > 2.5–3x median baseline (debounced / localStorage) | Liquidity stress building |
| DIVERGENCE | Cross-venue gap > 50 bps | One source is stale or manipulated |

## Alerts

- Professional web dashboard (zero-code, client-facing, localStorage volume baseline, overall health + total volume, error handling, bps deviation, sparklines, countdown, DefiLlama fallback, source indicator, color legend)
- Console + live CLI dashboard (price, 24h change, volume, colored status, timestamp)
- Telegram bot
- Email via SMTP
- JSON output (`--json`) for piping into dashboards, monitoring systems, or trading bots

## Tracked stablecoins

USDT, USDC, DAI, FDUSD, PYUSD, TUSD via CoinGecko free tier (no API key). Binance combined ticker stream for live mode on available pairs. Coinbase Exchange ticker for reliable tick-by-tick where Binance is blocked. DefiLlama as tertiary fallback for full coverage under rate limits.

## Verification

Live check (2026-10-21 ~22:03 UTC via CoinGecko):

- OK USDT $0.9995
- OK USDC $0.9998
- OK DAI $0.9996
- OK FDUSD $0.9984
- OK PYUSD $1.0000
- OK TUSD $0.9990

All six within $0.99-$1.01. All 14 unit tests pass. Multi-source REST prefers CoinGecko, falls back to Coinbase, then DefiLlama on rate limits. Dashboard auto-falls back to DefiLlama and shows source. Volume tracker uses pure median for outlier-robust baseline with cooldown. JSON snapshot mode confirmed. WebSocket reconnection with exponential backoff + jitter operational. Professional web dashboard live, polished, and client-ready with overall health indicator, total 24h volume, bps deviation, local sparklines, rate-limit resilience, source indicator, and color legend (v3.2).

## Features

- Professional single-file web dashboard (dashboard.html) — dark theme, mobile-responsive, auto-refresh + manual button + countdown, status badges, overall health bar + total volume, localStorage volume spikes with specific coin list, status animations, left-border coding, peg visual bar, bps deviation, mini sparklines, error handling, DefiLlama fallback, source indicator, color legend, version badge, zero-install
- Robust price verification with CoinGecko retry + Coinbase + DefiLlama fallback
- Binance WebSocket with exponential backoff + random jitter reconnection (capped at 60s), heartbeat, reconnect counting, and connection logging
- Coinbase WebSocket alternative for geo-restricted environments
- Volume anomaly detection using pure median baseline (skips zero volumes, clear spike alerts, debounce) as independent alert tier
- In-place refreshing CLI dashboard with ANSI colors (green OK / red DEPEG), timestamp, volume, and status
- Structured JSON snapshot mode (`--json`) for easy integration into external systems
- Unit tests covering threshold logic, volume spikes (including median robustness and cooldown), divergence, multi-coin, and edge cases with synthetic data
- Multi-source REST snapshot with Coinbase + DefiLlama fallback for rate-limit resilience

## Sales pitch

**Who to sell to:** small funds, prop desks, DeFi treasuries, OTC desks, and fintechs that already hold or clear large stablecoin volumes. Distribution = selling directly to people swimming in USDT/USDC flow. First clients: teams who need reliable sub-minute alerts without enterprise procurement cycles. Price point: a few hundred $/month.

**Why minutes matter:** USDC moved from ~$1.00 to $0.88 in hours during the March 2023 SVB event; UST collapsed in days. Volume spikes and early price drift give desks lead time to rotate, hedge, or pause transfers before cascade liquidations and redemption queues. This sits in the gap between free polling scripts and $50k+ institutional suites (TRM, Elliptic). Minutes of lead time prevent millions in losses. The web dashboard lets you show the product instantly on any device — open the file, show the cards, done.

## Upgrade path

1. Live Binance/Coinbase WebSocket with auto-reconnect, jitter, and heartbeat (implemented)
2. On-chain mint/burn monitoring via Alchemy or QuickNode
3. Hosted multi-tenant dashboard + custom alerts
4. Paid tier with custom thresholds per client

## License

MIT
