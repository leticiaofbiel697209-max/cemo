from __future__ import annotations

from datetime import date

from database.models import Estoque, MovimentacaoEstoque
from services.auditoria_service import registrar


def calcular_consumo_diario(consumo_medio_mensal: float | None) -> float | None:
    if not consumo_medio_mensal:
        return None
    return round(consumo_medio_mensal / 30, 4)


def calcular_cobertura(quantidade_atual: float | None, consumo_medio_mensal: float | None) -> float | None:
    diario = calcular_consumo_diario(consumo_medio_mensal)
    if not diario:
        return None
    return round((quantidade_atual or 0) / diario, 2)


def atualizar_calculos(estoque: Estoque) -> None:
    estoque.consumo_medio_diario = calcular_consumo_diario(estoque.consumo_medio_mensal)
    estoque.cobertura_dias = calcular_cobertura(estoque.quantidade_atual, estoque.consumo_medio_mensal)
    estoque.ponto_reposicao = round((estoque.consumo_medio_diario or 0) * 15, 2) if estoque.consumo_medio_diario else None


def registrar_movimentacao(
    session,
    estoque: Estoque,
    tipo: str,
    quantidade: float,
    usuario_id: int | None,
    motivo: str | None = None,
    permitir_negativo: bool = False,
    lote: str | None = None,
    validade: date | None = None,
):
    saldo_anterior = estoque.quantidade_atual or 0
    delta = quantidade if tipo in {"entrada", "devolução", "inventário"} else -quantidade
    saldo_posterior = quantidade if tipo == "inventário" else saldo_anterior + delta
    if saldo_posterior < 0 and not permitir_negativo:
        raise ValueError("A movimentação deixaria o estoque negativo.")
    estoque.quantidade_atual = saldo_posterior
    if lote:
        estoque.lote = lote
    if validade:
        estoque.validade = validade
    estoque.atualizado_por = usuario_id
    atualizar_calculos(estoque)
    mov = MovimentacaoEstoque(
        insumo_id=estoque.insumo_id,
        tipo_movimentacao=tipo,
        quantidade=quantidade,
        saldo_anterior=saldo_anterior,
        saldo_posterior=saldo_posterior,
        lote=lote,
        validade=validade,
        motivo=motivo,
        usuario_id=usuario_id,
    )
    session.add(mov)
    registrar(session, usuario_id, "estoque", estoque.insumo_id, "movimentação", {"saldo": saldo_anterior}, {"saldo": saldo_posterior, "tipo": tipo})
    return mov
