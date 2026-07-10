from __future__ import annotations

import streamlit as st

from services.auth_service import can_access

PAGES = [
    ("dashboard", "Dashboard"),
    ("insumos", "Insumos"),
    ("estoque", "Estoque"),
    ("compras", "Compras e Processos"),
    ("atas", "Atas e Contratos"),
    ("alertas", "Alertas"),
    ("relatorios", "Relatórios"),
    ("importar", "Importar planilha"),
    ("usuarios", "Usuários"),
    ("auditoria", "Auditoria"),
    ("configuracoes", "Configurações"),
]


def render_sidebar(user: dict) -> str:
    st.sidebar.markdown("### CEMO/INCA")
    st.sidebar.caption(f"{user['nome']} | {user['perfil']}")
    allowed = [(key, label) for key, label in PAGES if can_access(user["perfil"], key) or key == "importar" and user["perfil"] == "administrador"]
    page = st.sidebar.radio("Menu", allowed, format_func=lambda item: item[1], label_visibility="collapsed")
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    return page[0]
