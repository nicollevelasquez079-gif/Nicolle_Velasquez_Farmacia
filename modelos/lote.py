from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from database import Base

class Lote(Base):
    __tablename__ = "lotes"
    __table_args__ = (UniqueConstraint("producto_id", "numero_lote", name="uq_lote_producto_numero"),)

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    numero_lote = Column(String, nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)
    precio_compra = Column(Float)
