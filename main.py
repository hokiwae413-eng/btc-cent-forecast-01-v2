#!/usr/bin/env python3
"""btc-cent-forecast-01: mean-reversion forecaster for BTC/USDC, 4h ahead.

Model (measured on local backtests, see README):
    guess = last_price * exp(-0.20 * r24)
where r24 is the log-return of the last price over the previous 24 hours
(1440 minutes):  r24 = ln(px[-1]) - ln(px[-1-1440]).

Why: 4h-ahead BTC mean-reverts against its 24h move. An OLS of the forward
4h log-return on the past-24h log-return gives beta -0.40 (corr -0.53,
R^2 0.28), but that overfits: the MAE-optimal shrinkage is ~0.20
(grid-searched on MAE, not MSE). Measured local backtests:
  - hourly pseudo-checkpoints, n=64 (Nov 8-10): persistence 42,870.7c,
    this model 39,978.7c  (-6.7%)
  - 4h-spaced pseudo-checkpoints, n=16: persistence 41,768.3c,
    this model 39,537.6c  (-5.3%)
  - real practice cases p00-p04 (5 derivable actuals): persistence
    47,054.7c, this model 47,265.2c  (+0.4%, neutral there; the edge is
    on the broader pseudo sets)
  - per-day hourly (a=0.25): wins all 3 days; first/second-half split
    (a=0.20): wins both halves.
Momentum and EWMA-drift add-ons were tested and rejected: momentum wins
on the single trending day (Nov 10) but loses badly on Nov 8/9 and on
both full pseudo sets; it is regime-dependent. The 5-decimal grid and
(0, 10,000,000) bounds follow the kit starter's price5.

IO (mirrors starter/main.ts): read every <id>.in in the input directory
in name order, write <id>.out with exactly one forecast row.
Environment: MAKEFUN_INPUT_DIR (default /input), MAKEFUN_OUTPUT_DIR
(default /output). Python 3.12/3.13, standard library only, no network,
no randomness, no wall-clock use: fully deterministic, two runs are
byte-identical.
"""

import json
import math
import os
import sys
from pathlib import Path

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

# Shrinkage applied to the past-24h log-return (MAE-optimal, see header).
SHRINKAGE = 0.20
# Minutes in the lookback window: 24h of one-minute closes.
LOOKBACK_MINUTES = 1440

# Smallest positive price on the scorer's 5-decimal grid.
MIN_PRICE = 0.00001
# Largest grid price below the scorer's exclusive 10,000,000 cap.
MAX_PRICE = 9_999_999.99999


def price5(x):
    """Keep x on the 5-decimal grid inside (0, 10,000,000)."""
    clamped = min(MAX_PRICE, max(MIN_PRICE, x))
    return round(clamped * 100000) / 100000


def validate_case(case, case_id, filename):
    """Reject malformed cases before any forecast is written.

    Checks the case id matches its file name (when the field is present),
    the schema tag is the one this competition ships, and the single
    market's price list is long enough to define a 24h lookback.
    """
    if not isinstance(case, dict):
        raise ValueError(f"{filename} is not a JSON object")
    if case.get("schema") not in (None, "makefun/btc-cent-case/v1"):
        raise ValueError(f"{filename} has unexpected schema {case.get('schema')!r}")
    if "case" in case and case["case"] != case_id:
        raise ValueError(f"{filename} case id {case['case']!r} != file id {case_id!r}")
    markets = case.get("markets")
    if not isinstance(markets, list) or len(markets) != 1:
        raise ValueError(f"{filename} does not hold exactly one market")
    prices = markets[0].get("prices")
    if not isinstance(prices, list) or len(prices) < 2:
        raise ValueError(f"{filename} needs at least 2 prices to forecast")
    return markets[0]


def forecast(prices):
    """Mean-reversion forecast from one market's list of closes."""
    if not isinstance(prices, list) or not prices:
        raise ValueError("market has no prices")
    for p in prices:
        if not isinstance(p, (int, float)) or not math.isfinite(p) or p <= 0:
            raise ValueError("market prices must be finite positive numbers")
    last = prices[-1]
    # Price 1440 minutes back; for shorter inputs use the earliest close.
    base_index = max(0, len(prices) - LOOKBACK_MINUTES - 1)
    base = prices[base_index]
    r24 = math.log(last) - math.log(base)
    guess = last * math.exp(-SHRINKAGE * r24)
    if not math.isfinite(guess):
        raise ValueError("forecast is not finite")
    return price5(guess)


def main():
    input_dir = Path(INPUT_DIR)
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    # Name order, so two runs write the same bytes.
    inputs = sorted(p for p in input_dir.iterdir() if p.name.endswith(".in"))
    for in_path in inputs:
        case_id = in_path.name[: -len(".in")]
        with open(in_path, "r", encoding="utf-8") as f:
            case = json.load(f)
        markets = validate_case(case, case_id, in_path.name)
        price = forecast(markets.get("prices"))
        if not (0 < price < 10_000_000):
            raise ValueError(f"{in_path.name} forecast {price} outside (0, 10000000)")
        payload = {"forecasts": [{"case": case_id, "price": price}]}
        out_path = output_dir / f"{case_id}.out"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
