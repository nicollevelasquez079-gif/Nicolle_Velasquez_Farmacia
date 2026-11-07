from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from servicios.usuario import UsuarioServicio
import esquemas

router = APIRouter()

# LISTAR USUARIOS
@router.get("/")
def listar(db: Session = Depends(get_db)):
    return UsuarioServicio.listar(db)

# CREAR USUARIO
@router.post("/")
def crear(usuario: esquemas.UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return UsuarioServicio.crear(db, usuario)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

# ACTUALIZAR USUARIO
@router.put("/{usuario_id}")
def actualizar(
    usuario_id: int,
    usuario: esquemas.UsuarioCreate,
    db: Session = Depends(get_db)
):
    try:
        return UsuarioServicio.actualizar(db, usuario_id, usuario)
    except ValueError as error:
        codigo = 404 if str(error) == "Usuario no encontrado" else 400
        raise HTTPException(status_code=codigo, detail=str(error))

# ELIMINAR USUARIO
@router.delete("/{usuario_id}")
def eliminar(usuario_id: int, db: Session = Depends(get_db)):
    try:
        UsuarioServicio.eliminar(db, usuario_id)
        return {"mensaje": "Usuario eliminado correctamente"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))