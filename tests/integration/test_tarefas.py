import pytest


@pytest.mark.asyncio
async def test_criar_tarefa(client, usuario_e_token):
    r = await client.post("/tarefas", json={
        "titulo": "Estudar FastAPI",
        "descricao": "Ver documentação oficial",
        "prioridade": "alta"
    }, headers=usuario_e_token["headers"])
    assert r.status_code == 201
    data = r.json()
    assert data["titulo"] == "Estudar FastAPI"
    assert data["status"] == "pendente"
    assert data["concluida"] is False


@pytest.mark.asyncio
async def test_listar_tarefas(client, usuario_e_token):
    # Cria 2 tarefas
    for i in range(2):
        await client.post("/tarefas", json={
            "titulo": f"Tarefa {i}", "prioridade": "media"
        }, headers=usuario_e_token["headers"])

    r = await client.get("/tarefas", headers=usuario_e_token["headers"])
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "itens" in data
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_buscar_tarefa_por_id(client, usuario_e_token):
    criada = await client.post("/tarefas", json={
        "titulo": "Tarefa específica", "prioridade": "baixa"
    }, headers=usuario_e_token["headers"])
    tarefa_id = criada.json()["id"]

    r = await client.get(f"/tarefas/{tarefa_id}", headers=usuario_e_token["headers"])
    assert r.status_code == 200
    assert r.json()["id"] == tarefa_id


@pytest.mark.asyncio
async def test_atualizar_tarefa(client, usuario_e_token):
    criada = await client.post("/tarefas", json={
        "titulo": "Antes", "prioridade": "baixa"
    }, headers=usuario_e_token["headers"])
    tarefa_id = criada.json()["id"]

    r = await client.patch(f"/tarefas/{tarefa_id}", json={
        "titulo": "Depois",
        "status": "em_progresso",
        "concluida": True
    }, headers=usuario_e_token["headers"])
    assert r.status_code == 200
    assert r.json()["titulo"] == "Depois"
    assert r.json()["status"] == "em_progresso"
    assert r.json()["concluida"] is True


@pytest.mark.asyncio
async def test_deletar_tarefa(client, usuario_e_token):
    criada = await client.post("/tarefas", json={
        "titulo": "Para deletar", "prioridade": "baixa"
    }, headers=usuario_e_token["headers"])
    tarefa_id = criada.json()["id"]

    r = await client.delete(f"/tarefas/{tarefa_id}", headers=usuario_e_token["headers"])
    assert r.status_code == 204

    r = await client.get(f"/tarefas/{tarefa_id}", headers=usuario_e_token["headers"])
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_nao_acessa_tarefa_alheia(client):
    """BOLA — usuário não pode acessar tarefa de outro"""
    # Usuário 1
    await client.post("/auth/registro", json={
        "nome": "User1", "email": "u1@t.com", "senha": "123456"
    })
    r1 = await client.post("/auth/login", json={"email": "u1@t.com", "senha": "123456"})
    h1 = {"Authorization": f"Bearer {r1.json()['access_token']}"}

    # Usuário 2
    await client.post("/auth/registro", json={
        "nome": "User2", "email": "u2@t.com", "senha": "123456"
    })
    r2 = await client.post("/auth/login", json={"email": "u2@t.com", "senha": "123456"})
    h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}

    # User1 cria tarefa
    criada = await client.post("/tarefas", json={
        "titulo": "Tarefa privada", "prioridade": "alta"
    }, headers=h1)
    tarefa_id = criada.json()["id"]

    # User2 tenta acessar — deve receber 403
    r = await client.get(f"/tarefas/{tarefa_id}", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_filtrar_tarefas_por_status(client, usuario_e_token):
    await client.post("/tarefas", json={
        "titulo": "Pendente", "prioridade": "baixa"
    }, headers=usuario_e_token["headers"])

    r = await client.get("/tarefas?status=pendente", headers=usuario_e_token["headers"])
    assert r.status_code == 200
    for item in r.json()["itens"]:
        assert item["status"] == "pendente"
