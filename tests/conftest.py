import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.database import Base, get_db

DATABASE_TEST_URL = "sqlite+aiosqlite:///./test.db"

engine_test = create_async_engine(DATABASE_TEST_URL, echo=False)
TestSession = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def criar_tabelas():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db():
    async with TestSession() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db):
    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def usuario_e_token(client):
    """Cria usuário e retorna token JWT"""
    await client.post("/auth/registro", json={
        "nome": "Ana Teste",
        "email": "ana@teste.com",
        "senha": "senha123"
    })
    r = await client.post("/auth/login", json={
        "email": "ana@teste.com",
        "senha": "senha123"
    })
    token = r.json()["access_token"]
    return {"token": token, "headers": {"Authorization": f"Bearer {token}"}}
