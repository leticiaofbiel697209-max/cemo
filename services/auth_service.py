from __future__ import annotations

from datetime import datetime

from passlib.context import CryptContext

from database.models import Usuario
from database.repository import get_user_by_email
from utils.constants import PERMISSOES

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def authenticate(session, email: str, password: str) -> Usuario | None:
    user = get_user_by_email(session, email)
    if not user or not user.ativo or not verify_password(password, user.senha_hash):
        return None
    user.ultimo_acesso = datetime.now()
    return user


def can_access(perfil: str, page_key: str) -> bool:
    allowed = PERMISSOES.get(perfil, set())
    return "*" in allowed or page_key in allowed
