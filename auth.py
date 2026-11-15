import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from modelos.usuario import Usuario

# La clave real va en una variable de entorno: set SECRET_KEY=algo-largo-y-secreto
SECRET_KEY = os.getenv("SECRET_KEY", "clave-solo-para-desarrollo-cambiala")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

ROLES_ADMIN = {"admin", "administrador"}

# tokenUrl apunta al login que acepta formulario, así el botón "Authorize" de Swagger funciona
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def verificar_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, TypeError):
        # el valor guardado no es un hash bcrypt válido
        return False


def crear_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def crear_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o vencido")

    user = db.query(Usuario).filter(Usuario.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no existe")
    return user


def es_admin(user: Usuario) -> bool:
    return (user.rol or "").strip().lower() in ROLES_ADMIN


def solo_admin(user: Usuario = Depends(get_current_user)):
    if not es_admin(user):
        raise HTTPException(status_code=403, detail="Solo un administrador puede hacer esto")
    return user
