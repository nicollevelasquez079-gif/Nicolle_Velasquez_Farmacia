from sqlalchemy.orm import Session
from modelos.detalleventa import DetalleVenta
from repositorios.detalleventa import DetalleVentaRepositorio
from repositorios.venta import VentaRepositorio
from repositorios.lote import LoteRepositorio

class DetalleVentaServicio:

    @staticmethod
    def listar(db: Session):
        return DetalleVentaRepositorio.listar(db)

    @staticmethod
    def listar_por_venta(db: Session, venta_id: int):
        return DetalleVentaRepositorio.listar_por_venta(db, venta_id)

    @staticmethod
    def crear(db: Session, datos):
        if datos.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")

        if datos.precio_unitario < 0:
            raise ValueError("El precio no puede ser negativo")

        venta = VentaRepositorio.obtener_por_id(db, datos.venta_id)
        if not venta:
            raise ValueError("La venta no existe")

        lote = LoteRepositorio.obtener_por_id(db, datos.lote_id)
        if not lote:
            raise ValueError("El lote no existe")

        detalle = DetalleVenta(**datos.model_dump())

        return DetalleVentaRepositorio.crear(db, detalle)

    @staticmethod
    def actualizar(db: Session, detalle_id: int, datos):
        detalle = DetalleVentaRepositorio.obtener_por_id(db, detalle_id)

        if not detalle:
            raise ValueError("DetalleVenta no encontrado")

        if datos.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")

        if datos.precio_unitario < 0:
            raise ValueError("El precio no puede ser negativo")

        venta = VentaRepositorio.obtener_por_id(db, datos.venta_id)
        if not venta:
            raise ValueError("La venta no existe")

        lote = LoteRepositorio.obtener_por_id(db, datos.lote_id)
        if not lote:
            raise ValueError("El lote no existe")

        for key, value in datos.model_dump().items():
            setattr(detalle, key, value)

        return DetalleVentaRepositorio.actualizar(db, detalle)

    @staticmethod
    def eliminar(db: Session, detalle_id: int):
        detalle = DetalleVentaRepositorio.obtener_por_id(db, detalle_id)

        if not detalle:
            raise ValueError("DetalleVenta no encontrado")

        return DetalleVentaRepositorio.eliminar(db, detalle)