from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from database import Base

class Lote(Base):
    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    numero_lote = Column(String)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    fecha_vencimiento = Column(Date)
    cantidad = Column(Integer)
    precio_compra = Column(Float)