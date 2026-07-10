from __future__ import annotations

from pathlib import Path

import streamlit as st

from components.alerts import warning_login
from components.sidebar import render_sidebar
from config.database import get_session
from config.settings import APP_NAME
from database.init_db import init_db
from pages import alertas, atas, auditoria, compras, configuracoes, dashboard, estoque, importar, insumos, relatorios, usuarios
from services.auth_service import authenticate

st.set_page_config(page_title=APP_NAME, page_icon="CEMO", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #f6f8fb; }
    section[data-testid="stSidebar"] { background: #0f2d4a; color: white; }
    section[data-testid="stSidebar"] * { color: inherit; }
    div[data-testid="stMetric"] { background: white; border: 1px solid #dbe3ee; padding: 14px; border-radius: 8px; }
    .block-container { padding-top: 1.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()


def login_screen() -> None:
    st.title(APP_NAME)
    st.caption("Controle institucional de insumos, estoque e processos de compra.")
    with st.form("login"):
        email = st.text_input("E-mail", value="admin@cemo.local")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar", use_container_width=True)
    if submitted:
        with get_session() as session:
            user = authenticate(session, email, password)
            if not user:
                st.error("E-mail ou senha inválidos.")
                return
            st.session_state["user"] = {"id": user.id, "nome": user.nome, "email": user.email, "perfil": user.perfil, "trocar_senha": user.trocar_senha}
            st.rerun()


if "user" not in st.session_state:
    login_screen()
    st.stop()

user = st.session_state["user"]
if user.get("trocar_senha"):
    warning_login()

page = render_sidebar(user)
PAGES = {
    "dashboard": dashboard.render,
    "insumos": insumos.render,
    "estoque": estoque.render,
    "compras": compras.render,
    "atas": atas.render,
    "alertas": alertas.render,
    "relatorios": relatorios.render,
    "importar": importar.render,
    "usuarios": usuarios.render,
    "auditoria": auditoria.render,
    "configuracoes": configuracoes.render,
}
PAGES[page](user)
