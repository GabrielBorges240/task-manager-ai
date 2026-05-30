from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, nome: str, email: str, senha_hash: str) -> Usuario:
        usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash)
        self.db.add(usuario)
        await self.db.flush()
        await self.db.refresh(usuario)
        return usuario

    async def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        result = await self.db.execute(
            select(Usuario).where(Usuario.id == usuario_id)
        )
        return result.scalar_one_or_none()

    async def buscar_por_email(self, email: str) -> Usuario | None:
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email)
        )
        return result.scalar_one_or_none()

    async def atualizar(self, usuario: Usuario, dados: dict) -> Usuario:
        for campo, valor in dados.items():
            if valor is not None:
                setattr(usuario, campo, valor)
        await self.db.flush()
        await self.db.refresh(usuario)
        return usuario
