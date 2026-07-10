from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import select

from config.database import get_session
from database.models import AtaContrato


def render(user: dict) -> None:
    st.title("Atas e contratos")
    with get_session() as session:
        with st.expander("Cadastrar ata/contrato"):
            with st.form("ata"):
                numero = st.text_input("Número da ata")
                processo = st.text_input("Número do processo")
                fornecedor = st.text_input("Fornecedor")
                objeto = st.text_area("Objeto")
                inicio = st.date_input("Data de início", value=None)
                fim = st.date_input("Data de fim", value=None)
                valor = st.number_input("Valor total", min_value=0.0)
                saldo = st.number_input("Saldo disponível", min_value=0.0)
                status = st.selectbox("Status", ["vigente", "vencendo", "vencida", "sem saldo", "encerrada"])
                if st.form_submit_button("Salvar ata"):
                    session.add(AtaContrato(numero_ata=numero, numero_processo=processo, fornecedor=fornecedor, objeto=objeto, data_inicio=inicio, data_fim=fim, valor_total=valor, saldo_disponivel=saldo, status=status))
                    st.success("Ata cadastrada.")
        rows = session.execute(select(AtaContrato).order_by(AtaContrato.data_fim)).scalars().all()
        st.dataframe(pd.DataFrame([{c.name: getattr(a, c.name) for c in AtaContrato.__table__.columns} for a in rows]), use_container_width=True, hide_index=True)
