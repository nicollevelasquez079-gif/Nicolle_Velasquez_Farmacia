from sqlalchemy.orm import Session
from modelos.producto import Producto
from repositorios.producto import ProductoRepositorio
from repositorios.categoria import CategoriaRepositorio


class ProductoServicio:

    @staticmethod
    def listar(db: Session):
        return ProductoRepositorio.listar(db)

    @staticmethod
    def crear(db: Session, datos):
        if not datos.nombre.strip():
            raise ValueError("El nombre del producto es obligatorio")

        if datos.precio < 0:
            raise ValueError("El precio no puede ser negativo")

        if datos.stock < 0:
            raise ValueError("El stock no puede ser negativo")

        categoria = CategoriaRepositorio.obtener_por_id(
            db, datos.categoria_id
        )

        if not categoria:
            raise ValueError("La categoría no existe")

        producto = Producto(**datos.model_dump())

        return ProductoRepositorio.crear(db, producto)

    @staticmethod
    def actualizar(db: Session, producto_id: int, datos):
        producto = ProductoRepositorio.obtener_por_id(db, producto_id)

        if not producto:
            raise ValueError("Producto no encontrado")

        if not datos.nombre.strip():
            raise ValueError("El nombre del producto es obligatorio")

        if datos.precio < 0 or datos.stock < 0:
            raise ValueError("El precio y el stock no pueden ser negativos")

        categoria = CategoriaRepositorio.obtener_por_id(
            db, datos.categoria_id
        )

        if not categoria:
            raise ValueError("La categoría no existe")

        for key, value in datos.model_dump().items():
            setattr(producto, key, value)

        return ProductoRepositorio.actualizar(db, producto)

    @staticmethod
    def eliminar(db: Session, producto_id: int):
        producto = ProductoRepositorio.obtener_por_id(db, producto_id)

        if not producto:
            raise ValueError("Producto no encontrado")

        return ProductoRepositorio.eliminar(db, producto)