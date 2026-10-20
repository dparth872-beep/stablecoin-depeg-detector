# Stablecoin Depeg Detector v2

Real-time stablecoin peg monitor with three signal tiers: price depegs, volume spikes, and cross-source price divergence. Built for funds, prop desks, and fintech treasury teams who need lead time when billions move.

## Why this exists

Stablecoin depegs cascade into billions in losses within hours (USDC/SVB March 2023, UST May 2022). The free tools are basic. The institutional suites (TRM, Elliptic, Range) are compliance-priced. This sits in the gap: fast, cheap, trader-grade depeg intelligence.

## Quick start

```bash
pip install -r requirements.txt
python depeg_detector.py                      # single snapshot (CoinGecko REST)
python depeg_detector.py --loop 30            # poll every 30 seconds
python depeg_detector.py --dashboard          # live refreshing CLI board
python depeg_detector.py --ws                 # Binance WebSocket tick-by-tick with auto-reconnect
python verify_prices.py                       # one-shot verification with fallbacks
python tests/test_depeg_logic.py              # run unit tests
```

Copy `config.json.example` to `config.json` and fill Telegram/email if desired.

## Signals

| Tier | Trigger | Meaning |
| --- | --- | --- |
| DEPEG | Price outside $0.99-$1.01 | Peg break - incident mode |
| VOLUME SPIKE | 24h vol > 3x rolling avg | Liquidity stress building |
| DIVERGENCE | Cross-venue gap > 50 bps | One source is stale or manipulated |

## Alerts

- Console (always on) + color-coded CLI dashboard (price, 24h change, volume, status)
- Telegram bot
- Email via SMTP

## Tracked stablecoins

USDT, USDC, DAI, FDUSD, PYUSD, TUSD via CoinGecko free tier (no API key). Binance combined ticker stream for live mode on available pairs (usdcusdt, daiusdt, fdusdusdt, pyusdusdt, tusdusdt). USDT uses REST fallback.

## Verification

Live check (Oct 2026): USDT $0.9988, USDC $1.0000, DAI $0.9998, PYUSD $1.0000 all within band via Coinbase fallback when CoinGecko rate-limits. FDUSD/TUSD require CoinGecko or Binance WS. All unit tests pass.

## Features added in this build

- Robust price verification with CoinGecko retry + Coinbase fallback
- Binance WebSocket with exponential backoff reconnection (capped at 60s)
- Volume anomaly detection as independent alert tier
- In-place refreshing CLI dashboard with volume column
- 8 unit tests covering all signal logic with synthetic data

## Sales pitch

Who to sell to: small funds, prop desks, DeFi treasuries, and fintechs holding stablecoin reserves. Why: minutes matter when a depeg starts - early detection of volume spikes or price drift can prevent cascade losses. Position this as the $200-500/month tier between free GitHub scripts and $50k+ institutional compliance suites. First clients: teams already swimming in stablecoin volume who need reliable, low-latency alerts without enterprise procurement.

## Upgrade path

1. Live Binance/Coinbase WebSocket with auto-reconnect (implemented)
2. On-chain mint/burn monitoring via Alchemy or QuickNode
3. Hosted dashboard + multi-tenant alerts
4. Paid tier with custom thresholds per client

## License

MIT
