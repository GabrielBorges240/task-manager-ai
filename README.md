# Task Manager AI

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)
![Build](https://img.shields.io/badge/build-passing-brightgreen)

Evolução do [Task Manager API](https://github.com/GabrielBorges240/task-manager-api) com camada de **Inteligência Artificial** usando `scikit-learn`.

## Novas funcionalidades de AI

| Endpoint | Modelo | O que faz |
|----------|--------|-----------|
| `POST /ai/prioridade` | Naive Bayes + TF-IDF | Sugere prioridade da tarefa |
| `POST /ai/categoria` | Regressão Logística + TF-IDF | Classifica categoria automaticamente |
| `GET /ai/insights` | Estatístico | Score de produtividade + previsão de demanda |

## Tecnologias

- **FastAPI** — framework web assíncrono
- **scikit-learn** — modelos de ML (Naive Bayes, Logistic Regression)
- **TF-IDF** — vetorização de texto
- **PostgreSQL** + **SQLAlchemy** (async)
- **JWT** — autenticação
- **Docker + Docker Compose**
- **pytest** — testes automatizados

## Como rodar

```bash
git clone https://github.com/GabrielBorges240/task-manager-ai.git
cd task-manager-ai
docker-compose up -d
docker-compose exec api alembic upgrade head
# Documentação: http://localhost:8000/docs
```

## Configuração

Copie o arquivo `.env.example` para `.env` e preencha com suas próprias chaves antes de rodar o projeto.

## Exemplos de uso

### Sugerir prioridade

```bash
curl -X POST http://localhost:8000/ai/prioridade \
  -H "Content-Type: application/json" \
  -d '{"titulo": "bug critico sistema fora do ar", "descricao": "clientes bloqueados"}'
```

### Classificar categoria

```bash
curl -X POST http://localhost:8000/ai/categoria \
  -H "Content-Type: application/json" \
  -d '{"titulo": "configurar pipeline ci cd github actions"}'
```

### Insights de produtividade

```bash
curl http://localhost:8000/ai/insights \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Arquitetura de ML
