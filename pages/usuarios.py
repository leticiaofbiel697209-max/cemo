from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import select

from config.database import get_session
from database.models import Usuario
from services.auth_service import hash_password
from utils.constants import PERFIS
from utils.validators import valid_email


def render(user: dict) -> None:
    st.title("Usuários")
    if user["perfil"] != "administrador":
        st.warning("Somente administradores editam usuários.")
        return
    with get_session() as session:
        with st.form("user"):
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha inicial", type="password")
            perfil = st.selectbox("Perfil", PERFIS)
            setor = st.text_input("Setor")
            if st.form_submit_button("Criar usuário"):
                if not valid_email(email):
                    st.error("E-mail inválido.")
                else:
                    session.add(Usuario(nome=nome, email=email.lower(), senha_hash=hash_password(senha), perfil=perfil, setor=setor, ativo=True))
                    st.success("Usuário criado.")
        users = session.execute(select(Usuario)).scalars().all()
        st.dataframe(pd.DataFrame([{c.name: getattr(u, c.name) for c in Usuario.__table__.columns if c.name != "senha_hash"} for u in users]), use_container_width=True, hide_index=True)
