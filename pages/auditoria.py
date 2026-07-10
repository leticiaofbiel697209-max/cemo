from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import select

from config.database import get_session
from database.models import Auditoria


def render(user: dict) -> None:
    st.title("Auditoria")
    with get_session() as session:
        rows = session.execute(select(Auditoria).order_by(Auditoria.criado_em.desc()).limit(1000)).scalars().all()
        st.dataframe(pd.DataFrame([{c.name: getattr(a, c.name) for c in Auditoria.__table__.columns} for a in rows]), use_container_width=True, hide_index=True)
