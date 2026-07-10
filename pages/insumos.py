from __future__ import annotations

import streamlit as st
from sqlalchemy import select

from components.tables import searchable_table
from config.database import get_session
from database.models import Estoque, Insumo
from services.alertas_service import criticidade
from services.auditoria_service import registrar
from services.estoque_service import atualizar_calculos
from services.relatorios_service import df_insumos


def render(user: dict) -> None:
    st.title("Cadastro e consulta de insumos")
    with get_session() as session:
        with st.expander("Novo insumo", expanded=False):
            with st.form("insumo_form"):
                col1, col2 = st.columns(2)
                codigo = col1.text_input("Código")
                descricao = col2.text_input("Descrição")
                categoria = col1.text_input("Categoria")
                unidade = col2.text_input("Unidade de medida")
                fornecedor = col1.text_input("Fornecedor principal")
                exclusivo = col2.checkbox("Exclusivo")
                observacoes = st.text_area("Observações")
                if st.form_submit_button("Salvar insumo"):
                    insumo = Insumo(codigo=codigo or None, descricao=descricao, categoria=categoria, unidade_medida=unidade, fornecedor_principal=fornecedor, exclusivo=exclusivo, observacoes=observacoes)
                    session.add(insumo)
                    session.flush()
                    estoque = Estoque(insumo_id=insumo.id)
                    atualizar_calculos(estoque)
                    session.add(estoque)
                    registrar(session, user["id"], "insumo", insumo.id, "criação", depois={"descricao": descricao})
                    st.success("Insumo cadastrado.")
        df = df_insumos(session)
        searchable_table(df, "insumos")
        options = {f"{i.codigo or 'sem código'} - {i.descricao[:80]}": i.id for i in session.execute(select(Insumo).order_by(Insumo.descricao)).scalars()}
        if options:
            selected = st.selectbox("Abrir item", options.keys())
            insumo = session.get(Insumo, options[selected])
            estoque = insumo.estoque
            c1, c2, c3 = st.columns(3)
            c1.metric("Estoque atual", estoque.quantidade_atual if estoque else 0)
            c2.metric("Cobertura", estoque.cobertura_dias if estoque and estoque.cobertura_dias is not None else "-")
            c3.metric("Criticidade", insumo.criticidade_manual or criticidade(estoque, insumo))
            st.write(insumo.observacoes or "Sem observações registradas.")
