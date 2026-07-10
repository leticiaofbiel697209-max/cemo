from __future__ import annotations

from config.database import Base, engine, get_session
from config.settings import INITIAL_ADMIN_EMAIL, INITIAL_ADMIN_PASSWORD
from database.models import Usuario
from services.auth_service import hash_password


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        exists = session.query(Usuario).filter_by(email=INITIAL_ADMIN_EMAIL).first()
        if not exists:
            session.add(
                Usuario(
                    nome="Administrador",
                    email=INITIAL_ADMIN_EMAIL,
                    senha_hash=hash_password(INITIAL_ADMIN_PASSWORD),
                    perfil="administrador",
                    setor="Administração",
                    ativo=True,
                    trocar_senha=True,
                )
            )


if __name__ == "__main__":
    init_db()
    print("Banco inicializado com sucesso.")
