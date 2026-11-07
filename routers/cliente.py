from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from servicios.cliente import ClienteServicio
import esquemas

router = APIRouter()

# LISTAR CLIENTES
@router.get("/")
def listar(db: Session = Depends(get_db)):
    return ClienteServicio.listar(db)

# CREAR CLIENTE
@router.post("/")
def crear(cliente: esquemas.ClienteCreate, db: Session = Depends(get_db)):
    try:
        return ClienteServicio.crear(db, cliente)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

# ACTUALIZAR CLIENTE
@router.put("/{cliente_id}")
def actualizar(
    cliente_id: int,
    cliente: esquemas.ClienteCreate,
    db: Session = Depends(get_db)
):
    try:
        return ClienteServicio.actualizar(db, cliente_id, cliente)
    except ValueError as error:
        codigo = 404 if str(error) == "Cliente no encontrado" else 400
        raise HTTPException(status_code=codigo, detail=str(error))

# ELIMINAR CLIENTE
@router.delete("/{cliente_id}")
def eliminar(cliente_id: int, db: Session = Depends(get_db)):
    try:
        ClienteServicio.eliminar(db, cliente_id)
        return {"mensaje": "Cliente eliminado correctamente"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))