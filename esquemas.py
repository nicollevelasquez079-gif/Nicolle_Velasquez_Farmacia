from pydantic import BaseModel, field_serializer
from typing import Optional, List
from datetime import date, datetime

# --- CATEGORIA ---
class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class Categoria(CategoriaCreate):
    id: int
    class Config:
        from_attributes = True

# --- PRODUCTO ---
class ProductoCreate(BaseModel):
    nombre: str
    categoria_id: int
    precio: float
    stock: int
    requiere_receta: bool = False

class Producto(ProductoCreate):
    id: int
    class Config:
        from_attributes = True

# --- CLIENTE ---
class ClienteCreate(BaseModel):
    nombre: str
    telefono: str
    identidad: str

class Cliente(ClienteCreate):
    id: int
    class Config:
        from_attributes = True

# --- PROVEEDOR ---
class ProveedorCreate(BaseModel):
    razon_social: str
    ruc: str
    contacto: str
    telefono: Optional[str] = None

class Proveedor(ProveedorCreate):
    id: int
    class Config:
        from_attributes = True

# --- USUARIO ---
class UsuarioCreate(BaseModel):
    username: str
    password: str
    rol: str = "empleado"

class Usuario(UsuarioCreate):
    id: int
    class Config:
        from_attributes = True

# --- DETALLE QUE VIENE DENTRO DE LA VENTA (FIFO) ---
class DetalleVentaEnVentaCreate(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float

# --- VENTA ---
class VentaCreate(BaseModel):
    fecha: datetime
    total: float
    cliente_id: int
    usuario_id: int
    detalles: List[DetalleVentaEnVentaCreate] = []  # <-- ESTO FALTABA

class Venta(VentaCreate):
    id: int

    @field_serializer('fecha')
    def serializar_fecha(self, fecha: datetime):
        return fecha.strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True

# --- DETALLE VENTA (para crear solo, por si lo usas aparte) ---
class DetalleVentaCreate(BaseModel):
    venta_id: int
    lote_id: int
    cantidad: int
    precio_unitario: float

class DetalleVenta(DetalleVentaCreate):
    id: int
    class Config:
        from_attributes = True

# --- LOTE ---
class LoteCreate(BaseModel):
    producto_id: int
    numero_lote: str
    proveedor_id: int
    fecha_vencimiento: date
    cantidad: int
    precio_compra: float

class Lote(LoteCreate):
    id: int
    class Config:
        from_attributes = True