from __future__ import annotations

from typing import Iterable, Tuple, Union, Optional

from .models import MarketPrice, Portfolio
from .trades import buy_gold, sell_gold, buy_silver, sell_silver
from .ledger import record_trade, record_daily_nav


Trade = Tuple[str, float]  # (action, amount)


def run_day(
    *,
    date: str,
    gold_price: float,
    silver_price: float,
    portfolio: Portfolio,
    trades: Optional[Iterable[Trade]] = None,
    initial_cash: float = 50_000.0,
) -> None:
    """Run one trading day with optional manual trades.

    Args:
        date: ISO date string, e.g. "2026-02-03"
        gold_price: Gold ETF price
        silver_price: Silver ETF price
        portfolio: existing Portfolio (mutated in-place)
        trades: optional iterable of (action, amount)
            Supported actions:
              - BUY_GOLD (amount = cash)
              - SELL_GOLD (amount = shares)
              - BUY_SILVER (amount = cash)
              - SELL_SILVER (amount = shares)
        initial_cash: initial capital for P&L calculation
    """
    price = MarketPrice(
        date=date,
        gold_price=gold_price,
        silver_price=silver_price,
    )

    # Execute trades if provided
    if trades:
        for action, amount in trades:
            action = action.upper()

            if action == "BUY_GOLD":
                buy_gold(portfolio, price, cash_amount=amount)
                record_trade(
                    date=date,
                    asset="GOLD",
                    action="BUY",
                    price=price.gold_price,
                    cash_amount=amount,
                    shares=amount / price.gold_price,
                    fee=0.0,
                    notes="run_day",
                    portfolio=portfolio,
                    market_price=price,
                    initial_cash=initial_cash,
                )

            elif action == "SELL_GOLD":
                sell_gold(portfolio, price, shares=amount)
                record_trade(
                    date=date,
                    asset="GOLD",
                    action="SELL",
                    price=price.gold_price,
                    cash_amount=None,
                    shares=amount,
                    fee=0.0,
                    notes="run_day",
                    portfolio=portfolio,
                    market_price=price,
                    initial_cash=initial_cash,
                )

            elif action == "BUY_SILVER":
                buy_silver(portfolio, price, cash_amount=amount)
                record_trade(
                    date=date,
                    asset="SILVER",
                    action="BUY",
                    price=price.silver_price,
                    cash_amount=amount,
                    shares=amount / price.silver_price,
                    fee=0.0,
                    notes="run_day",
                    portfolio=portfolio,
                    market_price=price,
                    initial_cash=initial_cash,
                )

            elif action == "SELL_SILVER":
                sell_silver(portfolio, price, shares=amount)
                record_trade(
                    date=date,
                    asset="SILVER",
                    action="SELL",
                    price=price.silver_price,
                    cash_amount=None,
                    shares=amount,
                    fee=0.0,
                    notes="run_day",
                    portfolio=portfolio,
                    market_price=price,
                    initial_cash=initial_cash,
                )

            else:
                raise ValueError(f"Unsupported trade action: {action}")

    # Record end-of-day NAV regardless of trades
    record_daily_nav(
        market_price=price,
        portfolio=portfolio,
        initial_cash=initial_cash,
    )
