from datetime import date
from sqlalchemy.orm import Session
from modelos.venta import Venta
from modelos.detalleventa import DetalleVenta
from modelos.lote import Lote
from repositorios.venta import VentaRepositorio
from repositorios.cliente import ClienteRepositorio
from repositorios.usuario import UsuarioRepositorio

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
    def crear(db: Session, datos):
        if datos.total < 0:
            raise ValueError("El total no puede ser negativo")

        cliente = ClienteRepositorio.obtener_por_id(db, datos.cliente_id)
        if not cliente:
            raise ValueError("El cliente no existe")

        usuario = UsuarioRepositorio.obtener_por_id(db, datos.usuario_id)
        if not usuario:
            raise ValueError("El usuario no existe")

        hoy = date.today()
        datos_dict = datos.model_dump()
        detalles_data = datos_dict.pop("detalles", []) or []

        if not detalles_data:
            venta = Venta(**datos_dict)
            return VentaRepositorio.crear(db, venta)

        # 1. VALIDAR Y ARMAR PLAN FIFO POR LOTE
        # plan = lista de (lote_objeto, cantidad_a_descontar, precio_unitario)
        plan = []

        for d in detalles_data:
            producto_id = d.get("producto_id")
            cantidad_pedida = d.get("cantidad")
            precio = d.get("precio_unitario", 0)

            if cantidad_pedida is None or cantidad_pedida <= 0:
                raise ValueError(f"Cantidad debe ser mayor a 0 para producto {producto_id}")

            # SOLO lotes NO vencidos, ordenados por el que vence PRIMERO
            lotes = db.query(Lote).filter(
                Lote.producto_id == producto_id,
                Lote.cantidad > 0,
                Lote.fecha_vencimiento >= hoy
            ).order_by(Lote.fecha_vencimiento.asc()).all()

            stock_disponible = sum(l.cantidad for l in lotes)

            if stock_disponible == 0:
                raise ValueError(f"No hay stock vigente para producto {producto_id}. Todos los lotes están vencidos o agotados.")

            if cantidad_pedida > stock_disponible:
                raise ValueError(f"Stock insuficiente para producto {producto_id}. Disponible (sin vencidos): {stock_disponible}, Pedido: {cantidad_pedida}")

            pendiente = cantidad_pedida
            for lote in lotes:
                if pendiente == 0:
                    break
                a_descontar = min(lote.cantidad, pendiente)
                plan.append((lote, a_descontar, precio))
                pendiente -= a_descontar

        # 2. SI PASÓ TODO, DESCONTAR Y GUARDAR
        for lote, cantidad, _ in plan:
            lote.cantidad -= cantidad
            if lote.cantidad < 0:
                lote.cantidad = 0

        venta = Venta(**datos_dict)
        venta_guardada = VentaRepositorio.crear(db, venta)

        # 3. Crear UN DetalleVenta por CADA LOTE usado (por eso lleva lote_id)
        for lote, cantidad, precio in plan:
            detalle = DetalleVenta(
                venta_id=venta_guardada.id,
                lote_id=lote.id,
                cantidad=cantidad,
                precio_unitario=precio
            )
            db.add(detalle)

        db.commit()
        db.refresh(venta_guardada)
        return venta_guardada

    @staticmethod
    def actualizar(db: Session, venta_id: int, datos):
        venta = VentaRepositorio.obtener_por_id(db, venta_id)
        if not venta:
            raise ValueError("Venta no encontrada")
        if datos.total < 0:
            raise ValueError("El total no puede ser negativo")
        cliente = ClienteRepositorio.obtener_por_id(db, datos.cliente_id)
        if not cliente:
            raise ValueError("El cliente no existe")
        usuario = UsuarioRepositorio.obtener_por_id(db, datos.usuario_id)
        if not usuario:
            raise ValueError("El usuario no existe")
        for key, value in datos.model_dump(exclude={"detalles"}).items():
            setattr(venta, key, value)
        return VentaRepositorio.actualizar(db, venta)

    @staticmethod
    def eliminar(db: Session, venta_id: int):
        venta = VentaRepositorio.obtener_por_id(db, venta_id)
        if not venta:
            raise ValueError("Venta no encontrada")
        return VentaRepositorio.eliminar(db, venta)