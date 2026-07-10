from __future__ import annotations

import streamlit as st

from config.settings import CRITICAL_COVERAGE_DAYS, EXPIRY_ALERT_DAYS, PROCESS_STALE_DAYS, WARNING_COVERAGE_DAYS
from utils.constants import PERMISSOES


def render(user: dict) -> None:
    st.title("Configurações")
    st.caption("No MVP, os parâmetros são exibidos e devem ser persistidos via `.env`. A próxima versão pode mover essas regras para tabela editável.")
    st.number_input("Limite crítico de cobertura", value=CRITICAL_COVERAGE_DAYS)
    st.number_input("Limite de atenção", value=WARNING_COVERAGE_DAYS)
    st.number_input("Dias para processo parado", value=PROCESS_STALE_DAYS)
    st.number_input("Prazo de alerta de vencimento", value=EXPIRY_ALERT_DAYS)
    st.subheader("Permissões")
    st.json({k: sorted(v) for k, v in PERMISSOES.items()})
