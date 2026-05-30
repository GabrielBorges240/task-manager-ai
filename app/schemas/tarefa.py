from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.tarefa import StatusTarefa, PrioridadeTarefa


class TarefaCriar(BaseModel):
    titulo:     str = Field(..., min_length=1, max_length=200)
    descricao:  Optional[str] = Field(None, max_length=1000)
    prioridade: PrioridadeTarefa = PrioridadeTarefa.media
    prazo:      Optional[datetime] = None


class TarefaAtualizar(BaseModel):
    titulo:     Optional[str] = Field(None, min_length=1, max_length=200)
    descricao:  Optional[str] = Field(None, max_length=1000)
    status:     Optional[StatusTarefa] = None
    prioridade: Optional[PrioridadeTarefa] = None
    prazo:      Optional[datetime] = None
    concluida:  Optional[bool] = None


class TarefaResposta(BaseModel):
    id:          int
    titulo:      str
    descricao:   Optional[str]
    status:      StatusTarefa
    prioridade:  PrioridadeTarefa
    prazo:       Optional[datetime]
    concluida:   bool
    usuario_id:  int
    criado_em:   datetime
    atualizado:  Optional[datetime]

    model_config = {"from_attributes": True}


class TarefaListagem(BaseModel):
    total:   int
    pagina:  int
    limite:  int
    itens:   list[TarefaResposta]
