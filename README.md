# Stablecoin Depeg Detector

Real-time monitor for stablecoin prices and volume anomalies. Fires the moment any tracked stablecoin slips outside the safe band (default $0.99–$1.01) or shows a sudden volume spike — the earliest warning of a depeg or liquidity event.

## Why this matters / Sales pitch

Stablecoin depegs are the crypto equivalent of a bank run. USDC/SVB (2023) and UST (2022) moved billions in minutes. Funds, prop desks, market makers, and fintech teams that hold or intermediate large stablecoin volume pay for lead time because **minutes matter**. A few hundred dollars per month is cheap insurance against a multi-million-dollar loss. This tool is built for people already swimming in stablecoin flow who need sub-minute detection without building it themselves.

## Features (v2)

- **Coinbase WebSocket** tick-by-tick prices with automatic reconnection
- **REST fallback** for pairs without a direct WS feed
- **Volume anomaly detection** — flags when 24h volume exceeds 3× recent average
- **In-place CLI dashboard** — one line per coin, refreshes every 2s
- Threshold alerts (console; Telegram/email still supported via config)
- Unit tests for threshold and volume logic

## Quick start

```bash
pip install -r requirements.txt
python depeg_detector.py
```

Optional config:

```bash
cp config.json.example config.json
# edit thresholds / alert channels
python depeg_detector.py --config config.json
```

## Tracked stablecoins

USDT, USDC, DAI, FDUSD, PYUSD, TUSD (Coinbase pairs where available)

## Tests

```bash
python -m unittest test_depeg.py
```

## Upgrade path

- Add Binance combined stream as secondary source
- On-chain mint/burn monitoring
- Hosted multi-tenant dashboard + webhook API
- Historical depeg database

## Config

Copy `config.json.example` to `config.json`.

## License

MIT
