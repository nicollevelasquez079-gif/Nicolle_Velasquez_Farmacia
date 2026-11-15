"""Respaldo automático de la base de datos SQLite en un hilo (thread) aparte.

- Un hilo daemon hace una copia al arrancar y luego cada RESPALDO_CADA_MIN minutos.
- Se usa la API de backup de sqlite3, que copia de forma segura aunque la base esté en uso.
- Un Lock evita dos respaldos al mismo tiempo; se conservan solo los últimos RESPALDO_MAXIMO.
"""
import os
import sqlite3
import threading
from datetime import datetime
from database import engine

CARPETA = os.getenv("RESPALDO_DIR", "respaldos")
INTERVALO_MIN = float(os.getenv("RESPALDO_CADA_MIN", "30"))
MAXIMO = int(os.getenv("RESPALDO_MAXIMO", "10"))

_lock = threading.Lock()
_detener = threading.Event()
_hilo = None
estado = {"ultimo": None, "error": None}


def hacer_respaldo() -> str:
    origen = engine.url.database
    if not origen or not os.path.exists(origen):
        raise RuntimeError("No se encontró el archivo de la base de datos")

    with _lock:
        os.makedirs(CARPETA, exist_ok=True)
        nombre = f"farmacia_{datetime.now():%Y%m%d_%H%M%S}.db"
        destino = os.path.join(CARPETA, nombre)
        src = sqlite3.connect(origen)
        dst = sqlite3.connect(destino)
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()
        _rotar()
        estado["ultimo"] = datetime.now().isoformat(timespec="seconds")
        estado["error"] = None
    return nombre


def _rotar():
    archivos = sorted(f for f in os.listdir(CARPETA) if f.startswith("farmacia_") and f.endswith(".db"))
    for viejo in archivos[:-MAXIMO]:
        os.remove(os.path.join(CARPETA, viejo))


def listar():
    if not os.path.isdir(CARPETA):
        return []
    return sorted((f for f in os.listdir(CARPETA) if f.endswith(".db")), reverse=True)


def _seguro():
    try:
        hacer_respaldo()
    except Exception as e:  # el hilo nunca debe morirse por un error
        estado["error"] = str(e)


def _bucle():
    while True:
        _seguro()
        if _detener.wait(INTERVALO_MIN * 60):   # espera, o sale si piden detener
            break


def iniciar():
    global _hilo
    if _hilo and _hilo.is_alive():
        return
    _detener.clear()
    _hilo = threading.Thread(target=_bucle, name="respaldo-automatico", daemon=True)
    _hilo.start()


def detener():
    _detener.set()


def activo() -> bool:
    return bool(_hilo and _hilo.is_alive())


def lanzar_respaldo() -> threading.Thread:
    """Respaldo manual: corre en su propio hilo para no bloquear la petición."""
    hilo = threading.Thread(target=_seguro, name="respaldo-manual", daemon=True)
    hilo.start()
    return hilo
