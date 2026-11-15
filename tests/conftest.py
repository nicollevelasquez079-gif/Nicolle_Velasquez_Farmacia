import os
import tempfile

# Base de datos temporal para los tests: no toca farmacia.db.
# Tiene que ir ANTES de importar database/main.
_carpeta = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_carpeta}/test.db"

from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient

from database import Base, engine, SessionLocal
from main import app
from crear_bd import crear_admin
from modelos.categoria import Categoria
from modelos.producto import Producto
from modelos.proveedor import Proveedor
from modelos.cliente import Cliente
from modelos.lote import Lote


@pytest.fixture()
def datos():
    """Base limpia en cada test, con: admin, 1 categoría, 1 producto (precio 10),
    1 proveedor y 1 cliente. Devuelve los ids."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    crear_admin(db, "admin", "admin123", "admin")

    cat = Categoria(nombre="Analgésicos")
    db.add(cat); db.flush()
    prod = Producto(nombre="Paracetamol", categoria_id=cat.id, precio=10.0, stock=0)
    prov = Proveedor(razon_social="Distribuidora X", ruc="123", contacto="Juan")
    cli = Cliente(nombre="Ana", identidad="0801", telefono="9999")
    db.add_all([prod, prov, cli]); db.commit()
    ids = {"categoria": cat.id, "producto": prod.id, "proveedor": prov.id, "cliente": cli.id}
    db.close()
    return ids


@pytest.fixture()
def client(datos):
    return TestClient(app)


def token(client, usuario="admin", clave="admin123"):
    r = client.post("/api/v1/auth/login", json={"usuario": usuario, "clave": clave})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture()
def auth(client):
    return {"Authorization": f"Bearer {token(client)}"}


@pytest.fixture()
def nuevo_lote(datos):
    """Crea un lote directo en la base. dias = días hasta que vence (negativo = ya vencido)."""
    def _crear(numero, dias, cantidad):
        db = SessionLocal()
        lote = Lote(producto_id=datos["producto"], proveedor_id=datos["proveedor"],
                    numero_lote=numero, fecha_vencimiento=date.today() + timedelta(days=dias),
                    cantidad=cantidad, precio_compra=6.0)
        db.add(lote); db.commit()
        lid = lote.id
        db.close()
        return lid
    return _crear


def cantidad_lote(lote_id):
    db = SessionLocal()
    cant = db.get(Lote, lote_id).cantidad
    db.close()
    return cant