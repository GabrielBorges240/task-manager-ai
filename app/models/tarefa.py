from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class StatusTarefa(str, enum.Enum):
    pendente    = "pendente"
    em_progresso = "em_progresso"
    concluida   = "concluida"


class PrioridadeTarefa(str, enum.Enum):
    baixa  = "baixa"
    media  = "media"
    alta   = "alta"


class Tarefa(Base):
    __tablename__ = "tarefas"

    id          = Column(Integer, primary_key=True, index=True)
    titulo      = Column(String(200), nullable=False)
    descricao   = Column(String(1000))
    status      = Column(Enum(StatusTarefa), default=StatusTarefa.pendente, nullable=False)
    prioridade  = Column(Enum(PrioridadeTarefa), default=PrioridadeTarefa.media, nullable=False)
    prazo       = Column(DateTime(timezone=True), nullable=True)
    concluida   = Column(Boolean, default=False)
    usuario_id  = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    criado_em   = Column(DateTime(timezone=True), server_default=func.now())
    atualizado  = Column(DateTime(timezone=True), onupdate=func.now())

    usuario = relationship("Usuario", backref="tarefas")
