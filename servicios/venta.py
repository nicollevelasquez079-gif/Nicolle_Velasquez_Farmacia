from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from auth import es_admin
from modelos.venta import Venta
from modelos.detalleventa import DetalleVenta
from modelos.lote import Lote
from modelos.producto import Producto
from repositorios.venta import VentaRepositorio
from repositorios.cliente import ClienteRepositorio
from repositorios.usuario import UsuarioRepositorio
from servicios.producto import ProductoServicio

class VentaServicio:

    @staticmethod
    def listar(db: Session):
        return VentaRepositorio.listar(db)

    @staticmethod
    def obtener_por_id(db: Session, venta_id: int):
        venta = VentaRepositorio.obtener_por_id(db, venta_id)
        if not venta:
            raise ValueError("Venta no encontrada")
        return venta

    @staticmethod
    def crear(db: Session, datos, usuario_actual):
        if not datos.detalles:
            raise ValueError("La venta debe incluir al menos un producto")

        if not ClienteRepositorio.obtener_por_id(db, datos.cliente_id):
            raise ValueError("El cliente no existe")

        # El vendedor es quien inició sesión; solo un admin puede registrar la venta a nombre de otro.
        usuario_id = usuario_actual.id
        if es_admin(usuario_actual) and datos.usuario_id:
            if not UsuarioRepositorio.obtener_por_id(db, datos.usuario_id):
                raise ValueError("El usuario no existe")
            usuario_id = datos.usuario_id

        hoy = date.today()

        # 1. Si el mismo producto viene en varias líneas, se suman ANTES de validar el stock
        pedido = defaultdict(int)
        for d in datos.detalles:
            pedido[d.producto_id] += d.cantidad

        # 2. Validar y armar el plan FEFO. Todavía no se modifica nada.
        plan = []  # (lote, cantidad_a_descontar, precio_unitario)
        total = Decimal("0")

        for producto_id, cantidad in pedido.items():
            producto = db.get(Producto, producto_id)
            if not producto:
                raise ValueError(f"El producto {producto_id} no existe")

            # Regla 1: nunca lotes vencidos. Regla 2: primero el que vence antes.
            lotes = db.query(Lote).filter(
                Lote.producto_id == producto_id,
                Lote.cantidad > 0,
                Lote.fecha_vencimiento >= hoy
            ).order_by(Lote.fecha_vencimiento.asc(), Lote.id.asc()).all()

            disponible = sum(l.cantidad for l in lotes)

            if disponible == 0:
                raise ValueError(
                    f"No hay stock vigente de '{producto.nombre}'. Todos los lotes están vencidos o agotados.")
            if cantidad > disponible:
                raise ValueError(
                    f"Stock insuficiente de '{producto.nombre}'. Disponible (sin vencidos): {disponible}, pedido: {cantidad}")

            # El precio sale de la base de datos, no de lo que mande el cliente
            precio = Decimal(str(producto.precio or 0))
            total += precio * cantidad

            pendiente = cantidad
            for lote in lotes:
                if pendiente == 0:
                    break
                tomar = min(lote.cantidad, pendiente)
                plan.append((lote, tomar, precio))
                pendiente -= tomar

        total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # 3. Aplicar todo en UNA transacción: o se guarda completo o no se guarda nada
        try:
            venta = Venta(
                fecha=datos.fecha or datetime.now(),
                total=total,
                usuario_id=usuario_id,
                cliente_id=datos.cliente_id
            )
            db.add(venta)
            db.flush()  # para obtener venta.id sin confirmar todavía

            for lote, cantidad, precio in plan:
                if lote.cantidad - cantidad < 0:   # Regla 3: stock nunca negativo
                    raise ValueError("Error de stock: la operación dejaría un lote en negativo")
                lote.cantidad -= cantidad
                db.add(DetalleVenta(
                    venta_id=venta.id,
                    lote_id=lote.id,
                    cantidad=cantidad,
                    precio_unitario=precio
                ))

            db.flush()
            for producto_id in pedido:
                ProductoServicio.sincronizar_stock(db, producto_id)

            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(venta)
        return venta

    @staticmethod
    def actualizar(db: Session, venta_id: int, datos, usuario_actual):
        """Solo se corrigen cliente, vendedor y fecha. El total y los productos no se tocan
        (para cambiar productos, se anula la venta y se registra otra)."""
        venta = VentaRepositorio.obtener_por_id(db, venta_id)
        if not venta:
            raise ValueError("Venta no encontrada")
        if not ClienteRepositorio.obtener_por_id(db, datos.cliente_id):
            raise ValueError("El cliente no existe")
        if datos.usuario_id:
            if not UsuarioRepositorio.obtener_por_id(db, datos.usuario_id):
                raise ValueError("El usuario no existe")
            venta.usuario_id = datos.usuario_id
        venta.cliente_id = datos.cliente_id
        if datos.fecha:
            venta.fecha = datos.fecha
        return VentaRepositorio.actualizar(db, venta)

    @staticmethod
    def eliminar(db: Session, venta_id: int):
        """Anular una venta devuelve el stock a los lotes de donde salió."""
        venta = VentaRepositorio.obtener_por_id(db, venta_id)
        if not venta:
            raise ValueError("Venta no encontrada")

        try:
            productos = set()
            detalles = db.query(DetalleVenta).filter(DetalleVenta.venta_id == venta_id).all()
            for d in detalles:
                lote = db.get(Lote, d.lote_id)
                if lote:
                    lote.cantidad += d.cantidad
                    productos.add(lote.producto_id)
                db.delete(d)
            db.delete(venta)
            db.flush()
            for producto_id in productos:
                ProductoServicio.sincronizar_stock(db, producto_id)
            db.commit()
        except Exception:
            db.rollback()
            raise
        return True
