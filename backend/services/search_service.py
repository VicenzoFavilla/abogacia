"""
Servicio de búsqueda full-text y avanzada.
Usa LIKE con índices para SQLite; compatible con pg_trgm en PostgreSQL.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
from datetime import datetime

from backend.models.documento import Documento
from backend.models.caso import Caso
from backend.models.metadata_legal import MetadataLegal
from backend.models.etiqueta import Etiqueta
from backend.models.doc_etiqueta import documento_etiqueta


def busqueda_rapida(db: Session, query: str, limite: int = 50) -> List[Documento]:
    """Búsqueda rápida en nombre y contenido_texto."""
    q = f"%{query}%"
    return (
        db.query(Documento)
        .filter(or_(
            Documento.nombre.ilike(q),
            Documento.contenido_texto.ilike(q),
        ))
        .limit(limite)
        .all()
    )


def busqueda_avanzada(
    db: Session,
    texto: Optional[str] = None,
    tipo_documento: Optional[str] = None,
    jurisdiccion: Optional[str] = None,
    tribunal: Optional[str] = None,
    materia: Optional[str] = None,
    numero_expediente: Optional[str] = None,
    etiqueta_ids: Optional[List[int]] = None,
    caso_id: Optional[int] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    limite: int = 100,
    offset: int = 0,
) -> dict:
    """
    Búsqueda avanzada con múltiples filtros combinables.
    Retorna {"total": N, "items": [...]}
    """
    query = db.query(Documento)

    # Filtro de texto libre
    if texto:
        q = f"%{texto}%"
        query = query.filter(or_(
            Documento.nombre.ilike(q),
            Documento.contenido_texto.ilike(q),
        ))

    # Filtros sobre MetadataLegal (JOIN solo si se necesita)
    needs_metadata = any([tipo_documento, jurisdiccion, tribunal, materia, numero_expediente, fecha_desde, fecha_hasta])
    if needs_metadata:
        query = query.outerjoin(MetadataLegal, MetadataLegal.documento_id == Documento.id)
        if tipo_documento:
            query = query.filter(MetadataLegal.tipo_documento == tipo_documento)
        if jurisdiccion:
            query = query.filter(MetadataLegal.jurisdiccion.ilike(f"%{jurisdiccion}%"))
        if tribunal:
            query = query.filter(MetadataLegal.tribunal.ilike(f"%{tribunal}%"))
        if materia:
            query = query.filter(MetadataLegal.materia.ilike(f"%{materia}%"))
        if numero_expediente:
            query = query.filter(MetadataLegal.numero_expediente.ilike(f"%{numero_expediente}%"))
        if fecha_desde:
            query = query.filter(MetadataLegal.fecha_resolucion >= fecha_desde)
        if fecha_hasta:
            query = query.filter(MetadataLegal.fecha_resolucion <= fecha_hasta)

    # Filtro por etiquetas
    if etiqueta_ids:
        query = query.join(
            documento_etiqueta,
            documento_etiqueta.c.documento_id == Documento.id
        ).filter(documento_etiqueta.c.etiqueta_id.in_(etiqueta_ids))

    # Filtro por caso
    if caso_id:
        query = query.filter(Documento.caso_id == caso_id)

    total = query.count()
    items = query.offset(offset).limit(limite).all()

    return {"total": total, "items": items}
