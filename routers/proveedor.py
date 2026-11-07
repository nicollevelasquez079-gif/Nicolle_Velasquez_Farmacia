from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from servicios.proveedor import ProveedorServicio
import esquemas

router = APIRouter()

# LISTAR PROVEEDORES
@router.get("/")
def listar(db: Session = Depends(get_db)):
    return ProveedorServicio.listar(db)

# CREAR PROVEEDOR
@router.post("/")
def crear(proveedor: esquemas.ProveedorCreate, db: Session = Depends(get_db)):
    try:
        return ProveedorServicio.crear(db, proveedor)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

# ACTUALIZAR PROVEEDOR
@router.put("/{proveedor_id}")
def actualizar(
    proveedor_id: int,
    proveedor: esquemas.ProveedorCreate,
    db: Session = Depends(get_db)
):
    try:
        return ProveedorServicio.actualizar(db, proveedor_id, proveedor)
    except ValueError as error:
        codigo = 404 if str(error) == "Proveedor no encontrado" else 400
        raise HTTPException(status_code=codigo, detail=str(error))

# ELIMINAR PROVEEDOR
@router.delete("/{proveedor_id}")
def eliminar(proveedor_id: int, db: Session = Depends(get_db)):
    try:
        ProveedorServicio.eliminar(db, proveedor_id)
        return {"mensaje": "Proveedor eliminado correctamente"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))