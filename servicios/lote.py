from datetime import date, timedelta
from sqlalchemy.orm import Session
from modelos.lote import Lote
from modelos.detalleventa import DetalleVenta
from repositorios.lote import LoteRepositorio
from repositorios.producto import ProductoRepositorio
from repositorios.proveedor import ProveedorRepositorio
from servicios.producto import ProductoServicio

class LoteServicio:

    @staticmethod
    def listar(db: Session):
        return LoteRepositorio.listar(db)

    @staticmethod
    def listar_por_producto(db: Session, producto_id: int):
        return LoteRepositorio.listar_por_producto(db, producto_id)

    @staticmethod
    def obtener_por_vencer(db: Session, dias: int = 30):
        if dias < 0:
            raise ValueError("Los días no pueden ser negativos")
        hoy = date.today()
        limite = hoy + timedelta(days=dias)
        return db.query(Lote).filter(
            Lote.fecha_vencimiento >= hoy,
            Lote.fecha_vencimiento <= limite,
            Lote.cantidad > 0
        ).order_by(Lote.fecha_vencimiento.asc()).all()

    @staticmethod
    def _validar(db: Session, datos, lote_id=None, permitir_cero=False):
        if datos.cantidad < 0 or (datos.cantidad == 0 and not permitir_cero):
            raise ValueError("La cantidad debe ser mayor a cero")
        if datos.precio_compra < 0:
            raise ValueError("El precio de compra no puede ser negativo")
        if not datos.numero_lote.strip():
            raise ValueError("El número de lote es obligatorio")
        if not ProductoRepositorio.obtener_por_id(db, datos.producto_id):
            raise ValueError("El producto no existe")
        if not ProveedorRepositorio.obtener_por_id(db, datos.proveedor_id):
            raise ValueError("El proveedor no existe")
        repetido = LoteRepositorio.obtener_por_numero(db, datos.producto_id, datos.numero_lote.strip())
        if repetido and repetido.id != lote_id:
            raise ValueError("Ya existe un lote con ese número para este producto")

    @staticmethod
    def crear(db: Session, datos):
        LoteServicio._validar(db, datos)
        lote = Lote(**datos.model_dump())
        lote.numero_lote = lote.numero_lote.strip()
        lote = LoteRepositorio.crear(db, lote)
        ProductoServicio.sincronizar_stock(db, lote.producto_id)
        db.commit()
        return lote

    @staticmethod
    def actualizar(db: Session, lote_id: int, datos):
        lote = LoteRepositorio.obtener_por_id(db, lote_id)
        if not lote:
            raise ValueError("Lote no encontrado")

        # al editar sí se permite dejar el lote en 0 (se agotó)
        LoteServicio._validar(db, datos, lote_id=lote_id, permitir_cero=True)

        producto_anterior = lote.producto_id
        for key, value in datos.model_dump().items():
            setattr(lote, key, value)
        lote = LoteRepositorio.actualizar(db, lote)

        ProductoServicio.sincronizar_stock(db, lote.producto_id)
        if producto_anterior != lote.producto_id:
            ProductoServicio.sincronizar_stock(db, producto_anterior)
        db.commit()
        return lote

    @staticmethod
    def eliminar(db: Session, lote_id: int):
        lote = LoteRepositorio.obtener_por_id(db, lote_id)
        if not lote:
            raise ValueError("Lote no encontrado")

        if db.query(DetalleVenta).filter(DetalleVenta.lote_id == lote_id).first():
            raise ValueError("No se puede eliminar: el lote ya tiene ventas asociadas")

        producto_id = lote.producto_id
        LoteRepositorio.eliminar(db, lote)
        ProductoServicio.sincronizar_stock(db, producto_id)
        db.commit()
        return True
