from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from modelos.usuario import Usuario
from auth import verificar_password, crear_token

router = APIRouter()

class LoginRequest(BaseModel):
    usuario: str
    clave: str


def _autenticar(db: Session, username: str, clave: str) -> Usuario:
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user or not verificar_password(clave, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return user


@router.post("/login", summary="Iniciar sesión",
    description="Valida usuario y contraseña y devuelve un token JWT. "
                "El frontend debe enviarlo en el header 'Authorization: Bearer <token>'.")
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    user = _autenticar(db, datos.usuario, datos.clave)
    return {
        "access_token": crear_token({"sub": user.username}),
        "token_type": "bearer",
        "id": user.id,
        "usuario": user.username,
        "rol": user.rol
    }


@router.post("/token", summary="Login con formulario (para el botón Authorize de Swagger)")
def login_formulario(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = _autenticar(db, form.username, form.password)
    return {"access_token": crear_token({"sub": user.username}), "token_type": "bearer"}
