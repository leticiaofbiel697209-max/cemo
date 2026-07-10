from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import select

from config.settings import CRITICAL_COVERAGE_DAYS, EXPIRY_ALERT_DAYS, PROCESS_STALE_DAYS, WARNING_COVERAGE_DAYS
from database.models import Alerta, AtaContrato, Estoque, Insumo, ProcessoCompra
from services.auditoria_service import registrar
from utils.helpers import days_between


def criticidade(estoque: Estoque | None, insumo: Insumo | None = None) -> str:
    if estoque and (estoque.quantidade_atual or 0) <= 0:
        return "crítico"
    if estoque and estoque.cobertura_dias is not None:
        if estoque.cobertura_dias <= CRITICAL_COVERAGE_DAYS:
            return "crítico"
        if estoque.cobertura_dias <= WARNING_COVERAGE_DAYS:
            return "alto"
        if estoque.cobertura_dias <= 60:
            return "médio"
    if estoque and estoque.quantidade_atual < (estoque.estoque_minimo or 0):
        return "alto"
    if insumo and insumo.criticidade_manual:
        return insumo.criticidade_manual
    return "normal"


def _pendente(session, tipo, insumo_id=None, processo_id=None, ata_id=None) -> bool:
    return session.execute(
        select(Alerta).where(
            Alerta.tipo == tipo,
            Alerta.insumo_id == insumo_id,
            Alerta.processo_id == processo_id,
            Alerta.ata_id == ata_id,
            Alerta.status == "pendente",
        )
    ).first() is not None


def criar_alerta(session, tipo, titulo, descricao, nivel, usuario_id=None, insumo_id=None, processo_id=None, ata_id=None):
    if _pendente(session, tipo, insumo_id, processo_id, ata_id):
        return None
    alerta = Alerta(tipo=tipo, titulo=titulo, descricao=descricao, nivel=nivel, insumo_id=insumo_id, processo_id=processo_id, ata_id=ata_id)
    session.add(alerta)
    registrar(session, usuario_id, "alerta", None, "criação", depois={"tipo": tipo, "titulo": titulo})
    return alerta


def gerar_alertas(session, usuario_id: int | None = None) -> int:
    total = 0
    for estoque, insumo in session.execute(select(Estoque, Insumo).join(Insumo, Estoque.insumo_id == Insumo.id)).all():
        insumo.criticidade_automatica = criticidade(estoque, insumo)
        if (estoque.quantidade_atual or 0) <= 0 and criar_alerta(session, "estoque_zerado", f"Estoque zerado: {insumo.descricao[:80]}", "Item sem saldo disponível.", "crítico", usuario_id, insumo.id):
            total += 1
        if estoque.quantidade_atual < (estoque.estoque_minimo or 0) and criar_alerta(session, "estoque_minimo", f"Abaixo do mínimo: {insumo.descricao[:80]}", "Saldo inferior ao estoque mínimo.", "alto", usuario_id, insumo.id):
            total += 1
        if estoque.cobertura_dias is not None and estoque.cobertura_dias <= CRITICAL_COVERAGE_DAYS and criar_alerta(session, "cobertura_baixa", f"Cobertura baixa: {insumo.descricao[:80]}", f"Cobertura estimada de {estoque.cobertura_dias} dias.", "crítico", usuario_id, insumo.id):
            total += 1
        if estoque.validade and 0 <= (estoque.validade - date.today()).days <= EXPIRY_ALERT_DAYS and criar_alerta(session, "validade_proxima", f"Validade próxima: {insumo.descricao[:80]}", f"Lote vence em {estoque.validade:%d/%m/%Y}.", "alto", usuario_id, insumo.id):
            total += 1
    for processo in session.execute(select(ProcessoCompra).where(ProcessoCompra.status.notin_(["concluído", "cancelado"]))).scalars():
        parado = days_between(processo.atualizado_em)
        if parado and parado > PROCESS_STALE_DAYS and criar_alerta(session, "processo_parado", f"Processo parado: {processo.numero_processo}", f"Sem atualização há {parado} dias.", "alto", usuario_id, processo_id=processo.id):
            total += 1
        if processo.previsao_entrega and processo.previsao_entrega < date.today() and not processo.data_recebimento and criar_alerta(session, "entrega_atrasada", f"Entrega atrasada: {processo.numero_processo}", "Previsão de entrega vencida.", "crítico", usuario_id, processo_id=processo.id):
            total += 1
    for ata in session.execute(select(AtaContrato)).scalars():
        if ata.data_fim and ata.data_fim < date.today() and criar_alerta(session, "ata_vencida", f"Ata vencida: {ata.numero_ata}", "Ata/contrato com vigência encerrada.", "crítico", usuario_id, ata_id=ata.id):
            total += 1
        elif ata.data_fim and ata.data_fim <= date.today() + timedelta(days=EXPIRY_ALERT_DAYS) and criar_alerta(session, "ata_vencendo", f"Ata vencendo: {ata.numero_ata}", "Ata/contrato vence em até 30 dias.", "alto", usuario_id, ata_id=ata.id):
            total += 1
    return total


def resolver_alerta(session, alerta: Alerta, usuario_id: int, observacao: str | None = None) -> None:
    alerta.status = "resolvido"
    alerta.resolvido_em = datetime.now()
    alerta.resolvido_por = usuario_id
    alerta.observacao_resolucao = observacao
    registrar(session, usuario_id, "alerta", alerta.id, "resolução", depois={"observacao": observacao})
