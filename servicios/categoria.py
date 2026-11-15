from datetime import date
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from modelos.categoria import Categoria
from modelos.producto import Producto
from modelos.lote import Lote
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

    @staticmethod
    def valor_inventario(db: Session):
        """Reporte (reto propio): valor del inventario vigente agrupado por categoría.
        - valor_venta: unidades vigentes x precio de venta del producto
        - valor_costo: unidades vigentes x precio de compra del lote
        - valor_vencido: lo que ya está vencido y no se puede vender"""
        hoy = date.today()
        vigente = Lote.fecha_vencimiento >= hoy
        vencido = Lote.fecha_vencimiento < hoy

        filas = (
            db.query(
                Categoria.id,
                Categoria.nombre,
                func.coalesce(func.sum(case((vigente, Lote.cantidad), else_=0)), 0),
                func.coalesce(func.sum(case((vigente, Lote.cantidad * Producto.precio), else_=0)), 0),
                func.coalesce(func.sum(case((vigente, Lote.cantidad * Lote.precio_compra), else_=0)), 0),
                func.coalesce(func.sum(case((vencido, Lote.cantidad * Producto.precio), else_=0)), 0),
            )
            .outerjoin(Producto, Producto.categoria_id == Categoria.id)
            .outerjoin(Lote, Lote.producto_id == Producto.id)
            .group_by(Categoria.id, Categoria.nombre)
            .order_by(Categoria.nombre)
            .all()
        )

        categorias = [
            {
                "categoria_id": cid,
                "categoria": nombre,
                "unidades_vigentes": int(unidades),
                "valor_venta": round(float(v_venta), 2),
                "valor_costo": round(float(v_costo), 2),
                "valor_vencido": round(float(v_vencido), 2),
            }
            for cid, nombre, unidades, v_venta, v_costo, v_vencido in filas
        ]
        return {
            "fecha": hoy.isoformat(),
            "categorias": categorias,
            "total_valor_venta": round(sum(c["valor_venta"] for c in categorias), 2),
            "total_valor_costo": round(sum(c["valor_costo"] for c in categorias), 2),
            "total_valor_vencido": round(sum(c["valor_vencido"] for c in categorias), 2),
        }
