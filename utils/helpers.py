from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def now() -> datetime:
    return datetime.now()


def parse_decimal(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        text = str(value).replace(".", "").replace(",", ".") if isinstance(value, str) else value
        return float(Decimal(str(text)))
    except (InvalidOperation, ValueError):
        return None


def days_between(left: date | datetime | None, right: date | datetime | None = None) -> int | None:
    if not left:
        return None
    right = right or datetime.now()
    left_date = left.date() if isinstance(left, datetime) else left
    right_date = right.date() if isinstance(right, datetime) else right
    return (right_date - left_date).days


def safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if not denominator:
        return None
    return round((numerator or 0) / denominator, 2)
