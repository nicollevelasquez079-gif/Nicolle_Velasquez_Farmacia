from sqlalchemy.orm import Session
from modelos.usuario import Usuario
from repositorios.usuario import UsuarioRepositorio

class UsuarioServicio:

    @staticmethod
    def listar(db: Session):
        return UsuarioRepositorio.listar(db)

    @staticmethod
    def crear(db: Session, datos):
        if not datos.username.strip():
            raise ValueError("El username es obligatorio")

        if not datos.password.strip():
            raise ValueError("La contraseña es obligatoria")

        if not datos.rol.strip():
            raise ValueError("El rol es obligatorio")

        usuario = Usuario(
            username=datos.username,
            password_hash=datos.password,  
            rol=datos.rol
        )

        return UsuarioRepositorio.crear(db, usuario)

    @staticmethod
    def actualizar(db: Session, usuario_id: int, datos):
        usuario = UsuarioRepositorio.obtener_por_id(db, usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        if not datos.username.strip():
            raise ValueError("El username es obligatorio")
        if not datos.password.strip():
            raise ValueError("La contraseña es obligatoria")
        if not datos.rol.strip():
            raise ValueError("El rol es obligatorio")

        usuario.username = datos.username
        usuario.password_hash = datos.password
        usuario.rol = datos.rol

        return UsuarioRepositorio.actualizar(db, usuario)

    @staticmethod
    def eliminar(db: Session, usuario_id: int):
        usuario = UsuarioRepositorio.obtener_por_id(db, usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")
        return UsuarioRepositorio.eliminar(db, usuario)