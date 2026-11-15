from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database import get_db
from servicios.reporte import ReporteServicio

router = APIRouter()

@router.get("/resumen", summary="Reporte con colecciones (Counter, defaultdict, set, deque)")
def resumen(dias: int = 30, db: Session = Depends(get_db)):
    return ReporteServicio.resumen(db, dias)

@router.get("/csv/{entidad}", summary="Exportar una tabla a CSV")
def exportar(entidad: str, db: Session = Depends(get_db)):
    try:
        contenido = ReporteServicio.exportar_csv(db, entidad)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    # utf-8-sig: Excel abre bien las tildes y la ñ
    return Response(
        content=contenido.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{entidad}.csv"'},
    )
