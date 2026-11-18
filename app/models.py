from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Table
)
from sqlalchemy.orm import relationship

from .database import Base


# Relacionamento entre campanhas e contatos
campanha_contatos = Table(
    "campanha_contatos",
    Base.metadata,
    Column(
        "campanha_id",
        Integer,
        ForeignKey("campanhas.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "contato_id",
        Integer,
        ForeignKey("contatos.id", ondelete="CASCADE"),
        primary_key=True
    )
)


# Modelo de contatos
class Contato(Base):
    __tablename__ = "contatos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    telefone = Column(String(30), nullable=False)
    canal = Column(String(30), default="whatsapp")
    empresa_id = Column(String(100), nullable=False, index=True)

    campanhas = relationship(
        "Campanha",
        secondary=campanha_contatos,
        back_populates="contatos"
    )


# Modelo de campanhas
class Campanha(Base):
    __tablename__ = "campanhas"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(String(100), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    mensagem = Column(Text, default="")
    canal = Column(String(30), default="whatsapp")
    tipo_conteudo = Column(String(30), default="text")
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(100), nullable=True)
    legenda = Column(Text, default="")
    status = Column(String(30), default="rascunho")

    criada_em = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    contatos = relationship(
        "Contato",
        secondary=campanha_contatos,
        back_populates="campanhas"
    )

    historicos = relationship(
        "HistoricoCampanha",
        back_populates="campanha",
        cascade="all, delete-orphan"
    )


# Modelo de histórico das campanhas
class HistoricoCampanha(Base):
    __tablename__ = "historico_campanhas"

    id = Column(Integer, primary_key=True, index=True)

    campanha_id = Column(
        Integer,
        ForeignKey("campanhas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    nome = Column(String(200), nullable=False)
    status = Column(String(30), nullable=False)

    data = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    campanha = relationship(
        "Campanha",
        back_populates="historicos"
    )
