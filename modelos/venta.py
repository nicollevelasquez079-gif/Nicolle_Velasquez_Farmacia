from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey
from database import Base
import datetime

class Venta(Base):
    __tablename__ = "ventas"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False, default=datetime.datetime.now)
    total = Column(Numeric(10,2), nullable=False, default=0)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)