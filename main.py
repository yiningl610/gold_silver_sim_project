from __future__ import annotations

import argparse

from gold_silver_sim.models import MarketPrice
from gold_silver_sim.portfolio import initialize_portfolio, portfolio_value


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Gold/Silver paper-trading simulator (manual prices)."
    )
    p.add_argument("--date", required=True, help='ISO date like "2026-02-01"')
    p.add_argument("--gold", required=True, type=float, help="Gold ETF price")
    p.add_argument("--silver", required=True, type=float, help="Silver ETF price")
    p.add_argument(
        "--initial-cash",
        type=float,
        default=50_000.0,
        help="Initial cash (default: 50000)",
    )
    p.add_argument(
        "--gold-ratio",
        type=float,
        default=0.6,
        help="Initial allocation to gold (default: 0.6)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    price = MarketPrice(date=args.date, gold_price=args.gold, silver_price=args.silver)

    silver_ratio = 1.0 - args.gold_ratio
    portfolio = initialize_portfolio(
        price,
        initial_cash=args.initial_cash,
        gold_ratio=args.gold_ratio,
        silver_ratio=silver_ratio,
    )
    snapshot = portfolio_value(portfolio, price, initial_cash=args.initial_cash)

    print("=== Day-0 Initialized Portfolio ===")
    print(f"Date:         {snapshot['date']}")
    print(f"Gold value:   ${snapshot['gold_value']:.2f}")
    print(f"Silver value: ${snapshot['silver_value']:.2f}")
    print(f"Cash:         ${snapshot['cash']:.2f}")
    print(f"Total:        ${snapshot['total_value']:.2f}")
    print(f"P&L:          ${snapshot['pnl']:.2f}")
    print()
    print("Holdings (fractional shares allowed):")
    print(f"  Gold shares:   {portfolio.gold_shares:.6f}")
    print(f"  Silver shares: {portfolio.silver_shares:.6f}")


if __name__ == "__main__":
    main()
