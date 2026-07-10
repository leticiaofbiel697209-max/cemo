from __future__ import annotations

import streamlit as st
from sqlalchemy import select

from config.database import get_session
from database.models import Estoque, Insumo
from services.estoque_service import registrar_movimentacao
from utils.constants import TIPOS_MOVIMENTACAO


def render(user: dict) -> None:
    st.title("Controle de estoque")
    with get_session() as session:
        rows = session.execute(select(Insumo).order_by(Insumo.descricao)).scalars().all()
        options = {f"{i.codigo or 'sem código'} - {i.descricao[:90]}": i.id for i in rows}
        if not options:
            st.info("Cadastre ou importe insumos para registrar movimentações.")
            return
        item = st.selectbox("Insumo", options.keys())
        insumo = session.get(Insumo, options[item])
        estoque = insumo.estoque or Estoque(insumo_id=insumo.id)
        st.metric("Saldo atual", estoque.quantidade_atual or 0)
        with st.form("mov"):
            tipo = st.selectbox("Tipo de movimentação", TIPOS_MOVIMENTACAO)
            quantidade = st.number_input("Quantidade", min_value=0.0, step=1.0)
            motivo = st.text_area("Motivo / justificativa")
            lote = st.text_input("Lote")
            validade = st.date_input("Validade", value=None)
            permitir = st.checkbox("Autorizar saldo negativo com justificativa", disabled=user["perfil"] != "administrador")
            saldo_previsto = quantidade if tipo == "inventário" else (estoque.quantidade_atual or 0) + (quantidade if tipo in {"entrada", "devolução"} else -quantidade)
            st.info(f"Saldo previsto após operação: {saldo_previsto}")
            if st.form_submit_button("Registrar movimentação"):
                try:
                    registrar_movimentacao(session, estoque, tipo, quantidade, user["id"], motivo, permitir, lote or None, validade)
                    session.add(estoque)
                    st.success("Movimentação registrada.")
                except ValueError as exc:
                    st.error(str(exc))
