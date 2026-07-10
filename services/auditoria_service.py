from __future__ import annotations

import json

from database.models import Auditoria


def registrar(session, usuario_id: int | None, entidade: str, entidade_id, acao: str, antes=None, depois=None, ip=None) -> None:
    session.add(
        Auditoria(
            usuario_id=usuario_id,
            entidade=entidade,
            entidade_id=str(entidade_id) if entidade_id is not None else None,
            acao=acao,
            dados_anteriores=json.dumps(antes, default=str, ensure_ascii=False) if antes is not None else None,
            dados_novos=json.dumps(depois, default=str, ensure_ascii=False) if depois is not None else None,
            ip_origem=ip,
        )
    )
