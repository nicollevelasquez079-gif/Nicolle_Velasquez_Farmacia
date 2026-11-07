from sqlalchemy.orm import Session
from modelos.producto import Producto


class ProductoRepositorio:

    @staticmethod
    def listar(db: Session):
        return db.query(Producto).all()

    @staticmethod
    def obtener_por_id(db: Session, producto_id: int):
        return db.query(Producto).filter(
            Producto.id == producto_id
        ).first()

    @staticmethod
    def crear(db: Session, producto: Producto):
        db.add(producto)
        db.commit()
        db.refresh(producto)
        return producto

    @staticmethod
    def actualizar(db: Session, producto: Producto):
        db.commit()
        db.refresh(producto)
        return producto

    @staticmethod
    def eliminar(db: Session, producto: Producto):
        db.delete(producto)
        db.commit()
        return True