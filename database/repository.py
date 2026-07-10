from __future__ import annotations

from sqlalchemy import func, select

from database.models import Alerta, AtaContrato, Estoque, Insumo, ProcessoCompra, Usuario


def list_insumos(session):
    return session.execute(select(Insumo).order_by(Insumo.descricao)).scalars().all()


def get_insumo_options(session) -> dict[str, int]:
    rows = session.execute(select(Insumo.id, Insumo.codigo, Insumo.descricao).order_by(Insumo.descricao)).all()
    return {f"{codigo or 'sem código'} - {descricao[:80]}": item_id for item_id, codigo, descricao in rows}


def dashboard_counts(session) -> dict[str, float]:
    total_insumos = session.scalar(select(func.count(Insumo.id)).where(Insumo.ativo.is_(True))) or 0
    sem_estoque = session.scalar(select(func.count(Estoque.id)).where(Estoque.quantidade_atual <= 0)) or 0
    baixo_minimo = session.scalar(select(func.count(Estoque.id)).where(Estoque.quantidade_atual < Estoque.estoque_minimo)) or 0
    cobertura_15 = session.scalar(select(func.count(Estoque.id)).where(Estoque.cobertura_dias <= 15)) or 0
    cobertura_30 = session.scalar(select(func.count(Estoque.id)).where(Estoque.cobertura_dias > 15, Estoque.cobertura_dias <= 30)) or 0
    processos = session.scalar(select(func.count(ProcessoCompra.id)).where(ProcessoCompra.status.notin_(["concluído", "cancelado"]))) or 0
    atas = session.scalar(select(func.count(AtaContrato.id)).where(AtaContrato.status == "vigente")) or 0
    alertas = session.scalar(select(func.count(Alerta.id)).where(Alerta.status == "pendente")) or 0
    valor_aberto = session.scalar(select(func.sum(ProcessoCompra.valor_estimado)).where(ProcessoCompra.status != "concluído")) or 0
    return {
        "total_insumos": total_insumos,
        "sem_estoque": sem_estoque,
        "baixo_minimo": baixo_minimo,
        "cobertura_15": cobertura_15,
        "cobertura_30": cobertura_30,
        "processos": processos,
        "atas": atas,
        "alertas": alertas,
        "valor_aberto": valor_aberto,
    }


def get_user_by_email(session, email: str) -> Usuario | None:
    return session.execute(select(Usuario).where(Usuario.email == email.lower().strip())).scalar_one_or_none()
