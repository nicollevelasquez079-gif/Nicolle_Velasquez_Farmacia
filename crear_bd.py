from database import Base, engine, SessionLocal
from auth import crear_hash
from modelos.usuario import Usuario

Base.metadata.create_all(bind=engine)

db = SessionLocal()
db.query(Usuario).delete()
hashed = crear_hash("admin123")
admin = Usuario(username="admin", password_hash=hashed, rol="admin")
db.add(admin)
db.commit()
print("Listo! Usuario: admin Clave: admin123")
db.close()