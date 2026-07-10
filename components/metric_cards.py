from __future__ import annotations

import streamlit as st


def metric_grid(items: list[tuple[str, str | int | float, str | None]]) -> None:
    cols = st.columns(min(4, len(items)) or 1)
    for idx, (label, value, help_text) in enumerate(items):
        with cols[idx % len(cols)]:
            st.metric(label, value, help=help_text)
