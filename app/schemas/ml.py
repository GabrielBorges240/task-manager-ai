from pydantic import BaseModel, Field
from typing import Optional


class PrevisaoPrioridadeRequest(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=1000)


class PrevisaoPrioridadeResponse(BaseModel):
    prioridade_sugerida: str
    confianca: dict[str, float]
    confianca_maxima: float


class PrevisaoCategoriaRequest(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=1000)


class CategoriaTop3(BaseModel):
    categoria: str
    confianca: float


class PrevisaoCategoriaResponse(BaseModel):
    categoria_sugerida: str
    top3: list[CategoriaTop3]
    confianca_maxima: float


class ProdutividadeDetalhes(BaseModel):
    taxa_conclusao: float
    taxa_em_progresso: float
    taxa_atraso: float


class ProdutividadeResponse(BaseModel):
    score: float
    nivel: str
    detalhes: ProdutividadeDetalhes


class DemandaResponse(BaseModel):
    previsao_semana: float
    media_diaria: float
    tendencia: str
    base_calculo_dias: int


class HorarioPicoResponse(BaseModel):
    hora_pico: Optional[int]
    periodo_pico: str
    distribuicao: dict[str, int]


class InsightsResponse(BaseModel):
    produtividade: ProdutividadeResponse
    demanda: DemandaResponse
    horario_pico: HorarioPicoResponse
