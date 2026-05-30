# Task Manager AI

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

```
Título + Descrição
       ↓
  Pré-processamento (lowercase, strip)
       ↓
  TF-IDF Vectorizer (n-gramas 1-2)
       ↓
  Naive Bayes (prioridade) / Logistic Regression (categoria)
       ↓
  Prioridade ou Categoria + Confiança
```

## Testes

```bash
pip install -r requirements.txt aiosqlite pytest-asyncio
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Estrutura

```
task-manager-ai/
├── app/
│   ├── main.py
│   ├── ml/
│   │   ├── modelo_prioridade.py
│   │   ├── modelo_categoria.py
│   │   └── modelo_produtividade.py
│   ├── routers/ml.py
│   └── schemas/ml.py
├── tests/integration/test_ml.py
├── Dockerfile
└── docker-compose.yml
```

## Autor

Gabriel Borges — [@GabrielBorges240](https://github.com/GabrielBorges240)

> **Projeto Integrador II** — Ciência da Computação UFMS
