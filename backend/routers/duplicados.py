"""
Router de duplicados — detecta documentos duplicados.
Equivalente a Zotero Duplicate Detection.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from backend.database import get_db
from backend.models.documento import Documento
from backend.services.duplicados_service import listar_grupos_duplicados

router = APIRouter(prefix="/duplicados", tags=["Duplicados"])


@router.get("/")
def obtener_duplicados(db: Session = Depends(get_db)):
    """
    Lista grupos de documentos duplicados (mismo hash SHA-256).
    Cada grupo tiene 2 o más documentos idénticos.
    """
    grupos = listar_grupos_duplicados(db)
    resultado = []
    for grupo in grupos:
        resultado.append([
            {"id": d.id, "nombre": d.nombre, "tipo": d.tipo, "fecha_subida": d.fecha_subida}
            for d in grupo
        ])
    return {"grupos_duplicados": resultado, "total_grupos": len(resultado)}


@router.delete("/merge/{id_conservar}/{id_eliminar}")
def fusionar_documentos(id_conservar: int, id_eliminar: int, db: Session = Depends(get_db)):
    """
    Fusiona dos documentos: conserva uno y elimina el otro.
    Las anotaciones y relaciones del eliminado se reasignan al conservado.
    """
    doc_conservar = db.query(Documento).filter(Documento.id == id_conservar).first()
    doc_eliminar = db.query(Documento).filter(Documento.id == id_eliminar).first()

    if not doc_conservar or not doc_eliminar:
        raise HTTPException(status_code=404, detail="Uno o ambos documentos no existen")

    # Reasignar anotaciones
    for anotacion in doc_eliminar.anotaciones:
        anotacion.documento_id = id_conservar

    # Reasignar notas
    for nota in doc_eliminar.notas:
        nota.documento_id = id_conservar

    db.delete(doc_eliminar)
    db.commit()

    return {
        "mensaje": f"Documento #{id_eliminar} fusionado con #{id_conservar}",
        "documento_conservado": id_conservar
    }
