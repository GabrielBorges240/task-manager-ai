from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.database import get_db
from app.services.auth import get_current_user_id
from app.models.tarefa import Tarefa, StatusTarefa
from app.schemas.ml import (
    PrevisaoPrioridadeRequest, PrevisaoPrioridadeResponse,
    PrevisaoCategoriaRequest, PrevisaoCategoriaResponse,
    InsightsResponse,
)
from app.ml import (
    prever_prioridade,
    prever_categoria,
    calcular_score_produtividade,
    prever_demanda_semanal,
    analisar_horario_pico,
)

router = APIRouter(prefix="/ai", tags=["AI / ML"])


@router.post("/prioridade", response_model=PrevisaoPrioridadeResponse)
async def sugerir_prioridade(dados: PrevisaoPrioridadeRequest):
    """
    Sugere a prioridade de uma tarefa com base no título e descrição.
    Usa Naive Bayes + TF-IDF treinado com dados rotulados.
    """
    resultado = prever_prioridade(
        titulo=dados.titulo,
        descricao=dados.descricao or "",
    )
    return resultado


@router.post("/categoria", response_model=PrevisaoCategoriaResponse)
async def sugerir_categoria(dados: PrevisaoCategoriaRequest):
    """
    Classifica automaticamente a categoria de uma tarefa.
    Retorna a categoria sugerida + top 3 com confiança.
    """
    resultado = prever_categoria(
        titulo=dados.titulo,
        descricao=dados.descricao or "",
    )
    return resultado


@router.get("/insights", response_model=InsightsResponse)
async def meus_insights(
    usuario_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna insights de produtividade do usuário:
    - Score de produtividade (0-100)
    - Previsão de demanda para a próxima semana
    - Horário de pico de criação de tarefas
    """
    hoje = datetime.utcnow()
    trinta_dias_atras = hoje - timedelta(days=30)

    # Buscar todas as tarefas dos últimos 30 dias
    result = await db.execute(
        select(Tarefa).where(
            Tarefa.usuario_id == usuario_id,
            Tarefa.criado_em >= trinta_dias_atras,
        )
    )
    tarefas = result.scalars().all()

    # Contadores para produtividade
    total       = len(tarefas)
    concluidas  = sum(1 for t in tarefas if t.concluida)
    em_progresso = sum(1 for t in tarefas if t.status == StatusTarefa.em_progresso)
    atrasadas   = sum(
        1 for t in tarefas
        if t.prazo and t.prazo < hoje and not t.concluida
    )

    produtividade = calcular_score_produtividade(
        total_tarefas=total,
        concluidas=concluidas,
        em_progresso=em_progresso,
        atrasadas=atrasadas,
    )

    # Historico diário dos últimos 28 dias para previsão
    historico = []
    for i in range(27, -1, -1):
        dia = hoje - timedelta(days=i)
        prox_dia = dia + timedelta(days=1)
        qtd = sum(
            1 for t in tarefas
            if t.criado_em and dia.date() == t.criado_em.date()
        )
        historico.append(qtd)

    demanda = prever_demanda_semanal(historico)

    # Horário de pico
    horarios = [
        t.criado_em.hour
        for t in tarefas
        if t.criado_em
    ]
    horario_pico = analisar_horario_pico(horarios)

    return {
        "produtividade": produtividade,
        "demanda": demanda,
        "horario_pico": horario_pico,
    }
