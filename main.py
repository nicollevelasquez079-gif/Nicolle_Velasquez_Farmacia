from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import categorias, producto, cliente, proveedor, usuario, venta, detalleventa, lote, auth

import modelos.categoria
import modelos.producto
import modelos.proveedor
import modelos.cliente
import modelos.lote
import modelos.venta
import modelos.detalleventa
import modelos.usuario

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestion Farmacéutica")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(categorias.router, prefix="/api/v1/categorias", tags=["Categorías"])
app.include_router(producto.router, prefix="/api/v1/productos", tags=["Productos"])
app.include_router(cliente.router, prefix="/api/v1/clientes", tags=["Clientes"])
app.include_router(proveedor.router, prefix="/api/v1/proveedores", tags=["Proveedores"])
app.include_router(usuario.router, prefix="/api/v1/usuarios", tags=["Usuarios"])
app.include_router(venta.router, prefix="/api/v1/ventas", tags=["Ventas"])
app.include_router(detalleventa.router, prefix="/api/v1/detalleventas", tags=["DetalleVentas"])
app.include_router(lote.router, prefix="/api/v1/lotes", tags=["Lotes y Vencimientos"])

@app.get("/", tags=["General"])
def inicio():
    return {"mensaje": "API Farmacia funcionando"}