from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from servicios.venta import VentaServicio
import esquemas

router = APIRouter()

# LISTAR VENTAS
@router.get("/")
def listar(db: Session = Depends(get_db)):
    return VentaServicio.listar(db)

# OBTENER VENTA POR ID
@router.get("/{venta_id}")
def obtener(venta_id: int, db: Session = Depends(get_db)):
    try:
        return VentaServicio.obtener_por_id(db, venta_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

# CREAR VENTA
@router.post("/", response_model=esquemas.Venta)
def crear(venta: esquemas.VentaCreate, db: Session = Depends(get_db)):
    try:
        return VentaServicio.crear(db, venta)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

# ACTUALIZAR VENTA
@router.put("/{venta_id}")
def actualizar(
    venta_id: int,
    venta: esquemas.VentaCreate,
    db: Session = Depends(get_db)
):
    try:
        return VentaServicio.actualizar(db, venta_id, venta)
    except ValueError as error:
        codigo = 404 if str(error) == "Venta no encontrada" else 400
        raise HTTPException(status_code=codigo, detail=str(error))

# ELIMINAR VENTA
@router.delete("/{venta_id}")
def eliminar(venta_id: int, db: Session = Depends(get_db)):
    try:
        VentaServicio.eliminar(db, venta_id)
        return {"mensaje": "Venta eliminada correctamente"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))