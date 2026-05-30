from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import auth, usuarios, tarefas, ml
from app.ml.modelo_prioridade import carregar_modelo as carregar_prioridade
from app.ml.modelo_categoria import carregar_modelo as carregar_categoria


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pré-carrega modelos de ML na inicialização
    print("Carregando modelos de ML...")
    carregar_prioridade()
    carregar_categoria()
    print("Modelos prontos!")
    yield


app = FastAPI(
    title="Task Manager AI",
    description="""
API REST com camada de **Inteligência Artificial** para gerenciamento de tarefas.

## Funcionalidades de AI

- **Sugestão de prioridade** — Naive Bayes + TF-IDF
- **Classificação de categoria** — Regressão Logística + TF-IDF
- **Insights de produtividade** — Score, previsão de demanda e horário de pico

## Autenticação

Use o endpoint `/auth/login` para obter um token JWT e clique em **Authorize**.
    """,
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(tarefas.router)
app.include_router(ml.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "versao": "2.0.0",
        "ai": True,
        "modelos": ["prioridade", "categoria", "produtividade"],
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
