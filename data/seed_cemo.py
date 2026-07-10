from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from database.models import Estoque, Insumo, ProcessoCompra
from services.estoque_service import atualizar_calculos

_DATA_FILE = Path(__file__).with_name("seed_cemo.json")


def _carregar_dados() -> dict:
    if not _DATA_FILE.exists():
        return {"produtos": [], "processos": []}
    with _DATA_FILE.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _parse_date(valor):
    if not valor:
        return None
    try:
        return date.fromisoformat(str(valor)[:10])
    except (TypeError, ValueError):
        return None


def seed_cemo(session) -> None:
    dados = _carregar_dados()

    if session.query(Insumo).count() == 0:
        for item in dados.get("produtos", []):
            insumo = Insumo(
                codigo=item.get("codigo"),
                descricao=item.get("descricao") or "Sem descrição",
                categoria=item.get("categoria"),
                subcategoria=item.get("subcategoria"),
                unidade_medida=item.get("unidade_medida"),
                exclusivo=bool(item.get("exclusivo")),
                observacoes=item.get("observacoes"),
                dados_origem=json.dumps(item.get("dados_origem") or {}, ensure_ascii=False, default=str),
                ativo=True,
            )
            session.add(insumo)
            session.flush()

            estoque = Estoque(
                insumo_id=insumo.id,
                quantidade_atual=float(item.get("quantidade_atual") or 0),
                estoque_minimo=float(item.get("estoque_minimo") or 0),
                consumo_medio_mensal=(float(item["consumo_medio_mensal"]) if item.get("consumo_medio_mensal") not in (None, "") else None),
                local_armazenamento=item.get("local_armazenamento"),
            )
            atualizar_calculos(estoque)
            session.add(estoque)

    numeros_existentes = {n for (n,) in session.query(ProcessoCompra.numero_processo).all()}
    for item in dados.get("processos", []):
        numero = item.get("numero_processo")
        if not numero or numero in numeros_existentes:
            continue
        session.add(
            ProcessoCompra(
                numero_processo=numero,
                descricao=item.get("descricao"),
                etapa_atual=item.get("etapa_atual") or "solicitação",
                status=item.get("status") or "aberto",
                prioridade=item.get("prioridade") or "média",
                data_abertura=_parse_date(item.get("data_abertura")),
                observacoes=item.get("observacoes"),
                responsavel_atual=item.get("responsavel_atual"),
            )
        )
        numeros_existentes.add(numero)
