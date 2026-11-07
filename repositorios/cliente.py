from sqlalchemy.orm import Session
from modelos.cliente import Cliente

class ClienteRepositorio:

    @staticmethod
    def listar(db: Session):
        return db.query(Cliente).all()

    @staticmethod
    def obtener_por_id(db: Session, cliente_id: int):
        return db.query(Cliente).filter(
            Cliente.id == cliente_id
        ).first()

    @staticmethod
    def crear(db: Session, cliente: Cliente):
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return cliente

    @staticmethod
    def actualizar(db: Session, cliente: Cliente):
        db.commit()
        db.refresh(cliente)
        return cliente

    @staticmethod
    def eliminar(db: Session, cliente: Cliente):
        db.delete(cliente)
        db.commit()
        return True