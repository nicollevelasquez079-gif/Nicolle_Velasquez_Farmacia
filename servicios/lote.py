from datetime import date, timedelta
from sqlalchemy.orm import Session
from modelos.lote import Lote
from repositorios.lote import LoteRepositorio
from repositorios.producto import ProductoRepositorio
from repositorios.proveedor import ProveedorRepositorio

class LoteServicio:

    @staticmethod
    def listar(db: Session):
        return LoteRepositorio.listar(db)

    @staticmethod
    def listar_por_producto(db: Session, producto_id: int):
        return LoteRepositorio.listar_por_producto(db, producto_id)
        
    @staticmethod
    def obtener_por_vencer(db: Session, dias: int = 30):
        hoy = date.today()
        limite = hoy + timedelta(days=dias)
        return db.query(Lote).filter(
            Lote.fecha_vencimiento >= hoy,
            Lote.fecha_vencimiento <= limite,
            Lote.cantidad > 0
        ).order_by(Lote.fecha_vencimiento.asc()).all()

    @staticmethod
    def crear(db: Session, datos):
        if datos.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")

        if datos.precio_compra < 0:
            raise ValueError("El precio de compra no puede ser negativo")

        producto = ProductoRepositorio.obtener_por_id(db, datos.producto_id)
        if not producto:
            raise ValueError("El producto no existe")

        proveedor = ProveedorRepositorio.obtener_por_id(db, datos.proveedor_id)
        if not proveedor:
            raise ValueError("El proveedor no existe")

        lote = Lote(**datos.model_dump())

        return LoteRepositorio.crear(db, lote)

    @staticmethod
    def actualizar(db: Session, lote_id: int, datos):
        lote = LoteRepositorio.obtener_por_id(db, lote_id)

        if not lote:
            raise ValueError("Lote no encontrado")

        if datos.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")

        if datos.precio_compra < 0:
            raise ValueError("El precio de compra no puede ser negativo")

        producto = ProductoRepositorio.obtener_por_id(db, datos.producto_id)
        if not producto:
            raise ValueError("El producto no existe")

        proveedor = ProveedorRepositorio.obtener_por_id(db, datos.proveedor_id)
        if not proveedor:
            raise ValueError("El proveedor no existe")

        for key, value in datos.model_dump().items():
            setattr(lote, key, value)

        return LoteRepositorio.actualizar(db, lote)

    @staticmethod
    def eliminar(db: Session, lote_id: int):
        lote = LoteRepositorio.obtener_por_id(db, lote_id)

        if not lote:
            raise ValueError("Lote no encontrado")

        return LoteRepositorio.eliminar(db, lote)
