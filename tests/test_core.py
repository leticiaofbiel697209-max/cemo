from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.database import Base
from database.models import Alerta, Estoque, Insumo, Usuario
from services.alertas_service import gerar_alertas, criticidade
from services.auth_service import authenticate, can_access, hash_password
from services.auditoria_service import registrar
from services.estoque_service import calcular_cobertura, registrar_movimentacao


def session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    return Session()


def test_login_and_user_creation():
    db = session()
    db.add(Usuario(nome="Teste", email="teste@cemo.local", senha_hash=hash_password("Senha@123"), perfil="administrador", ativo=True))
    db.commit()
    assert authenticate(db, "teste@cemo.local", "Senha@123") is not None
    assert authenticate(db, "teste@cemo.local", "errada") is None


def test_permissions():
    assert can_access("administrador", "usuarios")
    assert can_access("consulta", "relatorios")
    assert not can_access("consulta", "estoque")


def test_cobertura():
    assert calcular_cobertura(60, 30) == 60
    assert calcular_cobertura(10, 0) is None


def test_movimentacao_estoque_and_auditoria():
    db = session()
    insumo = Insumo(descricao="Item teste")
    db.add(insumo)
    db.flush()
    estoque = Estoque(insumo_id=insumo.id, quantidade_atual=10, estoque_minimo=5, consumo_medio_mensal=30)
    db.add(estoque)
    db.flush()
    registrar_movimentacao(db, estoque, "saída", 2, None, "teste")
    db.commit()
    assert estoque.quantidade_atual == 8
    assert db.query(Alerta).count() == 0


def test_criticidade_and_alertas():
    db = session()
    insumo = Insumo(descricao="Crítico")
    db.add(insumo)
    db.flush()
    estoque = Estoque(insumo_id=insumo.id, quantidade_atual=0, estoque_minimo=5, consumo_medio_mensal=30)
    db.add(estoque)
    db.commit()
    assert criticidade(estoque, insumo) == "crítico"
    assert gerar_alertas(db) >= 1


def test_auditoria():
    db = session()
    registrar(db, None, "teste", 1, "criação", depois={"ok": True})
    db.commit()
    assert db.execute(__import__("sqlalchemy").select(__import__("database.models").models.Auditoria)).first() is not None
