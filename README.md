# Stablecoin Depeg Detector

Real-time monitor for stablecoin prices. Fires alerts the moment any tracked
stablecoin slips outside the safe band (default $0.99 - $1.01) - the earliest
warning sign of a depeg / bank run.

## Why this matters

Stablecoin depegs are the crypto equivalent of a bank run. When USDC or USDT
breaks the peg, billions in value move in minutes. Funds, prop desks, and
fintech teams pay for lead time because minutes matter.

## Quick start

```bash
pip install -r requirements.txt
python depeg_detector.py
```

Poll continuously:

```bash
python depeg_detector.py --loop 30
```

## Alerts

- **Console** - always on
- **Telegram** - set bot token + chat ID in config
- **Email (SMTP)** - set credentials in config

## Tracked stablecoins

USDT, USDC, DAI, FDUSD, PYUSD, TUSD (CoinGecko free tier, no API key)

## Upgrade path

1. Swap the REST poll for a Binance or Coinbase WebSocket for tick-by-tick data
2. Add volume anomaly detection (sudden withdrawal spikes, mint/burn imbalances)
3. Add on-chain monitoring via a node provider (Alchemy, QuickNode) for mint/burn events
4. Package as a hosted service with a dashboard

## Config

Copy `config.json.example` to `config.json` and fill in your alert channels.

## License

MIT
