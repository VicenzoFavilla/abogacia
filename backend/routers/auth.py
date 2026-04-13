"""
Router de autenticación — registro, login, perfil.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.database import get_db
from backend.models.usuario import Usuario
from backend.services.auth_service import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Schemas ──────────────────────────────────────────────────────────────────

class RegistroIn(BaseModel):
    nombre: str
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario_id: int
    nombre: str
    email: str


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str
    es_admin: bool

    class Config:
        from_attributes = True


# ── Dependency: usuario actual ────────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    user = db.query(Usuario).filter(Usuario.id == payload.get("sub")).first()
    if not user or not user.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user


def get_optional_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[Usuario]:
    """Versión opcional — no falla si no hay token (endpoints públicos)."""
    try:
        return get_current_user(token, db)
    except Exception:
        return None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenOut, status_code=201)
def registrar(datos: RegistroIn, db: Session = Depends(get_db)):
    """Registra un nuevo usuario y devuelve un JWT."""
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        hashed_password=hash_password(datos.password),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    token = create_access_token({"sub": usuario.id})
    return TokenOut(access_token=token, usuario_id=usuario.id, nombre=usuario.nombre, email=usuario.email)


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Inicia sesión con email + contraseña (form OAuth2). Devuelve JWT."""
    usuario = db.query(Usuario).filter(Usuario.email == form.username).first()
    if not usuario or not verify_password(form.password, usuario.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_access_token({"sub": usuario.id})
    return TokenOut(access_token=token, usuario_id=usuario.id, nombre=usuario.nombre, email=usuario.email)


@router.get("/me", response_model=UsuarioOut)
def perfil(current_user: Usuario = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    return current_user
