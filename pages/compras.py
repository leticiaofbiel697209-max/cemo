from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import select

from config.database import get_session
from database.models import Insumo, ProcessoCompra
from services.compras_service import alterar_etapa
from utils.constants import ETAPAS_PROCESSO


def render(user: dict) -> None:
    st.title("Compras e processos")
    with get_session() as session:
        insumos = {f"{i.codigo or 'sem código'} - {i.descricao[:70]}": i.id for i in session.execute(select(Insumo)).scalars()}
        with st.expander("Novo processo"):
            with st.form("proc"):
                numero = st.text_input("Número do processo")
                item = st.selectbox("Insumo", [""] + list(insumos.keys()))
                descricao = st.text_area("Descrição")
                qtd = st.number_input("Quantidade solicitada", min_value=0.0)
                etapa = st.selectbox("Etapa atual", ETAPAS_PROCESSO)
                status = st.selectbox("Status", ["aberto", "em andamento", "aguardando entrega", "concluído", "cancelado"])
                responsavel = st.text_input("Responsável atual")
                previsao = st.date_input("Previsão de entrega", value=None)
                if st.form_submit_button("Salvar processo"):
                    session.add(ProcessoCompra(numero_processo=numero, insumo_id=insumos.get(item), descricao=descricao, quantidade_solicitada=qtd, etapa_atual=etapa, status=status, responsavel_atual=responsavel, previsao_entrega=previsao))
                    st.success("Processo cadastrado.")
        processos = session.execute(select(ProcessoCompra).order_by(ProcessoCompra.atualizado_em.desc())).scalars().all()
        df = pd.DataFrame([{c.name: getattr(p, c.name) for c in ProcessoCompra.__table__.columns} for p in processos])
        tab1, tab2 = st.tabs(["Tabela", "Kanban"])
        tab1.dataframe(df, use_container_width=True, hide_index=True)
        with tab2:
            cols = st.columns(4)
            for idx, etapa in enumerate(ETAPAS_PROCESSO):
                with cols[idx % 4]:
                    st.subheader(etapa.title())
                    for p in [p for p in processos if p.etapa_atual == etapa]:
                        with st.container(border=True):
                            st.write(f"**{p.numero_processo}**")
                            st.caption(p.descricao or "Sem descrição")
                            nova = st.selectbox("Mover para", ETAPAS_PROCESSO, index=ETAPAS_PROCESSO.index(p.etapa_atual), key=f"move_{p.id}")
                            if nova != p.etapa_atual and st.button("Atualizar", key=f"btn_{p.id}"):
                                alterar_etapa(session, p, nova, user["id"])
                                st.rerun()
