from sqlalchemy.orm import Session
from modelos.categoria import Categoria


class CategoriaRepositorio:

    @staticmethod
    def listar(db: Session):
        return db.query(Categoria).all()

    @staticmethod
    def obtener_por_id(db: Session, categoria_id: int):
        return db.query(Categoria).filter(
            Categoria.id == categoria_id
        ).first()

    @staticmethod
    def crear(db: Session, categoria: Categoria):
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria

    @staticmethod
    def actualizar(db: Session, categoria: Categoria):
        db.commit()
        db.refresh(categoria)
        return categoria

    @staticmethod
    def eliminar(db: Session, categoria: Categoria):
        db.delete(categoria)
        db.commit()
        return True