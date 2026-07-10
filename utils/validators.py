from __future__ import annotations

import re


def valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


def require(value, label: str) -> str | None:
    return None if str(value or "").strip() else f"{label} é obrigatório."
