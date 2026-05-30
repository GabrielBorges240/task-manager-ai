from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.usuario import UsuarioResposta, UsuarioAtualizar
from app.repositories.usuario import UsuarioRepository
from app.services.auth import get_current_user_id

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("/me", response_model=UsuarioResposta)
async def meu_perfil(
    usuario_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo    = UsuarioRepository(db)
    usuario = await repo.buscar_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.patch("/me", response_model=UsuarioResposta)
async def atualizar_perfil(
    dados: UsuarioAtualizar,
    usuario_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo    = UsuarioRepository(db)
    usuario = await repo.buscar_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if dados.email and dados.email != usuario.email:
        if await repo.buscar_por_email(dados.email):
            raise HTTPException(status_code=400, detail="Email já em uso")

    return await repo.atualizar(usuario, dados.model_dump(exclude_none=True))
