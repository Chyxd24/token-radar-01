# Token Radar

[![make.fun](https://make.fun/badge/token-radar-01.svg)](https://make.fun/bounty/token-radar-01)
[![rank](https://make.fun/badge/token-radar-01/Chyxd24/token-radar-01/rank.svg)](https://make.fun/bounty/token-radar-01/leaderboard)
[![reward](https://make.fun/badge/token-radar-01/Chyxd24/token-radar-01/reward.svg)](https://make.fun/bounty/token-radar-01)

A token launch radar: it reads make.fun's sealed DefiLlama protocol snapshot and ranks pre-token
protocols by an implied value derived from the snapshot's own figures — TVL, seven-day growth and how
long the protocol has run with no token — then gives every one a concrete farm plan with a cost and a
time on each step.

The dashboard is a static page: no framework, no network. It separates protocols whose token already
trades (kept apart in a Live token tab) from those still to come, covers all 40 watchlist protocols,
and adds 160 early pre-token protocols below the $50M floor.

## The model

```
base       = tvl_usd x 0.25
growthMult = 1 + (clamp(change_7d, -60, 120) / 100) x 0.5
maturity   = 0.6 + min(age_days, 1095) / 1095 x 0.4      (age unknown: 365)
implied    = max(1, round(base x growthMult x maturity))
```

No protocol name is special-cased: the same function scores every row.

## Run

```
mkdir -p out
MAKEFUN_OUTPUT_DIR=out node main.ts --input /path/to/snapshot.json
```

Writes `out/board.json` (the ranked board), `out/data.js` (the dashboard's data), copies
`dashboard/` and `screenshots/`, and writes `out/dossier.json` with the vendored make.fun library.

## Screenshots

Render the dashboard's three views (board, a protocol's detail, a filtered view) with headless
Chromium:

```
/root/.hermes/bounty/.venv/bin/python tools/shoot.py screenshots out/data.js
```
