from sqlalchemy.orm import Session
from modelos.categoria import Categoria
from repositorios.categoria import CategoriaRepositorio


class CategoriaServicio:

    @staticmethod
    def listar(db: Session):
        return CategoriaRepositorio.listar(db)

    @staticmethod
    def crear(db: Session, nombre: str, descripcion: str):
        if not nombre.strip():
            raise ValueError("El nombre de la categoría es obligatorio")

        categoria = Categoria(
            nombre=nombre,
            descripcion=descripcion
        )

        return CategoriaRepositorio.crear(db, categoria)

    @staticmethod
    def actualizar(db: Session, categoria_id: int, nombre: str, descripcion: str):
        categoria = CategoriaRepositorio.obtener_por_id(db, categoria_id)

        if not categoria:
            raise ValueError("Categoría no encontrada")

        if not nombre.strip():
            raise ValueError("El nombre de la categoría es obligatorio")

        categoria.nombre = nombre
        categoria.descripcion = descripcion

        return CategoriaRepositorio.actualizar(db, categoria)

    @staticmethod
    def eliminar(db: Session, categoria_id: int):
        categoria = CategoriaRepositorio.obtener_por_id(db, categoria_id)

        if not categoria:
            raise ValueError("Categoría no encontrada")

        return CategoriaRepositorio.eliminar(db, categoria)