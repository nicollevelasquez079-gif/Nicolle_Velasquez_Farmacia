from sqlalchemy.orm import Session
from modelos.detalleventa import DetalleVenta

class DetalleVentaRepositorio:

    @staticmethod
    def listar(db: Session):
        return db.query(DetalleVenta).all()

    @staticmethod
    def obtener_por_id(db: Session, detalle_id: int):
        return db.query(DetalleVenta).filter(
            DetalleVenta.id == detalle_id
        ).first()

    @staticmethod
    def listar_por_venta(db: Session, venta_id: int):
        return db.query(DetalleVenta).filter(
            DetalleVenta.venta_id == venta_id
        ).all()

    @staticmethod
    def crear(db: Session, detalle: DetalleVenta):
        db.add(detalle)
        db.commit()
        db.refresh(detalle)
        return detalle

    @staticmethod
    def actualizar(db: Session, detalle: DetalleVenta):
        db.commit()
        db.refresh(detalle)
        return detalle

    @staticmethod
    def eliminar(db: Session, detalle: DetalleVenta):
        db.delete(detalle)
        db.commit()
        return True