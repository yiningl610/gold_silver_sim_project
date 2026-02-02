from __future__ import annotations

from dataclasses import asdict
from typing import List, Tuple, Optional

from gold_silver_sim.models import MarketPrice
from gold_silver_sim.portfolio import (
    DEFAULT_INITIAL_CASH,
    DEFAULT_GOLD_RATIO,
    DEFAULT_SILVER_RATIO,
    initialize_portfolio,
    portfolio_value,
)
from gold_silver_sim.runner import run_day
from gold_silver_sim.state import load_state, save_state



Trade = Tuple[str, float]


def _prompt(text: str) -> str:
    return input(text).strip()


def _prompt_float(text: str) -> float:
    while True:
        if 'p' in locals():
            _print_current_holdings(p, last_price)
        s = _prompt(text)
        try:
            v = float(s)
            return v
        except ValueError:
            print("  Please enter a valid number.")


def _prompt_date(text: str) -> str:
    # Keep it simple: accept any non-empty string; user provides ISO date.
    while True:
        s = _prompt(text)
        if s:
            return s
        print("  Please enter a non-empty date (e.g., 2026-02-01).")


def _prompt_yes_no(text: str, default: bool = False) -> bool:
    s = _prompt(text + (" [Y/n] " if default else " [y/N] "))
    if not s:
        return default
    return s.lower() in {"y", "yes"}


def _parse_trade(action: str, amount_str: str) -> Trade:
    action = action.strip().upper()
    if action not in {"BUY_GOLD", "SELL_GOLD", "BUY_SILVER", "SELL_SILVER"}:
        raise ValueError("Unsupported action")
    amount = float(amount_str)
    if amount <= 0:
        raise ValueError("Amount must be > 0")
    return (action, amount)


def _prompt_trades() -> List[Trade]:
    trades: List[Trade] = []
    print("\nEnter trades (optional). One per line in the format:")
    print("  BUY_GOLD 200        (cash amount)")
    print("  SELL_SILVER 10      (shares)")
    print("Supported: BUY_GOLD, SELL_GOLD, BUY_SILVER, SELL_SILVER")
    print("Press Enter on an empty line to finish.\n")

    while True:
        line = _prompt("trade> ")
        if not line:
            break
        parts = line.split()
        if len(parts) != 2:
            print("  Format error. Use: ACTION AMOUNT (e.g., BUY_GOLD 200)")
            continue
        try:
            trades.append(_parse_trade(parts[0], parts[1]))
        except Exception as e:
            print(f"  Invalid trade: {e}")
    return trades


def _print_current_holdings(portfolio) -> None:
    last = load_last_price()
    print("--- Current portfolio (before today's prices) ---")
    print(f"  Cash:   ${portfolio.cash:.2f}")
    print(f"  Gold:   {portfolio.gold_shares:.6f} shares")
    print(f"  Silver: {portfolio.silver_shares:.6f} shares")

    if last:
        gold_val = portfolio.gold_shares * float(last["gold_price"])
        silver_val = portfolio.silver_shares * float(last["silver_price"])
        total = gold_val + silver_val + portfolio.cash
        print("  --- Mark-to-market using last prices ---")
        print(f"  Last price date: {last['date']}")
        print(f"  Gold value:   ${gold_val:.2f}")
        print(f"  Silver value: ${silver_val:.2f}")
        print(f"  Total value:  ${total:.2f}")

    print("-------------------------------------------------")


def _print_current_holdings(portfolio, last_price: Optional[MarketPrice]) -> None:
    print("\n--- Current portfolio (before today's prices) ---")
    print(f"  Cash:   ${portfolio.cash:.2f}")
    print(f"  Gold:   {portfolio.gold_shares:.6f} shares")
    print(f"  Silver: {portfolio.silver_shares:.6f} shares")

    if last_price is not None and last_price.gold_price > 0 and last_price.silver_price > 0:
        gold_value = portfolio.gold_shares * last_price.gold_price
        silver_value = portfolio.silver_shares * last_price.silver_price
        total = gold_value + silver_value + portfolio.cash
        print("")
        print(f"  Valuation @ last prices ({last_price.date}):")
        print(f"    Gold value:   ${gold_value:.2f}  (price {last_price.gold_price:.4f})")
        print(f"    Silver value: ${silver_value:.2f}  (price {last_price.silver_price:.4f})")
        print(f"    Total value:  ${total:.2f}")
    else:
        print("")
        print("  Valuation @ last prices: N/A (no prior prices saved yet)")

    print("-------------------------------------------------\n")


def _print_summary(date: str, gold_price: float, silver_price: float, portfolio, initial_cash: float) -> None:
    snap = portfolio_value(
        portfolio,
        MarketPrice(date=date, gold_price=gold_price, silver_price=silver_price),
        initial_cash=initial_cash,
    )
    print("\n=== Summary ===")
    print(f"As of:        {snap['date']}")
    print(f"Total value:  ${snap['total_value']:.2f}")
    print(f"P&L:          ${snap['pnl']:.2f} ({snap['pnl']/initial_cash:.2%})")
    print("\nHoldings:")
    print(f"  Cash:        ${portfolio.cash:.2f}")
    print(f"  Gold:        {portfolio.gold_shares:.6f} shares")
    print(f"  Silver:      {portfolio.silver_shares:.6f} shares")
    print("\nSaved to:")
    print("  data/trades_ledger.csv (if any trades)")
    print("  data/daily_nav.csv (every day)")
    print("  data/portfolio_state.json (every day)")


def main() -> None:
    print("Gold/Silver Paper-Trading Simulator (Manual Prices) - CLI")
    print("---------------------------------------------------------")

    p_loaded, last_price = load_state()
    if p_loaded is None:
        print("\nNo existing portfolio_state found. Let's initialize Day-0.")
        date0 = _prompt_date("Day-0 date (e.g., 2026-02-01): ")
        gold0 = _prompt_float("Gold ETF price: ")
        silver0 = _prompt_float("Silver ETF price: ")

        initial_cash = _prompt_float(f"Initial cash (default {DEFAULT_INITIAL_CASH:.0f}): ") if _prompt_yes_no("Change initial cash?", default=False) else DEFAULT_INITIAL_CASH
        gold_ratio = _prompt_float(f"Gold allocation ratio (default {DEFAULT_GOLD_RATIO}): ") if _prompt_yes_no("Change gold ratio?", default=False) else DEFAULT_GOLD_RATIO
        silver_ratio = 1.0 - gold_ratio

        p = initialize_portfolio(
            MarketPrice(date=date0, gold_price=gold0, silver_price=silver0),
            initial_cash=initial_cash,
            gold_ratio=gold_ratio,
            silver_ratio=silver_ratio,
        )

        # Record Day-0 NAV (and persist state)
        run_day(
            date=date0,
            gold_price=gold0,
            silver_price=silver0,
            portfolio=p,
            trades=[],  # no trades beyond initialization
            initial_cash=initial_cash,
        )
        save_state(p, MarketPrice(date=date0, gold_price=gold0, silver_price=silver0))
        last_price = MarketPrice(date=date0, gold_price=gold0, silver_price=silver0)
        _print_summary(date0, gold0, silver0, p, initial_cash)
    else:
        p = p_loaded
        # We still need initial_cash for P&L %; keep default unless user changes.
        initial_cash = DEFAULT_INITIAL_CASH
        print("\nLoaded existing portfolio from data/portfolio_state.json.")
        if _prompt_yes_no(f"Use a different initial_cash than default {DEFAULT_INITIAL_CASH:.0f} for P&L display?", default=False):
            initial_cash = _prompt_float("Initial cash: ")

    print("\nEnter daily prices; type 'quit' to exit.\n")

    while True:
        s = _prompt("Date (YYYY-MM-DD) or 'quit': ")
        if s.lower() in {"q", "quit", "exit"}:
            break
        if not s:
            continue
        date = s

        print("\nCurrent holdings BEFORE today's prices:")
        print(f"  Cash:   ${p.cash:.2f}")
        print(f"  Gold:   {p.gold_shares:.6f} shares")
        print(f"  Silver: {p.silver_shares:.6f} shares")

        gold = _prompt_float("Gold ETF price: ")
        silver = _prompt_float("Silver ETF price: ")

        trades = _prompt_trades() if _prompt_yes_no("Any trades today?", default=False) else []

        try:
            run_day(
                date=date,
                gold_price=gold,
                silver_price=silver,
                portfolio=p,
                trades=trades,
                initial_cash=initial_cash,
            )
            save_state(p, MarketPrice(date=date0, gold_price=gold0, silver_price=silver0))
            _print_summary(date, gold, silver, p, initial_cash)
        except Exception as e:
            print(f"\nERROR: {e}")
            print("No files were rolled back automatically; if needed, delete the last lines in CSVs.")
            print("Try again.\n")

    print("\nBye!\n")


if __name__ == "__main__":
    main()
