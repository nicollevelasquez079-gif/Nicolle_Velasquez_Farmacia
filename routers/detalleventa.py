from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from servicios.detalleventa import DetalleVentaServicio
import esquemas

router = APIRouter()

# LISTAR DETALLES
@router.get("/")
def listar(db: Session = Depends(get_db)):
    return DetalleVentaServicio.listar(db)

# LISTAR POR VENTA
@router.get("/venta/{venta_id}")
def listar_por_venta(venta_id: int, db: Session = Depends(get_db)):
    return DetalleVentaServicio.listar_por_venta(db, venta_id)

# CREAR DETALLE
@router.post("/")
def crear(detalle: esquemas.DetalleVentaCreate, db: Session = Depends(get_db)):
    try:
        return DetalleVentaServicio.crear(db, detalle)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

# ACTUALIZAR DETALLE
@router.put("/{detalle_id}")
def actualizar(
    detalle_id: int,
    detalle: esquemas.DetalleVentaCreate,
    db: Session = Depends(get_db)
):
    try:
        return DetalleVentaServicio.actualizar(db, detalle_id, detalle)
    except ValueError as error:
        codigo = 404 if str(error) == "DetalleVenta no encontrado" else 400
        raise HTTPException(status_code=codigo, detail=str(error))

# ELIMINAR DETALLE
@router.delete("/{detalle_id}")
def eliminar(detalle_id: int, db: Session = Depends(get_db)):
    try:
        DetalleVentaServicio.eliminar(db, detalle_id)
        return {"mensaje": "DetalleVenta eliminado correctamente"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))