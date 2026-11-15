from fastapi import APIRouter
from servicios import respaldo

# Solo administrador (se exige en main.py)
router = APIRouter()

@router.post("/", status_code=202, summary="Lanzar un respaldo ahora (en un hilo aparte)")
def lanzar():
    respaldo.lanzar_respaldo()
    return {"mensaje": "Respaldo iniciado en segundo plano"}

@router.get("/", summary="Estado del respaldo automático y archivos guardados")
def estado():
    return {
        "automatico_activo": respaldo.activo(),
        "cada_minutos": respaldo.INTERVALO_MIN,
        "ultimo": respaldo.estado["ultimo"],
        "error": respaldo.estado["error"],
        "archivos": respaldo.listar(),
    }
