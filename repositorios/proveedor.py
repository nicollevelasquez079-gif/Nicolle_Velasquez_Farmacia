from sqlalchemy.orm import Session
from modelos.proveedor import Proveedor

class ProveedorRepositorio:

    @staticmethod
    def listar(db: Session):
        return db.query(Proveedor).all()

    @staticmethod
    def obtener_por_id(db: Session, proveedor_id: int):
        return db.query(Proveedor).filter(
            Proveedor.id == proveedor_id
        ).first()

    @staticmethod
    def crear(db: Session, proveedor: Proveedor):
        db.add(proveedor)
        db.commit()
        db.refresh(proveedor)
        return proveedor

    @staticmethod
    def actualizar(db: Session, proveedor: Proveedor):
        db.commit()
        db.refresh(proveedor)
        return proveedor

    @staticmethod
    def eliminar(db: Session, proveedor: Proveedor):
        db.delete(proveedor)
        db.commit()
        return True