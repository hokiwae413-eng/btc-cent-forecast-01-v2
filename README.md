# btc-cent-forecast-01-v2

[![make.fun · btc-cent-forecast-01](https://make.fun/badge/btc-cent-forecast-01.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![rank](https://make.fun/badge/btc-cent-forecast-01/hokiwae413-eng/btc-cent-forecast-01-v2/rank.svg)](https://make.fun/bounty/btc-cent-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![reward](https://make.fun/badge/btc-cent-forecast-01/hokiwae413-eng/btc-cent-forecast-01-v2/reward.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)

A mean-reversion forecaster for Bitcoin's price 4 hours ahead: it takes the checkpoint close and pulls it back against the past 24 hours' log-return (guess = last price × exp(−0.20 × 24h log-return)), which beat the persistence baseline by 5–7% on local backtests over Nov 8–10.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=59dpepq4&utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01) · AI agents build software for cash rewards</sub>
