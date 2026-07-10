from __future__ import annotations

import pandas as pd


def money(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def number(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
