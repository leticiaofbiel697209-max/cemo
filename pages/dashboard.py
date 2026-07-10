from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import select

from components.metric_cards import metric_grid
from config.database import get_session
from database.models import AtaContrato, Estoque, Insumo, ProcessoCompra
from database.repository import dashboard_counts
from services.alertas_service import gerar_alertas
from services.relatorios_service import df_insumos
from utils.formatters import money


def render(user: dict) -> None:
    st.title("Dashboard gerencial")
    with get_session() as session:
        if st.button("Atualizar alertas automáticos"):
            total = gerar_alertas(session, user["id"])
            st.success(f"{total} novo(s) alerta(s) gerado(s).")
        counts = dashboard_counts(session)
        metric_grid(
            [
                ("Insumos ativos", counts["total_insumos"], None),
                ("Sem estoque", counts["sem_estoque"], None),
                ("Cobertura <= 15 dias", counts["cobertura_15"], None),
                ("Processos em andamento", counts["processos"], None),
                ("Atas vigentes", counts["atas"], None),
                ("Alertas pendentes", counts["alertas"], None),
                ("Abaixo do mínimo", counts["baixo_minimo"], None),
                ("Valor estimado aberto", money(counts["valor_aberto"]), None),
            ]
        )
        df = df_insumos(session)
        col1, col2 = st.columns(2)
        if not df.empty:
            with col1:
                crit = df["Criticidade"].fillna("não classificado").value_counts().reset_index()
                st.plotly_chart(px.pie(crit, names="Criticidade", values="count", title="Insumos por criticidade"), use_container_width=True)
            with col2:
                bins = pd.cut(df["Cobertura dias"].fillna(-1), bins=[-2, 0, 15, 30, 60, 99999], labels=["sem cálculo", "0-15", "16-30", "31-60", ">60"])
                cov = bins.value_counts().reset_index()
                st.plotly_chart(px.bar(cov, x="Cobertura dias", y="count", title="Cobertura de estoque"), use_container_width=True)
        processos = pd.DataFrame([{"Etapa": p.etapa_atual, "Status": p.status, "Responsável": p.responsavel_atual or "sem responsável"} for p in session.execute(select(ProcessoCompra)).scalars()])
        if not processos.empty:
            c1, c2 = st.columns(2)
            c1.plotly_chart(px.bar(processos.value_counts("Etapa").reset_index(), x="Etapa", y="count", title="Processos por etapa"), use_container_width=True)
            c2.plotly_chart(px.bar(processos.value_counts("Status").reset_index(), x="Status", y="count", title="Processos por status"), use_container_width=True)
