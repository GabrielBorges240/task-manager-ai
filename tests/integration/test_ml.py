import pytest


@pytest.mark.asyncio
async def test_sugerir_prioridade_alta(client):
    r = await client.post("/ai/prioridade", json={
        "titulo": "bug critico sistema fora do ar producao",
        "descricao": "servidor caindo clientes bloqueados urgente"
    })
    assert r.status_code == 200
    data = r.json()
    assert "prioridade_sugerida" in data
    assert data["prioridade_sugerida"] in ["baixa", "media", "alta"]
    assert "confianca" in data
    assert "confianca_maxima" in data
    assert 0 <= data["confianca_maxima"] <= 1


@pytest.mark.asyncio
async def test_sugerir_prioridade_baixa(client):
    r = await client.post("/ai/prioridade", json={
        "titulo": "organizar arquivos antigos",
        "descricao": "limpar pasta downloads"
    })
    assert r.status_code == 200
    data = r.json()
    assert data["prioridade_sugerida"] in ["baixa", "media", "alta"]


@pytest.mark.asyncio
async def test_sugerir_prioridade_sem_descricao(client):
    r = await client.post("/ai/prioridade", json={
        "titulo": "corrigir bug pagamento"
    })
    assert r.status_code == 200
    assert "prioridade_sugerida" in r.json()


@pytest.mark.asyncio
async def test_sugerir_prioridade_titulo_vazio(client):
    r = await client.post("/ai/prioridade", json={"titulo": ""})
    assert r.status_code == 422  # validação Pydantic


@pytest.mark.asyncio
async def test_sugerir_categoria_desenvolvimento(client):
    r = await client.post("/ai/categoria", json={
        "titulo": "implementar endpoint api rest usuario",
        "descricao": "criar rota fastapi com autenticacao jwt"
    })
    assert r.status_code == 200
    data = r.json()
    assert "categoria_sugerida" in data
    assert "top3" in data
    assert len(data["top3"]) == 3
    assert all("categoria" in item and "confianca" in item for item in data["top3"])


@pytest.mark.asyncio
async def test_sugerir_categoria_bug(client):
    r = await client.post("/ai/categoria", json={
        "titulo": "corrigir erro login usuarios",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["categoria_sugerida"] in [
        "bug", "desenvolvimento", "devops",
        "documentacao", "reuniao", "estudo", "design", "outro"
    ]


@pytest.mark.asyncio
async def test_sugerir_categoria_devops(client):
    r = await client.post("/ai/categoria", json={
        "titulo": "configurar pipeline ci cd github actions docker"
    })
    assert r.status_code == 200
    assert "categoria_sugerida" in r.json()


@pytest.mark.asyncio
async def test_insights_sem_token(client):
    r = await client.get("/ai/insights")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_insights_usuario_sem_tarefas(client, usuario_e_token):
    r = await client.get("/ai/insights", headers=usuario_e_token["headers"])
    assert r.status_code == 200
    data = r.json()
    assert "produtividade" in data
    assert "demanda" in data
    assert "horario_pico" in data
    assert data["produtividade"]["score"] == 0


@pytest.mark.asyncio
async def test_insights_usuario_com_tarefas(client, usuario_e_token):
    # Cria e conclui algumas tarefas
    for i in range(3):
        criada = await client.post("/tarefas", json={
            "titulo": f"Tarefa {i}", "prioridade": "media"
        }, headers=usuario_e_token["headers"])
        tid = criada.json()["id"]
        await client.patch(f"/tarefas/{tid}", json={
            "concluida": True, "status": "concluida"
        }, headers=usuario_e_token["headers"])

    r = await client.get("/ai/insights", headers=usuario_e_token["headers"])
    assert r.status_code == 200
    data = r.json()
    assert data["produtividade"]["score"] > 0
    assert data["produtividade"]["nivel"] in ["excelente", "bom", "regular", "precisa melhorar"]
    assert data["demanda"]["tendencia"] in ["crescente", "decrescente", "estavel", "sem dados"]
