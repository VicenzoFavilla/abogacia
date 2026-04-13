"""
Router de búsqueda — rápida y avanzada.
Equivalente a Zotero Quick Search y Advanced Search.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from backend.database import get_db
from backend.services.search_service import busqueda_rapida, busqueda_avanzada

router = APIRouter(prefix="/buscar", tags=["Búsqueda"])


class BusquedaAvanzadaIn(BaseModel):
    texto: Optional[str] = None
    tipo_documento: Optional[str] = None
    jurisdiccion: Optional[str] = None
    tribunal: Optional[str] = None
    materia: Optional[str] = None
    numero_expediente: Optional[str] = None
    etiqueta_ids: Optional[List[int]] = None
    caso_id: Optional[int] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    limite: int = 50
    offset: int = 0


@router.get("/")
def buscar_rapido(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    """Búsqueda rápida en nombre y contenido de documentos."""
    docs = busqueda_rapida(db, q)
    return {
        "query": q,
        "total": len(docs),
        "resultados": [
            {
                "id": d.id,
                "nombre": d.nombre,
                "tipo": d.tipo,
                "caso_id": d.caso_id,
            }
            for d in docs
        ]
    }


@router.post("/avanzada")
def buscar_avanzado(filtros: BusquedaAvanzadaIn, db: Session = Depends(get_db)):
    """Búsqueda avanzada con múltiples filtros combinables."""
    resultado = busqueda_avanzada(
        db,
        texto=filtros.texto,
        tipo_documento=filtros.tipo_documento,
        jurisdiccion=filtros.jurisdiccion,
        tribunal=filtros.tribunal,
        materia=filtros.materia,
        numero_expediente=filtros.numero_expediente,
        etiqueta_ids=filtros.etiqueta_ids,
        caso_id=filtros.caso_id,
        fecha_desde=filtros.fecha_desde,
        fecha_hasta=filtros.fecha_hasta,
        limite=filtros.limite,
        offset=filtros.offset,
    )
    return resultado
