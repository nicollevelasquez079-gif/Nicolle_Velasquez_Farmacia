from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from servicios.categoria import CategoriaServicio
import esquemas
from typing import List

router = APIRouter()


# LISTAR CATEGORÍAS
@router.get("/", response_model=List[esquemas.Categoria])
def listar(db: Session = Depends(get_db)):
    return CategoriaServicio.listar(db)


# CREAR CATEGORÍA
@router.post("/", response_model=esquemas.Categoria)
def crear(cat: esquemas.CategoriaCreate, db: Session = Depends(get_db)):
    try:
        return CategoriaServicio.crear(
            db, cat.nombre, cat.descripcion
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# ACTUALIZAR CATEGORÍA
@router.put("/{categoria_id}", response_model=esquemas.Categoria)
def actualizar(
    categoria_id: int,
    categoria: esquemas.CategoriaCreate,
    db: Session = Depends(get_db)
):
    try:
        return CategoriaServicio.actualizar(
            db,
            categoria_id,
            categoria.nombre,
            categoria.descripcion
        )
    except ValueError as error:
        codigo = 404 if str(error) == "Categoría no encontrada" else 400
        raise HTTPException(status_code=codigo, detail=str(error))


# ELIMINAR CATEGORÍA
@router.delete("/{categoria_id}")
def eliminar(categoria_id: int, db: Session = Depends(get_db)):
    try:
        CategoriaServicio.eliminar(db, categoria_id)
        return {"mensaje": "Categoría eliminada correctamente"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))