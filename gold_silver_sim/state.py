from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple

from .models import Portfolio, MarketPrice


DATA_DIR = Path("data")
STATE_FILE = DATA_DIR / "portfolio_state.json"


def save_state(portfolio: Portfolio, last_price: Optional[MarketPrice]) -> None:
    """Persist portfolio + last known prices to data/portfolio_state.json."""
    DATA_DIR.mkdir(exist_ok=True)
    payload = {
        "portfolio": {
            "cash": portfolio.cash,
            "gold_shares": portfolio.gold_shares,
            "silver_shares": portfolio.silver_shares,
        },
        "last_price": None
        if last_price is None
        else {
            "date": last_price.date,
            "gold_price": last_price.gold_price,
            "silver_price": last_price.silver_price,
        },
    }
    STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_state() -> tuple[Optional[Portfolio], Optional[MarketPrice]]:
    """Load portfolio + last known prices from data/portfolio_state.json if present."""
    if not STATE_FILE.exists():
        return None, None

    payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))

    p_raw = payload.get("portfolio") or {}
    portfolio = Portfolio(
        cash=float(p_raw.get("cash", 0.0)),
        gold_shares=float(p_raw.get("gold_shares", 0.0)),
        silver_shares=float(p_raw.get("silver_shares", 0.0)),
    )

    lp = payload.get("last_price")
    last_price = None
    if isinstance(lp, dict):
        try:
            last_price = MarketPrice(
                date=str(lp.get("date", "")),
                gold_price=float(lp.get("gold_price", 0.0)),
                silver_price=float(lp.get("silver_price", 0.0)),
            )
        except Exception:
            last_price = None

    return portfolio, last_price
