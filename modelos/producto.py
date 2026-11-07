from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from database import Base

class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    precio = Column(Float)
    stock = Column(Integer)
    requiere_receta = Column(Boolean, default=False)