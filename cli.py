from __future__ import annotations

from typing import List, Tuple

from gold_silver_sim.models import MarketPrice
from gold_silver_sim.portfolio import initialize_portfolio
from gold_silver_sim.runner import run_day


def prompt_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt).strip())
        except ValueError:
            print("Please enter a valid number.")


def prompt_trades() -> List[Tuple[str, float]]:
    trades: List[Tuple[str, float]] = []
    print("\nEnter trades for today (empty action to finish).")
    print("Supported actions: BUY_GOLD, SELL_GOLD, BUY_SILVER, SELL_SILVER")

    while True:
        action = input("Action (or press Enter to finish): ").strip().upper()
        if not action:
            break
        amount = prompt_float("Amount (cash for BUY, shares for SELL): ")
        trades.append((action, amount))
    return trades


def main() -> None:
    print("=== Gold & Silver Paper Trading CLI ===\n")

    # Day 0 init
    date0 = input("Initial date (YYYY-MM-DD): ").strip()
    gold0 = prompt_float("Initial gold price: ")
    silver0 = prompt_float("Initial silver price: ")

    portfolio = initialize_portfolio(
        MarketPrice(date0, gold0, silver0)
    )

    print("\nPortfolio initialized. Starting daily loop.\n")

    while True:
        date = input("\nDate (YYYY-MM-DD, or 'q' to quit): ").strip()
        if date.lower() == "q":
            print("Exiting. Ledger saved.")
            break

        gold = prompt_float("Gold price today: ")
        silver = prompt_float("Silver price today: ")

        has_trades = input("Any trades today? (y/n): ").strip().lower()
        trades = []
        if has_trades == "y":
            trades = prompt_trades()

        run_day(
            date=date,
            gold_price=gold,
            silver_price=silver,
            portfolio=portfolio,
            trades=trades,
        )

        print("Day recorded.")


if __name__ == "__main__":
    main()
