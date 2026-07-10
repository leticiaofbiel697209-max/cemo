from __future__ import annotations

from io import BytesIO

import streamlit as st

from config.database import get_session
from services.relatorios_service import dataframe_for


def render(user: dict) -> None:
    st.title("Relatórios")
    report = st.selectbox("Relatório", ["insumos", "processos", "atas", "alertas", "movimentacoes", "auditoria"])
    with get_session() as session:
        df = dataframe_for(session, report)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Baixar CSV", df.to_csv(index=False).encode("utf-8-sig"), file_name=f"{report}.csv", mime="text/csv")
    output = BytesIO()
    with st.spinner("Preparando Excel"):
        with __import__("pandas").ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=report[:31])
    st.download_button("Baixar Excel", output.getvalue(), file_name=f"{report}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    if report == "insumos":
        st.subheader("Relatório executivo")
        criticos = df[df["Criticidade"].isin(["crítico", "alto"])] if not df.empty and "Criticidade" in df else df.head(0)
        st.write(f"Itens prioritários identificados: {len(criticos)}.")
        st.write("Recomendação: revisar processos ativos, atas vigentes e previsão de entrega dos itens com menor cobertura.")
