from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import select

from config.database import get_session
from database.models import Alerta
from services.alertas_service import gerar_alertas, resolver_alerta


def render(user: dict) -> None:
    st.title("Alertas")
    with get_session() as session:
        if st.button("Gerar alertas agora"):
            st.success(f"{gerar_alertas(session, user['id'])} novo(s) alerta(s) gerado(s).")
        nivel = st.selectbox("Nível", ["todos", "crítico", "alto", "médio", "informativo"])
        status = st.selectbox("Status", ["pendente", "resolvido", "todos"])
        query = select(Alerta).order_by(Alerta.criado_em.desc())
        rows = session.execute(query).scalars().all()
        rows = [a for a in rows if (nivel == "todos" or a.nivel == nivel) and (status == "todos" or a.status == status)]
        st.dataframe(pd.DataFrame([{c.name: getattr(a, c.name) for c in Alerta.__table__.columns} for a in rows]), use_container_width=True, hide_index=True)
        pendentes = {f"{a.nivel.upper()} - {a.titulo}": a.id for a in rows if a.status == "pendente"}
        if pendentes:
            with st.expander("Resolver alerta"):
                selected = st.selectbox("Alerta", pendentes.keys())
                obs = st.text_area("Observação")
                if st.button("Marcar como resolvido"):
                    resolver_alerta(session, session.get(Alerta, pendentes[selected]), user["id"], obs)
                    st.success("Alerta resolvido.")
                    st.rerun()
