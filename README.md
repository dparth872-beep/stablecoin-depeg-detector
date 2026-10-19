# Stablecoin Depeg Detector v2

Real-time stablecoin peg monitor with three signal tiers: price depegs, volume spikes, and cross-source price divergence. Built for funds, prop desks, and fintech treasury teams who need lead time when billions move.

## Why this exists

Stablecoin depegs cascade into billions in losses within hours (USDC/SVB March 2023, UST May 2022). The free tools are basic. The institutional suites (TRM, Elliptic, Range) are compliance-priced. This sits in the gap: fast, cheap, trader-grade depeg intelligence.

## Quick start

```bash
pip install -r requirements.txt
python depeg_detector.py                      # single snapshot
python depeg_detector.py --loop 30            # poll every 30 seconds
python depeg_detector.py --dashboard          # live refreshing CLI board
python depeg_detector.py --ws                 # Binance WebSocket tick-by-tick (upgrade path)
```

## Signals

| Tier | Trigger | Meaning |
| --- | --- | --- |
| DEPEG | Price outside $0.99-$1.01 | Peg break - incident mode |
| VOLUME SPIKE | 24h vol > 3x rolling avg | Liquidity stress building |
| DIVERGENCE | Cross-venue gap > 50 bps | One source is stale or manipulated |

## Alerts

- Console (always on) + color-coded CLI dashboard
- Telegram bot
- Email via SMTP

## Tracked stablecoins

USDT, USDC, DAI, FDUSD, PYUSD, TUSD via CoinGecko free tier (no API key). Binance pairs ready for WebSocket upgrade.

## Tests

```bash
python tests/test_depeg_logic.py
```

8 unit tests covering clean data, depeg up/down, missing data, volume spikes, and divergence.

## Sales pitch

Who to sell to: small funds, prop desks, DeFi treasuries, and fintechs holding stablecoin reserves. Why: minutes matter when a depeg starts - Webacy's monitor flagged USR 2+ hours before it lost 94%. Position this as the $200-500/month tier between free GitHub scripts and $50k+ institutional compliance suites.

## Upgrade path

1. Live Binance/Coinbase WebSocket with auto-reconnect
2. On-chain mint/burn monitoring via Alchemy or QuickNode
3. Hosted dashboard + multi-tenant alerts
4. Paid tier with custom thresholds per client

## License

MIT
