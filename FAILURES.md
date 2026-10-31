# Failures

## Price-only monitoring missed the Oct 30, 2026 stablecoin freeze

During the Oct 30, 2026 Binance hack, Tether and Circle froze billions in stablecoins. USDT and USDC held their peg on the CoinGecko and Coinbase feeds this detector uses, so a price-band check did not fire. The freeze was invisible to a monitor that only looks at price.

This repository still has no blacklist, freeze, or mint-authority feed. A freeze that leaves the printed price inside the band is a blind spot for the price tier. The 5-minute volume-velocity tier added in v1.8.0 can catch a trading surge around an event like this. It does not detect a freeze by itself, and it would not have fired on a freeze that left both price and 5-minute volume quiet.

## What the logs from that day actually show

Checked on 2026-10-31:

- The repo has no runtime log files. GitHub Actions has no workflows, so there are no Actions logs. GitHub Pages is not enabled. This environment's cloud-agent list contains only the current run, so there are no saved agent transcripts from Oct 30 to read.
- The written record is git history plus `CHANGELOG.md` and `VERIFY_RESULTS.md`. Verification commits run about once an hour from 2026-10-30 00:08 MDT through 17:08 MDT. There are no commits after 17:08 MDT that night (through 19:06 MDT, when this note was started). Nothing in-repo records prices or feed errors for the evening after 17:08 MDT.
- Every recorded USDT and USDC print that day was inside the old $0.99–$1.01 band. The last one, 17:05 MDT in `VERIFY_RESULTS.md`, is CoinGecko USDT $0.99911 and USDC $0.999787, both marked OK. No depeg alert was written down.
- Gmail for 2026-10-30 has no "Stablecoin Alert" message and no detector error log. A Market Briefs newsletter received at 2026-10-30 11:40 UTC has the snippet "a big crypto hack just went down." That newsletter is not a price feed, a freeze feed, or a detector log, and it was not used as one.

Data-source gaps that were written down:

- **09:06 MDT** (`VERIFY_RESULTS.md` at commit `0eee328`): CoinGecko's free tier was rate-limited from that environment. The snapshot used DefiLlama, with a Coinbase spot cross-check where a pair exists. Recorded prices: USDT $0.9990 (Coinbase $0.9984), USDC $0.9997 (Coinbase $1.0000), DAI $1.0002 (Coinbase $0.9994), FDUSD $0.9975 (no Coinbase figure in the note), PYUSD $1.0004 (Coinbase $1.0000), TUSD $0.9986 (no Coinbase figure in the note). All six were marked OK against $0.99–$1.01.
- **12:03 MDT** (`VERIFY_RESULTS.md` at commit `fe61ac5`, and the changelog): CoinGecko was rate-limited again. DefiLlama and Coinbase were used. Recorded prices: USDT $0.9992, USDC $0.9997, DAI $1.0000, FDUSD $0.9976 (DefiLlama only), PYUSD $1.0004, TUSD $0.9986 (DefiLlama only). All marked OK against $0.99–$1.01.
- **15:05 MDT** (changelog only): the changelog says the check used the CoinGecko free API with Coinbase and DefiLlama fallbacks on rate limit, and lists USDT $0.9991, USDC $0.9997, DAI $1.0000, FDUSD $0.9970, PYUSD $1.0000, TUSD $0.9986. The `VERIFY_RESULTS.md` file in the nearby 15:08 MDT commit `8521880` was still the 14:05 MDT CoinGecko table, not a separate 15:05 table.

No log entry describes a dropped USDT or USDC price, a missing USDT or USDC quote, or a freeze. The gaps above are CoinGecko rate limits plus coins with no Coinbase pair (FDUSD and TUSD are not in `coinbase_pairs`). Fallback prices for USDT and USDC still showed a held peg.
