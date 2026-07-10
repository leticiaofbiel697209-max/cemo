from __future__ import annotations

from datetime import date

import streamlit as st
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from components.tables import searchable_table
from config.database import get_session
from database.models import Alerta, Estoque, Insumo, ItemAta, MovimentacaoEstoque, ProcessoCompra
from services.alertas_service import criticidade
from services.auditoria_service import registrar
from services.estoque_service import atualizar_calculos
from services.relatorios_service import df_insumos


def _texto(valor: str) -> str | None:
    valor = valor.strip()
    return valor or None


def render(user: dict) -> None:
    st.title("Cadastro e consulta de insumos")
    st.caption("A base inicial foi preenchida com os produtos da planilha INSUMOS CPC_CEMO (3).xlsx.")

    with get_session() as session:
        with st.expander("Incluir novo produto", expanded=False):
            with st.form("insumo_form", clear_on_submit=True):
                st.subheader("Identificação")
                col1, col2 = st.columns(2)
                codigo = col1.text_input("Código")
                descricao = col2.text_input("Descrição *")
                categoria = col1.text_input("Categoria")
                subcategoria = col2.text_input("Subcategoria / atribuição de compra")
                unidade = col1.text_input("Unidade de medida")
                fornecedor = col2.text_input("Fornecedor principal")
                fabricante = col1.text_input("Fabricante")
                marca = col2.text_input("Marca")
                exclusivo = col1.checkbox("Insumo exclusivo")
                ativo = col2.checkbox("Produto ativo", value=True)
                criticidade_manual = st.selectbox(
                    "Criticidade manual",
                    ["Automática", "baixa", "média", "alta", "crítica"],
                )

                st.subheader("Estoque inicial")
                e1, e2, e3 = st.columns(3)
                quantidade_atual = e1.number_input("Quantidade atual", min_value=0.0, value=0.0)
                estoque_minimo = e2.number_input("Estoque mínimo / cota", min_value=0.0, value=0.0)
                estoque_maximo = e3.number_input("Estoque máximo", min_value=0.0, value=0.0)
                consumo_medio = e1.number_input("Consumo médio mensal (CMM)", min_value=0.0, value=0.0)
                lote = e2.text_input("Lote")
                validade = e3.date_input("Validade", value=None)
                local = st.text_input("Local de armazenamento")
                observacoes = st.text_area("Observações, processo de compra e ata")

                if st.form_submit_button("Salvar produto", use_container_width=True):
                    if not descricao.strip():
                        st.error("Informe a descrição do produto.")
                    else:
                        try:
                            insumo = Insumo(
                                codigo=_texto(codigo),
                                descricao=descricao.strip(),
                                categoria=_texto(categoria),
                                subcategoria=_texto(subcategoria),
                                unidade_medida=_texto(unidade),
                                fornecedor_principal=_texto(fornecedor),
                                fabricante=_texto(fabricante),
                                marca=_texto(marca),
                                exclusivo=exclusivo,
                                ativo=ativo,
                                criticidade_manual=None if criticidade_manual == "Automática" else criticidade_manual,
                                observacoes=_texto(observacoes),
                                dados_origem="Cadastro manual no sistema",
                            )
                            session.add(insumo)
                            session.flush()
                            estoque = Estoque(
                                insumo_id=insumo.id,
                                quantidade_atual=quantidade_atual,
                                estoque_minimo=estoque_minimo,
                                estoque_maximo=estoque_maximo or None,
                                consumo_medio_mensal=consumo_medio or None,
                                lote=_texto(lote),
                                validade=validade if isinstance(validade, date) else None,
                                local_armazenamento=_texto(local),
                                data_ultima_contagem=date.today(),
                                atualizado_por=user["id"],
                            )
                            atualizar_calculos(estoque)
                            session.add(estoque)
                            registrar(
                                session,
                                user["id"],
                                "insumo",
                                insumo.id,
                                "criação",
                                depois={"codigo": insumo.codigo, "descricao": insumo.descricao},
                            )
                            st.success("Produto incluído com sucesso.")
                        except IntegrityError:
                            session.rollback()
                            st.error("Já existe um produto com esse código.")

        df = df_insumos(session)
        searchable_table(df, "insumos")

        itens = list(session.execute(select(Insumo).order_by(Insumo.descricao)).scalars())
        options = {f"{i.codigo or 'sem código'} - {i.descricao[:90]}": i.id for i in itens}
        if not options:
            st.info("Nenhum produto cadastrado.")
            return

        selected = st.selectbox("Abrir produto", options.keys())
        insumo = session.get(Insumo, options[selected])
        estoque = insumo.estoque

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Estoque atual", estoque.quantidade_atual if estoque else 0)
        c2.metric("Estoque mínimo", estoque.estoque_minimo if estoque else 0)
        c3.metric("Cobertura", estoque.cobertura_dias if estoque and estoque.cobertura_dias is not None else "-")
        c4.metric("Criticidade", insumo.criticidade_manual or criticidade(estoque, insumo))

        d1, d2 = st.columns(2)
        with d1:
            st.write(f"**Categoria:** {insumo.categoria or '-'}")
            st.write(f"**Subcategoria:** {insumo.subcategoria or '-'}")
            st.write(f"**Unidade:** {insumo.unidade_medida or '-'}")
            st.write(f"**Exclusivo:** {'Sim' if insumo.exclusivo else 'Não'}")
        with d2:
            st.write(f"**Fabricante:** {insumo.fabricante or '-'}")
            st.write(f"**Marca:** {insumo.marca or '-'}")
            st.write(f"**Fornecedor:** {insumo.fornecedor_principal or '-'}")
            st.write(f"**Local:** {estoque.local_armazenamento if estoque and estoque.local_armazenamento else '-'}")
        st.write(insumo.observacoes or "Sem observações registradas.")

        if user.get("perfil") == "administrador":
            with st.expander("Excluir produto", expanded=False):
                st.warning("A exclusão remove o estoque e as movimentações do produto. Processos e atas permanecem, mas ficam sem vínculo com o item.")
                confirmar = st.checkbox(
                    f"Confirmo a exclusão de {insumo.codigo or ''} - {insumo.descricao}",
                    key=f"confirmar_exclusao_{insumo.id}",
                )
                if st.button("Excluir definitivamente", type="primary", disabled=not confirmar, use_container_width=True):
                    dados_anteriores = {"codigo": insumo.codigo, "descricao": insumo.descricao}
                    session.execute(update(ProcessoCompra).where(ProcessoCompra.insumo_id == insumo.id).values(insumo_id=None))
                    session.execute(update(ItemAta).where(ItemAta.insumo_id == insumo.id).values(insumo_id=None))
                    session.execute(delete(Alerta).where(Alerta.insumo_id == insumo.id))
                    session.execute(delete(MovimentacaoEstoque).where(MovimentacaoEstoque.insumo_id == insumo.id))
                    session.delete(insumo)
                    session.flush()
                    registrar(session, user["id"], "insumo", options[selected], "exclusão", antes=dados_anteriores)
                    st.success("Produto excluído com sucesso. Atualize a página para renovar a lista.")
