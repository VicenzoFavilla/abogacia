"""
Router de exportación — citas jurídicas, BibTeX, RIS, CSV.
Equivalente a Zotero Create Bibliography / Export.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.documento import Documento
from backend.services.exportacion_service import (
    formatear_cita_juridica, exportar_bibtex, exportar_ris, exportar_csv
)

router = APIRouter(prefix="/exportar", tags=["Exportación"])


def _get_docs(ids: List[int], db: Session) -> List[Documento]:
    docs = db.query(Documento).filter(Documento.id.in_(ids)).all()
    if not docs:
        raise HTTPException(status_code=404, detail="No se encontraron documentos")
    return docs


@router.get("/cita/{documento_id}")
def obtener_cita(documento_id: int, db: Session = Depends(get_db)):
    """Genera la cita jurídica de UN documento en formato argentino."""
    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return {"documento_id": documento_id, "cita": formatear_cita_juridica(doc)}


@router.get("/bibtex")
def exportar_bibtex_endpoint(ids: str = Query(..., description="IDs separados por coma: 1,2,3"), db: Session = Depends(get_db)):
    """Exporta los documentos en formato BibTeX."""
    id_list = [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()]
    docs = _get_docs(id_list, db)
    contenido = exportar_bibtex(docs)
    return Response(content=contenido, media_type="application/x-bibtex",
                    headers={"Content-Disposition": "attachment; filename=exportacion.bib"})


@router.get("/ris")
def exportar_ris_endpoint(ids: str = Query(..., description="IDs separados por coma"), db: Session = Depends(get_db)):
    """Exporta los documentos en formato RIS."""
    id_list = [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()]
    docs = _get_docs(id_list, db)
    contenido = exportar_ris(docs)
    return Response(content=contenido, media_type="application/x-research-info-systems",
                    headers={"Content-Disposition": "attachment; filename=exportacion.ris"})


@router.get("/csv")
def exportar_csv_endpoint(ids: str = Query(..., description="IDs separados por coma"), db: Session = Depends(get_db)):
    """Exporta los documentos como CSV."""
    id_list = [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()]
    docs = _get_docs(id_list, db)
    contenido = exportar_csv(docs)
    return Response(content=contenido, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=exportacion.csv"})
