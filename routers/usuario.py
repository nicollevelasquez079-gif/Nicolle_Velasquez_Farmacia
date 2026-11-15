from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from servicios.usuario import UsuarioServicio
import esquemas

# Todo este router es solo para administradores (se exige en main.py)
router = APIRouter()

@router.get("/", response_model=List[esquemas.UsuarioOut])
def listar(db: Session = Depends(get_db)):
    return UsuarioServicio.listar(db)

@router.post("/", response_model=esquemas.UsuarioOut)
def crear(usuario: esquemas.UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return UsuarioServicio.crear(db, usuario)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.put("/{usuario_id}", response_model=esquemas.UsuarioOut)
def actualizar(usuario_id: int, usuario: esquemas.UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return UsuarioServicio.actualizar(db, usuario_id, usuario)
    except ValueError as error:
        codigo = 404 if str(error) == "Usuario no encontrado" else 400
        raise HTTPException(status_code=codigo, detail=str(error))

@router.delete("/{usuario_id}")
def eliminar(usuario_id: int, db: Session = Depends(get_db)):
    try:
        UsuarioServicio.eliminar(db, usuario_id)
        return {"mensaje": "Usuario eliminado correctamente"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
