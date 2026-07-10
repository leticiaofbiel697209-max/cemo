from __future__ import annotations

import pandas as pd
from sqlalchemy import select

from database.models import Alerta, AtaContrato, Auditoria, Estoque, Insumo, MovimentacaoEstoque, ProcessoCompra


def df_insumos(session) -> pd.DataFrame:
    rows = session.execute(select(Insumo, Estoque).join(Estoque, Estoque.insumo_id == Insumo.id, isouter=True)).all()
    return pd.DataFrame(
        [
            {
                "Código": insumo.codigo,
                "Descrição": insumo.descricao,
                "Categoria": insumo.categoria,
                "Unidade": insumo.unidade_medida,
                "Fornecedor": insumo.fornecedor_principal,
                "Estoque atual": estoque.quantidade_atual if estoque else None,
                "Estoque mínimo": estoque.estoque_minimo if estoque else None,
                "Cobertura dias": estoque.cobertura_dias if estoque else None,
                "Criticidade": insumo.criticidade_manual or insumo.criticidade_automatica,
                "Atualizado em": insumo.atualizado_em,
            }
            for insumo, estoque in rows
        ]
    )


def dataframe_for(session, name: str) -> pd.DataFrame:
    if name == "insumos":
        return df_insumos(session)
    model_map = {
        "processos": ProcessoCompra,
        "atas": AtaContrato,
        "alertas": Alerta,
        "movimentacoes": MovimentacaoEstoque,
        "auditoria": Auditoria,
    }
    model = model_map[name]
    rows = session.execute(select(model)).scalars().all()
    return pd.DataFrame([{col.name: getattr(row, col.name) for col in model.__table__.columns} for row in rows])
