from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.models.tarefa import Tarefa, StatusTarefa, PrioridadeTarefa


class TarefaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, usuario_id: int, dados: dict) -> Tarefa:
        tarefa = Tarefa(usuario_id=usuario_id, **dados)
        self.db.add(tarefa)
        await self.db.flush()
        await self.db.refresh(tarefa)
        return tarefa

    async def buscar_por_id(self, tarefa_id: int) -> Tarefa | None:
        result = await self.db.execute(
            select(Tarefa).where(Tarefa.id == tarefa_id)
        )
        return result.scalar_one_or_none()

    async def listar(
        self,
        usuario_id: int,
        pagina: int = 1,
        limite: int = 20,
        status: Optional[StatusTarefa] = None,
        prioridade: Optional[PrioridadeTarefa] = None,
        concluida: Optional[bool] = None,
    ) -> tuple[list[Tarefa], int]:
        query = select(Tarefa).where(Tarefa.usuario_id == usuario_id)

        if status:     query = query.where(Tarefa.status == status)
        if prioridade: query = query.where(Tarefa.prioridade == prioridade)
        if concluida is not None: query = query.where(Tarefa.concluida == concluida)

        total_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.scalar()

        result = await self.db.execute(
            query.order_by(Tarefa.criado_em.desc())
                 .offset((pagina - 1) * limite)
                 .limit(limite)
        )
        return result.scalars().all(), total

    async def atualizar(self, tarefa: Tarefa, dados: dict) -> Tarefa:
        for campo, valor in dados.items():
            if valor is not None:
                setattr(tarefa, campo, valor)
        await self.db.flush()
        await self.db.refresh(tarefa)
        return tarefa

    async def deletar(self, tarefa: Tarefa) -> None:
        await self.db.delete(tarefa)
        await self.db.flush()
