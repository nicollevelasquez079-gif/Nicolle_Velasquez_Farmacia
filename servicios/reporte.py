"""Reportes y exportación CSV.

El resumen usa a propósito las colecciones de Python (Counter, defaultdict, deque, set)
para cumplir el requisito "reporte con colecciones" del Avance 3.
"""
import csv
import io
from collections import Counter, defaultdict, deque
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from modelos.categoria import Categoria
from modelos.producto import Producto
from modelos.proveedor import Proveedor
from modelos.cliente import Cliente
from modelos.lote import Lote
from modelos.venta import Venta
from modelos.detalleventa import DetalleVenta

# Entidades que se pueden exportar. "usuarios" NO está a propósito (tiene hashes de contraseña).
EXPORTABLES = {
    "productos": Producto,
    "categorias": Categoria,
    "proveedores": Proveedor,
    "clientes": Cliente,
    "lotes": Lote,
    "ventas": Venta,
    "detalleventas": DetalleVenta,
}


class ReporteServicio:

    @staticmethod
    def resumen(db: Session, dias_por_vencer: int = 30):
        hoy = date.today()
        limite = hoy + timedelta(days=dias_por_vencer)

        productos = {p.id: p for p in db.query(Producto).all()}
        lotes = {l.id: l for l in db.query(Lote).all()}
        clientes = {c.id: c for c in db.query(Cliente).all()}
        ventas = db.query(Venta).order_by(Venta.fecha).all()
        detalles = db.query(DetalleVenta).all()

        # Counter: unidades vendidas por producto (detalle -> lote -> producto)
        unidades = Counter()
        for d in detalles:
            lote = lotes.get(d.lote_id)
            if lote:
                unidades[lote.producto_id] += d.cantidad
        mas_vendidos = [
            {"producto": productos[pid].nombre, "unidades": n}
            for pid, n in unidades.most_common(5) if pid in productos
        ]

        # defaultdict: total vendido por día y por cliente
        por_dia = defaultdict(float)
        por_cliente = defaultdict(lambda: {"compras": 0, "total": 0.0})
        for v in ventas:
            por_dia[v.fecha.date().isoformat()] += float(v.total)
            c = por_cliente[v.cliente_id]
            c["compras"] += 1
            c["total"] += float(v.total)
        mejores_clientes = sorted(
            ({"cliente": clientes[cid].nombre if cid in clientes else f"Cliente {cid}",
              "compras": c["compras"], "total": round(c["total"], 2)}
             for cid, c in por_cliente.items()),
            key=lambda x: x["total"], reverse=True)[:5]

        # Counter: lotes según su estado
        estados = Counter()
        for l in lotes.values():
            if l.cantidad <= 0:
                estados["agotado"] += 1
            elif l.fecha_vencimiento < hoy:
                estados["vencido"] += 1
            elif l.fecha_vencimiento <= limite:
                estados["por_vencer"] += 1
            else:
                estados["vigente"] += 1

        # set: productos que nunca se han vendido
        sin_ventas = sorted(productos[p].nombre for p in set(productos) - set(unidades))

        # deque con maxlen: las últimas 5 ventas
        ultimas = deque(ventas, maxlen=5)

        return {
            "fecha": hoy.isoformat(),
            "mas_vendidos": mas_vendidos,
            "ventas_por_dia": {dia: round(t, 2) for dia, t in sorted(por_dia.items())},
            "mejores_clientes": mejores_clientes,
            "lotes_por_estado": {k: estados.get(k, 0) for k in ("vigente", "por_vencer", "vencido", "agotado")},
            "productos_sin_ventas": sin_ventas,
            "ultimas_ventas": [
                {"id": v.id, "fecha": v.fecha.strftime("%Y-%m-%dT%H:%M:%S"), "total": float(v.total)}
                for v in reversed(ultimas)
            ],
        }

    @staticmethod
    def exportar_csv(db: Session, entidad: str) -> str:
        modelo = EXPORTABLES.get(entidad)
        if modelo is None:
            raise ValueError("Entidad no exportable")

        columnas = [c.name for c in modelo.__table__.columns]
        salida = io.StringIO()
        escritor = csv.writer(salida, delimiter=";")   # Excel en español separa columnas con ;
        escritor.writerow(columnas)
        for fila in db.query(modelo).order_by(modelo.id).all():
            valores = []
            for c in columnas:
                v = getattr(fila, c)
                if v is None:
                    v = ""
                elif isinstance(v, (float, Decimal)):
                    v = str(v).replace(".", ",")   # Excel en español usa coma decimal
                valores.append(v)
            escritor.writerow(valores)
        return salida.getvalue()
