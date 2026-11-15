from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import Optional, List
from datetime import date, datetime


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- CATEGORIA ---
class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class Categoria(CategoriaCreate, ORMModel):
    id: int

# --- PRODUCTO ---
class ProductoCreate(BaseModel):
    nombre: str
    categoria_id: int
    precio: float = Field(ge=0)
    stock: int = Field(default=0, ge=0)   # referencia: se sincroniza con los lotes vigentes
    requiere_receta: bool = False

class Producto(ProductoCreate, ORMModel):
    id: int

# --- CLIENTE ---
class ClienteCreate(BaseModel):
    nombre: str
    telefono: str
    identidad: str

class Cliente(ClienteCreate, ORMModel):
    id: int

# --- PROVEEDOR ---
class ProveedorCreate(BaseModel):
    razon_social: str
    ruc: str
    contacto: str
    telefono: Optional[str] = None

class Proveedor(ProveedorCreate, ORMModel):
    id: int

# --- USUARIO ---
class UsuarioCreate(BaseModel):
    username: str
    password: str
    rol: str = "empleado"

class UsuarioOut(ORMModel):
    """Lo que se devuelve al cliente: nunca incluye la contraseña ni su hash."""
    id: int
    username: str
    rol: str

Usuario = UsuarioOut

# --- DETALLE QUE VIENE DENTRO DE LA VENTA ---
class DetalleVentaEnVentaCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)
    
    precio_unitario: Optional[float] = None

# --- VENTA ---
class VentaCreate(BaseModel):
    fecha: Optional[datetime] = None          
    total: Optional[float] = None             
    cliente_id: int
    usuario_id: Optional[int] = None          
    detalles: List[DetalleVentaEnVentaCreate] = []

class Venta(ORMModel):
    id: int
    fecha: datetime
    total: float
    cliente_id: int
    usuario_id: int

    @field_serializer('fecha')
    def serializar_fecha(self, fecha: datetime):
        return fecha.strftime("%Y-%m-%dT%H:%M:%S")

# --- DETALLE VENTA (uso directo, solo administrador) ---
class DetalleVentaCreate(BaseModel):
    venta_id: int
    lote_id: int
    cantidad: int
    precio_unitario: float

class DetalleVenta(DetalleVentaCreate, ORMModel):
    id: int

# --- LOTE ---
class LoteCreate(BaseModel):
    producto_id: int
    numero_lote: str
    proveedor_id: int
    fecha_vencimiento: date
    cantidad: int
    precio_compra: float

class Lote(LoteCreate, ORMModel):
    id: int
