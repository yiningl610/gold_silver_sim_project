# Gold & Silver ETF Paper-Trading Simulator (Manual Prices)

This is a small starter project that:
- Initializes a portfolio with **$50,000** split **60% Gold / 40% Silver** (3:2),
- Uses **manually provided daily prices** (no API),
- Computes marked-to-market portfolio value and P&L.

## Quick start

From the project folder:

```bash
python main.py --date 2026-02-01 --gold 235.40 --silver 28.10
```

You can change the initial allocation:

```bash
python main.py --date 2026-02-01 --gold 235.40 --silver 28.10 --gold-ratio 0.6
```

## Next steps
- Add **trade operations** (buy/sell) with cash checks
- Add a **daily ledger** (CSV) for tracking history
- Add a **strategy layer** that suggests trades (but doesn't auto-execute)


## Trade operations (buy/sell)

You can apply manual trades between valuations.

Example (Python):

```python
from gold_silver_sim.models import MarketPrice
from gold_silver_sim.portfolio import initialize_portfolio, portfolio_value
from gold_silver_sim.trades import buy_gold, sell_silver

price = MarketPrice(date="2026-02-01", gold_price=235.40, silver_price=28.10)
p = initialize_portfolio(price)

# Suppose you later deposit proceeds from a sale or keep some cash:
p.cash = 1000.00

# Buy $200 of gold:
buy_gold(p, price, cash_amount=200.00)

# Sell 5 shares of silver:
sell_silver(p, price, shares=5.0)

print(portfolio_value(p, price))
```

Rules enforced:
- No negative cash (can't buy more than you have)
- No short selling (can't sell more shares than you hold)
- Fractional shares allowed
- No transaction costs (for now)


## Trade ledger & daily NAV

This project now records:
- **All trades** to `data/trades_ledger.csv`
- **Daily portfolio snapshots** to `data/daily_nav.csv`

Both files are **append-only** and never split by month.

### Example usage

```python
from gold_silver_sim.models import MarketPrice
from gold_silver_sim.portfolio import initialize_portfolio
from gold_silver_sim.trades import buy_gold
from gold_silver_sim.ledger import record_trade, record_daily_nav

price = MarketPrice(date="2026-02-01", gold_price=235.40, silver_price=28.10)
p = initialize_portfolio(price)

# Suppose you later have cash:
p.cash = 500.0
buy_gold(p, price, cash_amount=200.0)

record_trade(
    date=price.date,
    asset="GOLD",
    action="BUY",
    price=price.gold_price,
    cash_amount=200.0,
    shares=200.0 / price.gold_price,
    fee=0.0,
    notes="manual buy",
    portfolio=p,
    market_price=price,
    initial_cash=50_000.0,
)

record_daily_nav(
    market_price=price,
    portfolio=p,
    initial_cash=50_000.0,
)
```


## One-day runner (with optional trades)

You can now simulate a **full trading day** with a single function call.
Trades can be **empty or omitted**.

```python
from gold_silver_sim.models import MarketPrice
from gold_silver_sim.portfolio import initialize_portfolio
from gold_silver_sim.runner import run_day

# Day 0
p = initialize_portfolio(
    MarketPrice("2026-02-01", 235.40, 28.10)
)

# Day 1: no trades
run_day(
    date="2026-02-02",
    gold_price=236.20,
    silver_price=28.40,
    portfolio=p,
)

# Day 2: manual trades
run_day(
    date="2026-02-03",
    gold_price=238.00,
    silver_price=27.50,
    portfolio=p,
    trades=[
        ("SELL_SILVER", 10),
        ("BUY_GOLD", 200),
    ],
)
```

This will:
- Execute trades (if any)
- Append all trades to `data/trades_ledger.csv`
- Append daily NAV to `data/daily_nav.csv`


## Interactive CLI / REPL

A simple command-line interface is provided for daily manual input.

Run from project root:

```bash
python cli.py
```

You will be prompted for:
- Initial date & prices (Day 0)
- Daily gold & silver prices
- Optional trades for each day

All trades and daily NAV will be automatically recorded to:
- `data/trades_ledger.csv`
- `data/daily_nav.csv`


## CLI / REPL (interactive)

Run:

```bash
python repl_cli.py
```

What it does:
- If `data/portfolio_state.json` exists, it loads your latest portfolio.
- Otherwise, it walks you through Day-0 initialization.
- Each day you enter: `date`, `gold_price`, `silver_price`
- Trades are optional. If you enter trades, they are recorded to `data/trades_ledger.csv`.
- Every day, it appends a NAV row to `data/daily_nav.csv` and saves state to `data/portfolio_state.json`.

Tip: If you want a fresh start, delete:
- `data/portfolio_state.json`
- `data/trades_ledger.csv`
- `data/daily_nav.csv`


### CLI quality-of-life

The CLI shows your **current holdings and cash** *before* you enter today's prices, so you can decide whether to trade.


### CLI: show valuation at last entered prices

Before you enter today's prices, the CLI shows your current shares **and** their **valuation using the last prices you entered** (saved in `data/portfolio_state.json`).
