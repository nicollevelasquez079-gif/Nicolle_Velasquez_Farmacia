from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from servicios.lote import LoteServicio
import esquemas

# El token se exige en main.py para todo este router
router = APIRouter()

# LISTAR LOTES
@router.get("/")
def listar(db: Session = Depends(get_db)):
    return LoteServicio.listar(db)

# POR VENCER (reto propio)
@router.get("/por-vencer")
def listar_por_vencer(dias: int = 30, db: Session = Depends(get_db)):
    try:
        return LoteServicio.obtener_por_vencer(db, dias)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

# LISTAR POR PRODUCTO - FEFO: vence primero, sale primero
@router.get("/producto/{producto_id}")
def listar_por_producto(producto_id: int, db: Session = Depends(get_db)):
    return LoteServicio.listar_por_producto(db, producto_id)

# CREAR LOTE
@router.post("/")
def crear(lote: esquemas.LoteCreate, db: Session = Depends(get_db)):
    try:
        return LoteServicio.crear(db, lote)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

# ACTUALIZAR LOTE
@router.put("/{lote_id}")
def actualizar(lote_id: int, lote: esquemas.LoteCreate, db: Session = Depends(get_db)):
    try:
        return LoteServicio.actualizar(db, lote_id, lote)
    except ValueError as error:
        codigo = 404 if str(error) == "Lote no encontrado" else 400
        raise HTTPException(status_code=codigo, detail=str(error))

# ELIMINAR LOTE
@router.delete("/{lote_id}")
def eliminar(lote_id: int, db: Session = Depends(get_db)):
    try:
        LoteServicio.eliminar(db, lote_id)
        return {"mensaje": "Lote eliminado correctamente"}
    except ValueError as error:
        codigo = 404 if str(error) == "Lote no encontrado" else 400
        raise HTTPException(status_code=codigo, detail=str(error))
