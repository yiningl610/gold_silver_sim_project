from __future__ import annotations

import csv
from pathlib import Path
from datetime import datetime
from typing import Optional

from .models import MarketPrice, Portfolio
from .portfolio import portfolio_value


DATA_DIR = Path("data")
TRADES_FILE = DATA_DIR / "trades_ledger.csv"
NAV_FILE = DATA_DIR / "daily_nav.csv"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)


def record_trade(
    *,
    timestamp: Optional[datetime],
    date: str,
    asset: str,
    action: str,
    price: float,
    cash_amount: Optional[float],
    shares: Optional[float],
    fee: float,
    notes: str,
    portfolio: Portfolio,
    market_price: MarketPrice,
    initial_cash: float,
) -> None:
    """Append a single trade record to trades_ledger.csv."""
    _ensure_data_dir()
    ts = (timestamp or datetime.utcnow()).isoformat(timespec="seconds")

    snapshot = portfolio_value(portfolio, market_price, initial_cash=initial_cash)

    file_exists = TRADES_FILE.exists()
    with TRADES_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp",
                "date",
                "asset",
                "action",
                "price",
                "cash_amount",
                "shares",
                "fee",
                "notes",
                "cash_after",
                "gold_shares_after",
                "silver_shares_after",
                "total_value_after",
            ])
        writer.writerow([
            ts,
            date,
            asset,
            action,
            f"{price:.6f}",
            "" if cash_amount is None else f"{cash_amount:.2f}",
            "" if shares is None else f"{shares:.6f}",
            f"{fee:.2f}",
            notes,
            f"{portfolio.cash:.2f}",
            f"{portfolio.gold_shares:.6f}",
            f"{portfolio.silver_shares:.6f}",
            f"{snapshot['total_value']:.2f}",
        ])


def record_daily_nav(
    *,
    market_price: MarketPrice,
    portfolio: Portfolio,
    initial_cash: float,
) -> None:
    """Append today's NAV snapshot to daily_nav.csv."""
    _ensure_data_dir()
    snapshot = portfolio_value(portfolio, market_price, initial_cash=initial_cash)

    gold_value = portfolio.gold_shares * market_price.gold_price
    silver_value = portfolio.silver_shares * market_price.silver_price
    total = snapshot["total_value"]

    file_exists = NAV_FILE.exists()
    with NAV_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "date",
                "gold_price",
                "silver_price",
                "cash",
                "gold_shares",
                "silver_shares",
                "gold_value",
                "silver_value",
                "total_value",
                "pnl",
                "pnl_pct",
                "gold_weight",
                "silver_weight",
                "cash_weight",
            ])

        writer.writerow([
            market_price.date,
            f"{market_price.gold_price:.6f}",
            f"{market_price.silver_price:.6f}",
            f"{portfolio.cash:.2f}",
            f"{portfolio.gold_shares:.6f}",
            f"{portfolio.silver_shares:.6f}",
            f"{gold_value:.2f}",
            f"{silver_value:.2f}",
            f"{total:.2f}",
            f"{snapshot['pnl']:.2f}",
            f"{snapshot['pnl'] / initial_cash:.6f}",
            f"{gold_value / total if total else 0:.6f}",
            f"{silver_value / total if total else 0:.6f}",
            f"{portfolio.cash / total if total else 0:.6f}",
        ])
