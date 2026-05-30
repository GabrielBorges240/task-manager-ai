from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.schemas.tarefa import TarefaCriar, TarefaAtualizar, TarefaResposta, TarefaListagem
from app.repositories.tarefa import TarefaRepository
from app.models.tarefa import StatusTarefa, PrioridadeTarefa
from app.services.auth import get_current_user_id

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])


@router.post("", response_model=TarefaResposta, status_code=status.HTTP_201_CREATED)
async def criar_tarefa(
    dados: TarefaCriar,
    usuario_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = TarefaRepository(db)
    return await repo.criar(usuario_id, dados.model_dump())


@router.get("", response_model=TarefaListagem)
async def listar_tarefas(
    pagina:    int                       = Query(1, ge=1),
    limite:    int                       = Query(20, ge=1, le=100),
    status:    Optional[StatusTarefa]    = None,
    prioridade: Optional[PrioridadeTarefa] = None,
    concluida: Optional[bool]            = None,
    usuario_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = TarefaRepository(db)
    itens, total = await repo.listar(
        usuario_id=usuario_id,
        pagina=pagina,
        limite=limite,
        status=status,
        prioridade=prioridade,
        concluida=concluida,
    )
    return {"total": total, "pagina": pagina, "limite": limite, "itens": itens}


@router.get("/{tarefa_id}", response_model=TarefaResposta)
async def buscar_tarefa(
    tarefa_id: int,
    usuario_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo   = TarefaRepository(db)
    tarefa = await repo.buscar_por_id(tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    if tarefa.usuario_id != usuario_id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    return tarefa


@router.patch("/{tarefa_id}", response_model=TarefaResposta)
async def atualizar_tarefa(
    tarefa_id: int,
    dados: TarefaAtualizar,
    usuario_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo   = TarefaRepository(db)
    tarefa = await repo.buscar_por_id(tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    if tarefa.usuario_id != usuario_id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    return await repo.atualizar(tarefa, dados.model_dump(exclude_none=True))


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_tarefa(
    tarefa_id: int,
    usuario_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo   = TarefaRepository(db)
    tarefa = await repo.buscar_por_id(tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    if tarefa.usuario_id != usuario_id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    await repo.deletar(tarefa)
