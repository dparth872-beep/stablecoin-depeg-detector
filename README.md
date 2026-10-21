# Stablecoin Depeg Detector v2

Real-time stablecoin peg monitor with three signal tiers: price depegs, volume spikes, and cross-source price divergence. Built for funds, prop desks, and fintech treasury teams who need lead time when billions move.

## Why this exists

Stablecoin depegs cascade into billions in losses within hours (USDC/SVB March 2023, UST May 2022). The free tools are basic. The institutional suites (TRM, Elliptic, Range) are compliance-priced. This sits in the gap: fast, cheap, trader-grade depeg intelligence.

## Quick start

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

## Signals

| Tier | Trigger | Meaning |
| --- | --- | --- |
| DEPEG | Price outside $0.99-$1.01 | Peg break - incident mode |
| VOLUME SPIKE | 24h vol > 3x median baseline (debounced) | Liquidity stress building |
| DIVERGENCE | Cross-venue gap > 50 bps | One source is stale or manipulated |

## Alerts

- Console (always on) + live CLI dashboard (price, 24h change, volume, colored status, timestamp)
- Telegram bot
- Email via SMTP
- JSON output (`--json`) for piping into dashboards, monitoring systems, or trading bots

## Tracked stablecoins

USDT, USDC, DAI, FDUSD, PYUSD, TUSD via CoinGecko free tier (no API key). Binance combined ticker stream for live mode on available pairs. Coinbase Exchange ticker for reliable tick-by-tick where Binance is blocked. DefiLlama as tertiary fallback for full coverage under rate limits.

## Verification

Live check (2026-10-21, CoinGecko direct):

- USDT $0.9991 OK [CoinGecko] vol=$50.99B 24h=-0.01%
- USDC $0.9997 OK [CoinGecko] vol=$15.04B 24h=-0.03%
- DAI $1.0000 OK [CoinGecko] vol=$160.9M 24h=-0.04%
- FDUSD $0.9980 OK [CoinGecko] vol=$103.8M 24h=+0.07%
- PYUSD $1.0010 OK [CoinGecko] vol=$50.8M 24h=+0.06%
- TUSD $0.9986 OK [CoinGecko] vol=$6.1M 24h=-0.01%

All 14 unit tests pass. Multi-source REST prefers CoinGecko, falls back to Coinbase, then DefiLlama on rate limits. Volume tracker uses pure median for outlier-robust baseline with 5-minute alert cooldown. JSON snapshot mode confirmed. WebSocket reconnection with exponential backoff + jitter operational.

## Features

- Robust price verification with CoinGecko retry + Coinbase + DefiLlama fallback
- Binance WebSocket with exponential backoff + random jitter reconnection (capped at 60s), heartbeat, reconnect counting, and connection logging
- Coinbase WebSocket alternative for geo-restricted environments
- Volume anomaly detection using pure median baseline (skips zero volumes, clear spike alerts, 300s debounce) as independent alert tier
- In-place refreshing CLI dashboard with ANSI colors (green OK / red DEPEG), timestamp, volume, and status
- Structured JSON snapshot mode (`--json`) for easy integration into external systems
- 14 unit tests covering threshold logic, volume spikes (including median robustness and cooldown), divergence, multi-coin, and edge cases with synthetic data
- Multi-source REST snapshot with Coinbase + DefiLlama fallback for rate-limit resilience

## Sales pitch

**Who to sell to:** small funds, prop desks, DeFi treasuries, OTC desks, and fintechs that already hold or clear large stablecoin volumes. Distribution = selling directly to people swimming in USDT/USDC flow. First clients: teams who need reliable sub-minute alerts without enterprise procurement cycles. Price point: a few hundred $/month.

**Why minutes matter:** USDC moved from ~$1.00 to $0.88 in hours during the March 2023 SVB event; UST collapsed in days. Volume spikes and early price drift give desks lead time to rotate, hedge, or pause transfers before cascade liquidations and redemption queues. This sits in the gap between free polling scripts and $50k+ institutional suites (TRM, Elliptic). Minutes of lead time prevent millions in losses.

## Upgrade path

1. Live Binance/Coinbase WebSocket with auto-reconnect, jitter, and heartbeat (implemented)
2. On-chain mint/burn monitoring via Alchemy or QuickNode
3. Hosted dashboard + multi-tenant alerts
4. Paid tier with custom thresholds per client

## License

MIT
