from sqlalchemy.orm import Session
from modelos.usuario import Usuario

class UsuarioRepositorio:

    @staticmethod
    def listar(db: Session):
        return db.query(Usuario).all()

    @staticmethod
    def obtener_por_id(db: Session, usuario_id: int):
        return db.query(Usuario).filter(
            Usuario.id == usuario_id
        ).first()

    @staticmethod
    def obtener_por_correo(db: Session, correo: str):
        return db.query(Usuario).filter(
            Usuario.correo == correo
        ).first()

    @staticmethod
    def crear(db: Session, usuario: Usuario):
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def actualizar(db: Session, usuario: Usuario):
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def eliminar(db: Session, usuario: Usuario):
        db.delete(usuario)
        db.commit()
        return True