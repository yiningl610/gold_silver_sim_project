from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .models import MarketPrice, Portfolio


DEFAULT_INITIAL_CASH: float = 50_000.0
DEFAULT_GOLD_RATIO: float = 0.6   # 3/5
DEFAULT_SILVER_RATIO: float = 0.4 # 2/5


def initialize_portfolio(
    price: MarketPrice,
    *,
    initial_cash: float = DEFAULT_INITIAL_CASH,
    gold_ratio: float = DEFAULT_GOLD_RATIO,
    silver_ratio: float = DEFAULT_SILVER_RATIO,
) -> Portfolio:
    """Initialize (day-0) portfolio by buying gold & silver with all cash.

    Assumes no transaction costs and fractional shares are allowed.
    """
    if initial_cash < 0:
        raise ValueError("initial_cash must be non-negative")
    if price.gold_price <= 0 or price.silver_price <= 0:
        raise ValueError("Prices must be positive")
    if abs((gold_ratio + silver_ratio) - 1.0) > 1e-9:
        raise ValueError("gold_ratio + silver_ratio must equal 1.0")
    if gold_ratio < 0 or silver_ratio < 0:
        raise ValueError("Ratios must be non-negative")

    gold_cash = initial_cash * gold_ratio
    silver_cash = initial_cash * silver_ratio

    gold_shares = gold_cash / price.gold_price if gold_cash else 0.0
    silver_shares = silver_cash / price.silver_price if silver_cash else 0.0

    return Portfolio(cash=0.0, gold_shares=gold_shares, silver_shares=silver_shares)


def portfolio_value(
    portfolio: Portfolio,
    price: MarketPrice,
    *,
    initial_cash: float = DEFAULT_INITIAL_CASH,
) -> Dict[str, float]:
    """Compute today's marked-to-market value and P&L."""
    if price.gold_price <= 0 or price.silver_price <= 0:
        raise ValueError("Prices must be positive")

    gold_value = portfolio.gold_shares * price.gold_price
    silver_value = portfolio.silver_shares * price.silver_price
    total_value = gold_value + silver_value + portfolio.cash

    return {
        "date": price.date,
        "gold_value": float(gold_value),
        "silver_value": float(silver_value),
        "cash": float(portfolio.cash),
        "total_value": float(total_value),
        "pnl": float(total_value - initial_cash),
    }
