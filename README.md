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
python depeg_detector.py --dashboard          # live refreshing CLI board
python depeg_detector.py --ws                 # Binance WebSocket tick-by-tick with auto-reconnect
python verify_prices.py                       # one-shot verification with fallbacks
python tests/test_depeg_logic.py              # run unit tests
```

## Signals

| Tier | Trigger | Meaning |
| --- | --- | --- |
| DEPEG | Price outside $0.99-$1.01 | Peg break - incident mode |
| VOLUME SPIKE | 24h vol > 3x rolling avg | Liquidity stress building |
| DIVERGENCE | Cross-venue gap > 50 bps | One source is stale or manipulated |

## Alerts

- Console (always on) + live CLI dashboard (price, 24h change, volume, status, timestamp)
- Telegram bot
- Email via SMTP

## Tracked stablecoins

USDT, USDC, DAI, FDUSD, PYUSD, TUSD via CoinGecko free tier (no API key). Binance combined ticker stream for live mode on available pairs (usdcusdt, daiusdt, fdusdusdt, pyusdusdt, tusdusdt). USDT uses REST fallback.

## Verification

Live check (2026-10-20 05:03 UTC): CoinGecko returned 200. All six within band:
- USDT $0.9992 OK (24h vol ~$46.8B)
- USDC $0.9999 OK (24h vol ~$16.5B)
- DAI $1.0000 OK (24h vol ~$341M)
- FDUSD $0.9974 OK (24h vol ~$63M)
- PYUSD $1.0000 OK (24h vol ~$63M)
- TUSD $0.9987 OK (24h vol ~$14M)
All 11 unit tests pass. Multi-source REST prefers CoinGecko, falls back to Coinbase on rate limits.

## Features

- Robust price verification with CoinGecko retry + Coinbase fallback
- Binance WebSocket with exponential backoff reconnection (capped at 60s) and connection logging
- Volume anomaly detection (skips zero volumes, clear spike alerts) as independent alert tier
- In-place refreshing CLI dashboard with timestamp, volume, and status
- 11 unit tests covering threshold logic, volume spikes, divergence, and edge cases with synthetic data
- Multi-source REST snapshot with Coinbase fallback for rate-limit resilience

## Sales pitch

**Who to sell to:** small funds, prop desks, DeFi treasuries, and fintechs holding stablecoin reserves. Distribution = selling to people already swimming in stablecoin volume.

**Why minutes matter:** A depeg can move from 50 bps to 5% in under an hour (see March 2023 USDC). Early detection of volume spikes or price drift gives desks time to rotate or hedge before cascade liquidations. This tool is the $200-500/month tier between free GitHub scripts and $50k+ institutional compliance suites. First clients: teams who need reliable, low-latency alerts without enterprise procurement.

## Upgrade path

1. Live Binance/Coinbase WebSocket with auto-reconnect (implemented)
2. On-chain mint/burn monitoring via Alchemy or QuickNode
3. Hosted dashboard + multi-tenant alerts
4. Paid tier with custom thresholds per client

## License

MIT
