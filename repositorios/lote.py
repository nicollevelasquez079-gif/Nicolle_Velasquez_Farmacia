from sqlalchemy.orm import Session
from modelos.lote import Lote

class LoteRepositorio:

    @staticmethod
    def listar(db: Session):
        return db.query(Lote).all()

    @staticmethod
    def obtener_por_id(db: Session, lote_id: int):
        return db.query(Lote).filter(
            Lote.id == lote_id
        ).first()

    @staticmethod
    def listar_por_producto(db: Session, producto_id: int):
        # FEFO: ordena por fecha de vencimiento, el que vence primero sale primero
        return db.query(Lote).filter(
            Lote.producto_id == producto_id,
            Lote.cantidad_actual > 0
        ).order_by(Lote.fecha_vencimiento.asc()).all()

    @staticmethod
    def crear(db: Session, lote: Lote):
        db.add(lote)
        db.commit()
        db.refresh(lote)
        return lote

    @staticmethod
    def actualizar(db: Session, lote: Lote):
        db.commit()
        db.refresh(lote)
        return lote

    @staticmethod
    def eliminar(db: Session, lote: Lote):
        db.delete(lote)
        db.commit()
        return True