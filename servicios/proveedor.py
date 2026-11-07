from sqlalchemy.orm import Session
from modelos.proveedor import Proveedor
from repositorios.proveedor import ProveedorRepositorio

class ProveedorServicio:

    @staticmethod
    def listar(db: Session):
        return ProveedorRepositorio.listar(db)

    @staticmethod
    def crear(db: Session, datos):
        if not datos.razon_social.strip():
            raise ValueError("La razón social es obligatoria")

        if not datos.ruc.strip():
            raise ValueError("El RUC es obligatorio")

        if not datos.contacto.strip():
            raise ValueError("El contacto es obligatorio")

        if not datos.telefono.strip():
            raise ValueError("El teléfono es obligatorio")

        proveedor = Proveedor(**datos.model_dump())

        return ProveedorRepositorio.crear(db, proveedor)

    @staticmethod
    def actualizar(db: Session, proveedor_id: int, datos):
        proveedor = ProveedorRepositorio.obtener_por_id(db, proveedor_id)

        if not proveedor:
            raise ValueError("Proveedor no encontrado")

        if not datos.razon_social.strip():
            raise ValueError("La razón social es obligatoria")

        if not datos.ruc.strip():
            raise ValueError("El RUC es obligatorio")

        if not datos.contacto.strip():
            raise ValueError("El contacto es obligatorio")

        if not datos.telefono.strip():
            raise ValueError("El teléfono es obligatorio")

        for key, value in datos.model_dump().items():
            setattr(proveedor, key, value)

        return ProveedorRepositorio.actualizar(db, proveedor)

    @staticmethod
    def eliminar(db: Session, proveedor_id: int):
        proveedor = ProveedorRepositorio.obtener_por_id(db, proveedor_id)

        if not proveedor:
            raise ValueError("Proveedor no encontrado")

        return ProveedorRepositorio.eliminar(db, proveedor)