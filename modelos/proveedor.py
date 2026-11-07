from sqlalchemy import Column, Integer, String
from database import Base

class Proveedor(Base):
    __tablename__ = "proveedores"
    id = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String(150), nullable=False)
    ruc = Column(String(30))
    contacto = Column(String(100))
    telefono = Column(String(20))