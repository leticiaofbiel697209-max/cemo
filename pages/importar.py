from __future__ import annotations

import streamlit as st

from config.database import get_session
from services.import_service import FIELD_ALIASES, import_sheet, preview


def render(user: dict) -> None:
    st.title("Importar planilha")
    uploaded = st.file_uploader("Arquivo Excel", type=["xlsx", "xlsm"])
    if not uploaded:
        st.info("Envie a planilha original `INSUMOS CPC_CEMO (3).xlsx` ou uma versão futura do mesmo modelo.")
        return
    file_bytes = uploaded.getvalue()
    sheets, mappings = preview(file_bytes)
    st.success(f"{len(sheets)} aba(s) identificada(s).")
    final_mappings = {}
    for sheet_name, df in sheets.items():
        with st.expander(f"Aba: {sheet_name}", expanded=True):
            st.dataframe(df.head(20), use_container_width=True)
            cols = [""] + list(df.columns)
            final_mappings[sheet_name] = {}
            for field in FIELD_ALIASES:
                suggested = mappings[sheet_name].get(field) or ""
                index = cols.index(suggested) if suggested in cols else 0
                final_mappings[sheet_name][field] = st.selectbox(field, cols, index=index, key=f"{sheet_name}_{field}") or None
    if st.button("Confirmar importação"):
        with get_session() as session:
            result = import_sheet(session, uploaded.name, sheets, final_mappings, user["id"])
            st.success(f"Importação registrada: {result.registros_importados} novo(s) insumo(s), {result.registros_ignorados} ignorado(s).")
