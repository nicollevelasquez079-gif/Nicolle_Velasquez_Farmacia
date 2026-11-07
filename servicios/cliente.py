from sqlalchemy.orm import Session
from modelos.cliente import Cliente
from repositorios.cliente import ClienteRepositorio

class ClienteServicio:

    @staticmethod
    def listar(db: Session):
        return ClienteRepositorio.listar(db)

    @staticmethod
    def crear(db: Session, datos):
        if not datos.nombre.strip():
            raise ValueError("El nombre del cliente es obligatorio")

        if not datos.identidad.strip():
            raise ValueError("La identidad del cliente es obligatoria")

        if not datos.telefono.strip():
            raise ValueError("El teléfono del cliente es obligatorio")

        cliente = Cliente(**datos.model_dump())

        return ClienteRepositorio.crear(db, cliente)

    @staticmethod
    def actualizar(db: Session, cliente_id: int, datos):
        cliente = ClienteRepositorio.obtener_por_id(db, cliente_id)

        if not cliente:
            raise ValueError("Cliente no encontrado")

        if not datos.nombre.strip():
            raise ValueError("El nombre del cliente es obligatorio")

        if not datos.identidad.strip():
            raise ValueError("La identidad del cliente es obligatoria")

        if not datos.telefono.strip():
            raise ValueError("El teléfono del cliente es obligatorio")

        for key, value in datos.model_dump().items():
            setattr(cliente, key, value)

        return ClienteRepositorio.actualizar(db, cliente)

    @staticmethod
    def eliminar(db: Session, cliente_id: int):
        cliente = ClienteRepositorio.obtener_por_id(db, cliente_id)

        if not cliente:
            raise ValueError("Cliente no encontrado")

        return ClienteRepositorio.eliminar(db, cliente)