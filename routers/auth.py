from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from modelos.usuario import Usuario
from auth import verificar_password, crear_token

router = APIRouter()

class LoginRequest(BaseModel):
    usuario: str
    clave: str

@router.post("/login", summary="Iniciar Sesion",
    description="Valida usuario y contraseña contra la tabla 'usuarios'. No usa tokens ni sesiones, por ahora el cliente simplemente guarda en memoria los datos del usuario que inició sesión."
)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == datos.usuario).first()
    if not user or not verificar_password(datos.clave, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return {
    "access_token": crear_token({"sub": user.username}),
    "token_type": "bearer",
    "id": user.id,
    "usuario": user.username,
    "rol": user.rol
}