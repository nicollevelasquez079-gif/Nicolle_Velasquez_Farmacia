from sqlalchemy.orm import Session
from modelos.usuario import Usuario
from repositorios.usuario import UsuarioRepositorio
from auth import crear_hash

class UsuarioServicio:

    @staticmethod
    def listar(db: Session):
        return UsuarioRepositorio.listar(db)

    @staticmethod
    def _validar(datos):
        if not datos.username.strip():
            raise ValueError("El username es obligatorio")
        if not datos.password.strip():
            raise ValueError("La contraseña es obligatoria")
        if not datos.rol.strip():
            raise ValueError("El rol es obligatorio")

    @staticmethod
    def crear(db: Session, datos):
        UsuarioServicio._validar(datos)

        if UsuarioRepositorio.obtener_por_username(db, datos.username.strip()):
            raise ValueError("Ese nombre de usuario ya existe")

        usuario = Usuario(
            username=datos.username.strip(),
            password_hash=crear_hash(datos.password),   # nunca se guarda la clave en texto plano
            rol=datos.rol.strip()
        )
        return UsuarioRepositorio.crear(db, usuario)

    @staticmethod
    def actualizar(db: Session, usuario_id: int, datos):
        usuario = UsuarioRepositorio.obtener_por_id(db, usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        UsuarioServicio._validar(datos)

        otro = UsuarioRepositorio.obtener_por_username(db, datos.username.strip())
        if otro and otro.id != usuario_id:
            raise ValueError("Ese nombre de usuario ya existe")

        usuario.username = datos.username.strip()
        usuario.password_hash = crear_hash(datos.password)
        usuario.rol = datos.rol.strip()
        return UsuarioRepositorio.actualizar(db, usuario)

    @staticmethod
    def eliminar(db: Session, usuario_id: int):
        usuario = UsuarioRepositorio.obtener_por_id(db, usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")
        return UsuarioRepositorio.eliminar(db, usuario)
