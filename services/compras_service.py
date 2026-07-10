from __future__ import annotations

from database.models import ProcessoCompra
from services.auditoria_service import registrar


def alterar_etapa(session, processo: ProcessoCompra, nova_etapa: str, usuario_id: int | None, observacao: str | None = None) -> None:
    anterior = processo.etapa_atual
    processo.etapa_atual = nova_etapa
    registrar(
        session,
        usuario_id,
        "processo_compra",
        processo.id,
        "alteração de etapa",
        {"etapa": anterior},
        {"etapa": nova_etapa, "observacao": observacao},
    )
