from __future__ import annotations

from .models import MarketPrice, Portfolio


def buy_gold(portfolio: Portfolio, price: MarketPrice, cash_amount: float) -> None:
    """Buy gold using `cash_amount` dollars.

    Rules:
      - cash_amount must be > 0
      - portfolio.cash must be sufficient
      - fractional shares are allowed
      - no transaction costs (for now)
    """
    if cash_amount <= 0:
        raise ValueError("cash_amount must be > 0")
    if price.gold_price <= 0:
        raise ValueError("gold_price must be positive")
    if portfolio.cash + 1e-12 < cash_amount:
        raise ValueError("Insufficient cash to buy gold")

    shares = cash_amount / price.gold_price
    portfolio.cash -= cash_amount
    portfolio.gold_shares += shares


def sell_gold(portfolio: Portfolio, price: MarketPrice, shares: float) -> None:
    """Sell `shares` of gold.

    Rules:
      - shares must be > 0
      - shares must be <= portfolio.gold_shares
      - proceeds are added to portfolio.cash
      - no transaction costs (for now)
    """
    if shares <= 0:
        raise ValueError("shares must be > 0")
    if price.gold_price <= 0:
        raise ValueError("gold_price must be positive")
    if portfolio.gold_shares + 1e-12 < shares:
        raise ValueError("Insufficient gold shares to sell")

    proceeds = shares * price.gold_price
    portfolio.gold_shares -= shares
    portfolio.cash += proceeds


def buy_silver(portfolio: Portfolio, price: MarketPrice, cash_amount: float) -> None:
    """Buy silver using `cash_amount` dollars."""
    if cash_amount <= 0:
        raise ValueError("cash_amount must be > 0")
    if price.silver_price <= 0:
        raise ValueError("silver_price must be positive")
    if portfolio.cash + 1e-12 < cash_amount:
        raise ValueError("Insufficient cash to buy silver")

    shares = cash_amount / price.silver_price
    portfolio.cash -= cash_amount
    portfolio.silver_shares += shares


def sell_silver(portfolio: Portfolio, price: MarketPrice, shares: float) -> None:
    """Sell `shares` of silver."""
    if shares <= 0:
        raise ValueError("shares must be > 0")
    if price.silver_price <= 0:
        raise ValueError("silver_price must be positive")
    if portfolio.silver_shares + 1e-12 < shares:
        raise ValueError("Insufficient silver shares to sell")

    proceeds = shares * price.silver_price
    portfolio.silver_shares -= shares
    portfolio.cash += proceeds
