import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import Base, engine
from auth import get_current_user, solo_admin
from routers import categorias, producto, cliente, proveedor, usuario, venta, detalleventa, lote, auth, reportes
from routers import respaldo as respaldo_router
from servicios import respaldo

import modelos  # registra todos los modelos

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Hilo de respaldo automático (se puede apagar con RESPALDO_AUTO=0)
    if os.getenv("RESPALDO_AUTO", "1") == "1":
        respaldo.iniciar()
    yield
    respaldo.detener()


app = FastAPI(title="Sistema de Gestion Farmacéutica", lifespan=lifespan)

# El frontend se sirve desde este mismo servidor, así que no hace falta abrir CORS a todo el mundo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Login: público
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])

# Todo lo demás exige token válido
protegido = [Depends(get_current_user)]
app.include_router(categorias.router, prefix="/api/v1/categorias", tags=["Categorías"], dependencies=protegido)
app.include_router(producto.router, prefix="/api/v1/productos", tags=["Productos"], dependencies=protegido)
app.include_router(cliente.router, prefix="/api/v1/clientes", tags=["Clientes"], dependencies=protegido)
app.include_router(proveedor.router, prefix="/api/v1/proveedores", tags=["Proveedores"], dependencies=protegido)
app.include_router(venta.router, prefix="/api/v1/ventas", tags=["Ventas"], dependencies=protegido)
app.include_router(detalleventa.router, prefix="/api/v1/detalleventas", tags=["DetalleVentas"], dependencies=protegido)
app.include_router(lote.router, prefix="/api/v1/lotes", tags=["Lotes y Vencimientos"], dependencies=protegido)

app.include_router(reportes.router, prefix="/api/v1/reportes", tags=["Reportes y CSV"], dependencies=protegido)

# Respaldos: solo administrador
app.include_router(respaldo_router.router, prefix="/api/v1/respaldos", tags=["Respaldos"], dependencies=[Depends(solo_admin)])

# Usuarios: solo administrador
app.include_router(usuario.router, prefix="/api/v1/usuarios", tags=["Usuarios"], dependencies=[Depends(solo_admin)])

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/", tags=["General"])
def inicio():
    return FileResponse("frontend/index.html")
