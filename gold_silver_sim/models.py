from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketPrice:
    """Market prices for a single day.

    Attributes:
        date: ISO date string, e.g. "2026-02-01"
        gold_price: price per 1 share/unit of the chosen Gold ETF
        silver_price: price per 1 share/unit of the chosen Silver ETF
    """
    date: str
    gold_price: float
    silver_price: float


@dataclass
class Portfolio:
    """Portfolio state at a point in time."""
    cash: float
    gold_shares: float
    silver_shares: float
