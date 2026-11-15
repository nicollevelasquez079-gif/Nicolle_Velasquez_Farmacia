from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from servicios.venta import VentaServicio
from auth import get_current_user, solo_admin
import esquemas

# El token se exige en main.py para todo este router
router = APIRouter()

# LISTAR VENTAS
@router.get("/", response_model=list[esquemas.Venta])
def listar(db: Session = Depends(get_db)):
    return VentaServicio.listar(db)

# OBTENER VENTA POR ID
@router.get("/{venta_id}", response_model=esquemas.Venta)
def obtener(venta_id: int, db: Session = Depends(get_db)):
    try:
        return VentaServicio.obtener_por_id(db, venta_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

# CREAR VENTA (descuenta stock por FEFO; el total lo calcula el servidor)
@router.post("/", response_model=esquemas.Venta)
def crear(venta: esquemas.VentaCreate, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    try:
        return VentaServicio.crear(db, venta, usuario)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

# ACTUALIZAR VENTA (solo admin)
@router.put("/{venta_id}", response_model=esquemas.Venta)
def actualizar(venta_id: int, venta: esquemas.VentaCreate,
               db: Session = Depends(get_db), admin=Depends(solo_admin)):
    try:
        return VentaServicio.actualizar(db, venta_id, venta, admin)
    except ValueError as error:
        codigo = 404 if str(error) == "Venta no encontrada" else 400
        raise HTTPException(status_code=codigo, detail=str(error))

# ANULAR VENTA (solo admin; devuelve el stock a los lotes)
@router.delete("/{venta_id}")
def eliminar(venta_id: int, db: Session = Depends(get_db), admin=Depends(solo_admin)):
    try:
        VentaServicio.eliminar(db, venta_id)
        return {"mensaje": "Venta eliminada correctamente y stock devuelto a los lotes"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
