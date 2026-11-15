"""Crea las tablas y el usuario admin.

Uso:  python crear_bd.py
La clave del admin se toma de la variable ADMIN_PASSWORD (por defecto admin123, solo para desarrollo).
"""
import os
import modelos  # registra todos los modelos
from database import Base, engine, SessionLocal
from auth import crear_hash
from modelos.usuario import Usuario


def crear_admin(db, username="admin", clave="admin123", rol="admin"):
    existente = db.query(Usuario).filter(Usuario.username == username).first()
    if existente:
        return existente
    admin = Usuario(username=username, password_hash=crear_hash(clave), rol=rol)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    clave = os.getenv("ADMIN_PASSWORD", "admin123")
    crear_admin(db, "admin", clave)
    print(f"Listo. Usuario: admin  Clave: {clave}")
    db.close()


if __name__ == "__main__":
    main()
