from sqlalchemy.orm import Session
from modelos.venta import Venta

class VentaRepositorio:

    @staticmethod
    def listar(db: Session):
        return db.query(Venta).all()

    @staticmethod
    def obtener_por_id(db: Session, venta_id: int):
        return db.query(Venta).filter(
            Venta.id == venta_id
        ).first()

    @staticmethod
    def crear(db: Session, venta: Venta):
        db.add(venta)
        db.commit()
        db.refresh(venta)
        return venta

    @staticmethod
    def actualizar(db: Session, venta: Venta):
        db.commit()
        db.refresh(venta)
        return venta

    @staticmethod
    def eliminar(db: Session, venta: Venta):
        db.delete(venta)
        db.commit()
        return True