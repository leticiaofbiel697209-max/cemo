from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base


class TimestampMixin:
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(40), default="consulta")
    setor: Mapped[str | None] = mapped_column(String(120))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime)
    trocar_senha: Mapped[bool] = mapped_column(Boolean, default=True)


class Insumo(Base, TimestampMixin):
    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    descricao: Mapped[str] = mapped_column(Text, index=True)
    categoria: Mapped[str | None] = mapped_column(String(120))
    subcategoria: Mapped[str | None] = mapped_column(String(120))
    unidade_medida: Mapped[str | None] = mapped_column(String(40))
    fabricante: Mapped[str | None] = mapped_column(String(160))
    marca: Mapped[str | None] = mapped_column(String(160))
    fornecedor_principal: Mapped[str | None] = mapped_column(String(160))
    exclusivo: Mapped[bool] = mapped_column(Boolean, default=False)
    criticidade_manual: Mapped[str | None] = mapped_column(String(40))
    criticidade_automatica: Mapped[str | None] = mapped_column(String(40))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    observacoes: Mapped[str | None] = mapped_column(Text)
    dados_origem: Mapped[str | None] = mapped_column(Text)

    estoque = relationship("Estoque", back_populates="insumo", uselist=False, cascade="all, delete-orphan")


class Estoque(Base):
    __tablename__ = "estoques"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    insumo_id: Mapped[int] = mapped_column(ForeignKey("insumos.id"), unique=True)
    quantidade_atual: Mapped[float] = mapped_column(Float, default=0)
    estoque_minimo: Mapped[float] = mapped_column(Float, default=0)
    estoque_maximo: Mapped[float | None] = mapped_column(Float)
    consumo_medio_mensal: Mapped[float | None] = mapped_column(Float)
    consumo_medio_diario: Mapped[float | None] = mapped_column(Float)
    cobertura_dias: Mapped[float | None] = mapped_column(Float)
    ponto_reposicao: Mapped[float | None] = mapped_column(Float)
    lote: Mapped[str | None] = mapped_column(String(120))
    validade: Mapped[date | None] = mapped_column(Date)
    local_armazenamento: Mapped[str | None] = mapped_column(String(160))
    data_ultima_contagem: Mapped[date | None] = mapped_column(Date)
    atualizado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    insumo = relationship("Insumo", back_populates="estoque")


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    insumo_id: Mapped[int] = mapped_column(ForeignKey("insumos.id"))
    tipo_movimentacao: Mapped[str] = mapped_column(String(40))
    quantidade: Mapped[float] = mapped_column(Float)
    saldo_anterior: Mapped[float] = mapped_column(Float)
    saldo_posterior: Mapped[float] = mapped_column(Float)
    lote: Mapped[str | None] = mapped_column(String(120))
    validade: Mapped[date | None] = mapped_column(Date)
    motivo: Mapped[str | None] = mapped_column(Text)
    documento_referencia: Mapped[str | None] = mapped_column(String(160))
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class ProcessoCompra(Base, TimestampMixin):
    __tablename__ = "processos_compra"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero_processo: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    insumo_id: Mapped[int | None] = mapped_column(ForeignKey("insumos.id"))
    descricao: Mapped[str | None] = mapped_column(Text)
    quantidade_solicitada: Mapped[float | None] = mapped_column(Float)
    quantidade_comprada: Mapped[float | None] = mapped_column(Float)
    setor_solicitante: Mapped[str | None] = mapped_column(String(120))
    solicitante: Mapped[str | None] = mapped_column(String(160))
    etapa_atual: Mapped[str] = mapped_column(String(80), default="solicitação")
    status: Mapped[str] = mapped_column(String(80), default="aberto")
    prioridade: Mapped[str] = mapped_column(String(40), default="média")
    data_solicitacao: Mapped[date | None] = mapped_column(Date)
    data_abertura: Mapped[date | None] = mapped_column(Date)
    previsao_compra: Mapped[date | None] = mapped_column(Date)
    previsao_entrega: Mapped[date | None] = mapped_column(Date)
    data_recebimento: Mapped[date | None] = mapped_column(Date)
    fornecedor: Mapped[str | None] = mapped_column(String(160))
    valor_estimado: Mapped[float | None] = mapped_column(Float)
    valor_comprado: Mapped[float | None] = mapped_column(Float)
    observacoes: Mapped[str | None] = mapped_column(Text)
    responsavel_atual: Mapped[str | None] = mapped_column(String(160))


class AtaContrato(Base, TimestampMixin):
    __tablename__ = "atas_contratos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero_ata: Mapped[str] = mapped_column(String(120), unique=True)
    numero_processo: Mapped[str | None] = mapped_column(String(120))
    fornecedor: Mapped[str | None] = mapped_column(String(160))
    objeto: Mapped[str | None] = mapped_column(Text)
    data_inicio: Mapped[date | None] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)
    valor_total: Mapped[float | None] = mapped_column(Float)
    saldo_disponivel: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(80), default="vigente")
    observacoes: Mapped[str | None] = mapped_column(Text)


class ItemAta(Base):
    __tablename__ = "itens_atas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ata_id: Mapped[int] = mapped_column(ForeignKey("atas_contratos.id"))
    insumo_id: Mapped[int | None] = mapped_column(ForeignKey("insumos.id"))
    quantidade_total: Mapped[float | None] = mapped_column(Float)
    quantidade_utilizada: Mapped[float | None] = mapped_column(Float, default=0)
    quantidade_disponivel: Mapped[float | None] = mapped_column(Float)
    valor_unitario: Mapped[float | None] = mapped_column(Float)
    valor_total: Mapped[float | None] = mapped_column(Float)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class Alerta(Base):
    __tablename__ = "alertas"
    __table_args__ = (UniqueConstraint("tipo", "insumo_id", "processo_id", "ata_id", "status", name="uq_alerta_pendente"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo: Mapped[str] = mapped_column(String(80))
    titulo: Mapped[str] = mapped_column(String(180))
    descricao: Mapped[str | None] = mapped_column(Text)
    nivel: Mapped[str] = mapped_column(String(40))
    insumo_id: Mapped[int | None] = mapped_column(ForeignKey("insumos.id"))
    processo_id: Mapped[int | None] = mapped_column(ForeignKey("processos_compra.id"))
    ata_id: Mapped[int | None] = mapped_column(ForeignKey("atas_contratos.id"))
    status: Mapped[str] = mapped_column(String(40), default="pendente")
    responsavel: Mapped[str | None] = mapped_column(String(160))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    resolvido_em: Mapped[datetime | None] = mapped_column(DateTime)
    resolvido_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    observacao_resolucao: Mapped[str | None] = mapped_column(Text)


class Auditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    entidade: Mapped[str] = mapped_column(String(80))
    entidade_id: Mapped[str | None] = mapped_column(String(80))
    acao: Mapped[str] = mapped_column(String(80))
    dados_anteriores: Mapped[str | None] = mapped_column(Text)
    dados_novos: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    ip_origem: Mapped[str | None] = mapped_column(String(80))


class ImportacaoPlanilha(Base):
    __tablename__ = "importacoes_planilha"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_arquivo: Mapped[str] = mapped_column(String(255))
    abas_processadas: Mapped[int] = mapped_column(Integer, default=0)
    registros_importados: Mapped[int] = mapped_column(Integer, default=0)
    registros_ignorados: Mapped[int] = mapped_column(Integer, default=0)
    relatorio: Mapped[str | None] = mapped_column(Text)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

