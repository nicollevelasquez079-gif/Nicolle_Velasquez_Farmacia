from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from servicios.producto import ProductoServicio
import esquemas

router = APIRouter()


# LISTAR PRODUCTOS
@router.get("/")
def listar(db: Session = Depends(get_db)):
    return ProductoServicio.listar(db)


# CREAR PRODUCTO
@router.post("/")
def crear(producto: esquemas.ProductoCreate, db: Session = Depends(get_db)):
    try:
        return ProductoServicio.crear(db, producto)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# ACTUALIZAR PRODUCTO
@router.put("/{producto_id}")
def actualizar(
    producto_id: int,
    producto: esquemas.ProductoCreate,
    db: Session = Depends(get_db)
):
    try:
        return ProductoServicio.actualizar(db, producto_id, producto)
    except ValueError as error:
        codigo = 404 if str(error) == "Producto no encontrado" else 400
        raise HTTPException(status_code=codigo, detail=str(error))


# ELIMINAR PRODUCTO
@router.delete("/{producto_id}")
def eliminar(producto_id: int, db: Session = Depends(get_db)):
    try:
        ProductoServicio.eliminar(db, producto_id)
        return {"mensaje": "Producto eliminado correctamente"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))