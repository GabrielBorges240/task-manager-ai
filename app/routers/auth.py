from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.usuario import LoginSchema, TokenResposta, UsuarioCriar, UsuarioResposta
from app.repositories.usuario import UsuarioRepository
from app.services.auth import hash_senha, verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registro", response_model=UsuarioResposta, status_code=status.HTTP_201_CREATED)
async def registrar(dados: UsuarioCriar, db: AsyncSession = Depends(get_db)):
    repo = UsuarioRepository(db)

    if await repo.buscar_por_email(dados.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    usuario = await repo.criar(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
    )
    return usuario


@router.post("/login", response_model=TokenResposta)
async def login(dados: LoginSchema, db: AsyncSession = Depends(get_db)):
    repo    = UsuarioRepository(db)
    usuario = await repo.buscar_por_email(dados.email)

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada"
        )

    token = criar_token(usuario.id, usuario.email)
    return {"access_token": token, "token_type": "bearer"}
