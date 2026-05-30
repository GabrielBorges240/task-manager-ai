import pytest


@pytest.mark.asyncio
async def test_registro_sucesso(client):
    r = await client.post("/auth/registro", json={
        "nome": "Carlos Silva",
        "email": "carlos@teste.com",
        "senha": "senha123"
    })
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "carlos@teste.com"
    assert data["nome"] == "Carlos Silva"
    assert "senha" not in data
    assert "senha_hash" not in data


@pytest.mark.asyncio
async def test_registro_email_duplicado(client):
    payload = {"nome": "Bia", "email": "bia@teste.com", "senha": "senha123"}
    await client.post("/auth/registro", json=payload)
    r = await client.post("/auth/registro", json=payload)
    assert r.status_code == 400
    assert "Email já cadastrado" in r.json()["detail"]


@pytest.mark.asyncio
async def test_login_sucesso(client):
    await client.post("/auth/registro", json={
        "nome": "Joao", "email": "joao@teste.com", "senha": "senha123"
    })
    r = await client.post("/auth/login", json={
        "email": "joao@teste.com", "senha": "senha123"
    })
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_senha_errada(client):
    await client.post("/auth/registro", json={
        "nome": "Teste", "email": "err@teste.com", "senha": "correta"
    })
    r = await client.post("/auth/login", json={
        "email": "err@teste.com", "senha": "errada"
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_rota_sem_token(client):
    r = await client.get("/usuarios/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_perfil_com_token(client, usuario_e_token):
    r = await client.get("/usuarios/me", headers=usuario_e_token["headers"])
    assert r.status_code == 200
    assert r.json()["email"] == "ana@teste.com"
