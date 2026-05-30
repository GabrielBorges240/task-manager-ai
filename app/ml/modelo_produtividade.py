"""
Análise de produtividade e previsão de demanda.

Funcionalidades:
  - Taxa de conclusão por período
  - Previsão de quantas tarefas serão criadas na próxima semana
  - Horário de pico de criação de tarefas
  - Score de produtividade do usuário
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Optional


def calcular_score_produtividade(
    total_tarefas: int,
    concluidas: int,
    em_progresso: int,
    atrasadas: int,
) -> dict:
    """
    Score de 0 a 100 baseado em taxa de conclusão e atrasos.
    """
    if total_tarefas == 0:
        return {"score": 0, "nivel": "sem dados", "detalhes": {}}

    taxa_conclusao  = concluidas / total_tarefas
    taxa_progresso  = em_progresso / total_tarefas
    taxa_atraso     = atrasadas / total_tarefas

    score = (
        taxa_conclusao  * 60   # conclusão vale 60%
        + taxa_progresso * 20  # em progresso vale 20%
        - taxa_atraso    * 30  # atraso penaliza 30%
    ) * 100

    score = max(0.0, min(100.0, score))

    if score >= 80:
        nivel = "excelente"
    elif score >= 60:
        nivel = "bom"
    elif score >= 40:
        nivel = "regular"
    else:
        nivel = "precisa melhorar"

    return {
        "score": round(score, 1),
        "nivel": nivel,
        "detalhes": {
            "taxa_conclusao":  round(taxa_conclusao * 100, 1),
            "taxa_em_progresso": round(taxa_progresso * 100, 1),
            "taxa_atraso":     round(taxa_atraso * 100, 1),
        },
    }


def prever_demanda_semanal(historico_diario: list[int]) -> dict:
    """
    Prevê quantas tarefas serão criadas na próxima semana
    usando média móvel ponderada dos últimos 28 dias.

    historico_diario: lista com contagem de tarefas por dia (mais antigo → mais recente)
    """
    if not historico_diario:
        return {"previsao_semana": 0, "media_diaria": 0, "tendencia": "sem dados"}

    dados = np.array(historico_diario[-28:], dtype=float)

    # Pesos exponenciais — dias mais recentes pesam mais
    pesos = np.exp(np.linspace(0, 1, len(dados)))
    pesos /= pesos.sum()

    media_ponderada = float(np.dot(dados, pesos))

    # Tendência: comparar primeira metade vs segunda metade
    metade = len(dados) // 2
    if metade > 0:
        media_antiga  = float(dados[:metade].mean())
        media_recente = float(dados[metade:].mean())
        if media_recente > media_antiga * 1.1:
            tendencia = "crescente"
        elif media_recente < media_antiga * 0.9:
            tendencia = "decrescente"
        else:
            tendencia = "estavel"
    else:
        tendencia = "estavel"

    previsao_semana = round(media_ponderada * 7, 1)

    return {
        "previsao_semana":  previsao_semana,
        "media_diaria":     round(media_ponderada, 2),
        "tendencia":        tendencia,
        "base_calculo_dias": len(dados),
    }


def analisar_horario_pico(horarios_criacao: list[int]) -> dict:
    """
    Identifica em quais horas do dia o usuário mais cria tarefas.

    horarios_criacao: lista de horas (0-23) de quando as tarefas foram criadas
    """
    if not horarios_criacao:
        return {"hora_pico": None, "periodo_pico": "sem dados", "distribuicao": {}}

    contagem = {}
    for hora in horarios_criacao:
        contagem[hora] = contagem.get(hora, 0) + 1

    hora_pico = max(contagem, key=contagem.get)

    if 5 <= hora_pico < 12:
        periodo = "manha"
    elif 12 <= hora_pico < 18:
        periodo = "tarde"
    elif 18 <= hora_pico < 23:
        periodo = "noite"
    else:
        periodo = "madrugada"

    # Agrupa por período
    periodos = {"manha": 0, "tarde": 0, "noite": 0, "madrugada": 0}
    for hora, qtd in contagem.items():
        if 5 <= hora < 12:   periodos["manha"]     += qtd
        elif 12 <= hora < 18: periodos["tarde"]     += qtd
        elif 18 <= hora < 23: periodos["noite"]     += qtd
        else:                 periodos["madrugada"] += qtd

    return {
        "hora_pico":    hora_pico,
        "periodo_pico": periodo,
        "distribuicao": periodos,
    }
