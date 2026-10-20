# Stablecoin Depeg Detector v2

Real-time stablecoin peg monitor with three signal tiers: price depegs, volume spikes, and cross-source price divergence. Built for funds, prop desks, and fintech treasury teams who need lead time when billions move.

## Why this exists

Stablecoin depegs cascade into billions in losses within hours (USDC/SVB March 2023, UST May 2022). The free tools are basic. The institutional suites (TRM, Elliptic, Range) are compliance-priced. This sits in the gap: fast, cheap, trader-grade depeg intelligence.

## Quick start

```bash
pip install -r requirements.txt
cp config.json.example config.json   # optional: enable Telegram/email
python depeg_detector.py                      # single snapshot (CoinGecko REST)
python depeg_detector.py --loop 30            # poll every 30 seconds
python depeg_detector.py --dashboard          # live refreshing CLI board with colors
python depeg_detector.py --ws                 # Binance WebSocket tick-by-tick with auto-reconnect + heartbeat
python verify_prices.py                       # one-shot verification with 24h vol/change
python tests/test_depeg_logic.py              # run unit tests (13 cases)
```

## Signals

| Tier | Trigger | Meaning |
| --- | --- | --- |
| DEPEG | Price outside $0.99-$1.01 | Peg break - incident mode |
| VOLUME SPIKE | 24h vol > 3x median baseline | Liquidity stress building |
| DIVERGENCE | Cross-venue gap > 50 bps | One source is stale or manipulated |

## Alerts

- Console (always on) + live CLI dashboard (price, 24h change, volume, colored status, timestamp)
- Telegram bot
- Email via SMTP

## Tracked stablecoins

USDT, USDC, DAI, FDUSD, PYUSD, TUSD via CoinGecko free tier (no API key). Binance combined ticker stream for live mode on available pairs (usdcusdt, daiusdt, fdusdusdt, pyusdusdt, tusdusdt). USDT uses REST fallback.

## Verification

Live check (2026-10-20): CoinGecko returned all six within band after rate-limit handling:
- USDT ~$0.9992 OK
- USDC ~$0.9998 OK
- DAI ~$1.0000 OK
- FDUSD ~$0.9982 OK
- PYUSD ~$1.0000 OK
- TUSD ~$0.9987 OK

All 13 unit tests pass. Multi-source REST prefers CoinGecko, falls back to Coinbase on rate limits. Volume tracker uses pure median for outlier-robust baseline.

## Features

- Robust price verification with CoinGecko retry + Coinbase fallback
- Binance WebSocket with exponential backoff reconnection (capped at 60s), heartbeat/stale detection, serverShutdown handling, and connection logging
- Volume anomaly detection using pure median baseline (skips zero volumes, clear spike alerts) as independent alert tier
- In-place refreshing CLI dashboard with ANSI colors (green OK / red DEPEG), timestamp, volume, and status
- 13 unit tests covering threshold logic, volume spikes (including median robustness), divergence, multi-coin, and edge cases with synthetic data
- Multi-source REST snapshot with Coinbase fallback for rate-limit resilience

## Sales pitch

**Who to sell to:** small funds, prop desks, DeFi treasuries, and fintechs holding stablecoin reserves. Distribution = selling to people already swimming in stablecoin volume. First clients: teams who need reliable, low-latency alerts without enterprise procurement. Target $200-500/month.

**Why minutes matter:** A depeg can move from 50 bps to 5% in under an hour (see March 2023 USDC). Early detection of volume spikes or price drift gives desks time to rotate or hedge before cascade liquidations. This tool is the trader-grade tier between free GitHub scripts and $50k+ institutional compliance suites. Minutes of lead time prevent millions in losses.

## Upgrade path

1. Live Binance/Coinbase WebSocket with auto-reconnect and heartbeat (implemented)
2. On-chain mint/burn monitoring via Alchemy or QuickNode
3. Hosted dashboard + multi-tenant alerts
4. Paid tier with custom thresholds per client

## License

MIT
