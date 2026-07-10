from __future__ import annotations

import pandas as pd
import streamlit as st


def searchable_table(df: pd.DataFrame, key: str, placeholder: str = "Pesquisar") -> pd.DataFrame:
    query = st.text_input(placeholder, key=f"{key}_search")
    filtered = df
    if query and not df.empty:
        mask = df.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        filtered = df[mask]
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    return filtered
