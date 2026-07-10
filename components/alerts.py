from __future__ import annotations

import streamlit as st


def warning_login() -> None:
    st.warning("Usuário inicial criado. Recomenda-se trocar a senha no primeiro acesso.")
