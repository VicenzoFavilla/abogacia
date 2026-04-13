"""
Router del editor de documentos con auto-guardado.
⭐ Funcionalidad clave: ver y editar Word/PDF dentro de Flutter.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.models.documento import Documento
from backend.models.revision import Revision
from backend.services.editor_service import get_docx_as_html, html_to_docx
from backend.routers.auth import get_current_user
from backend.models.usuario import Usuario

router = APIRouter(prefix="/documentos", tags=["Editor de Documentos"])


class ContenidoIn(BaseModel):
    contenido_html: str
    mensaje: Optional[str] = None    # Descripción del cambio (vacío = autoguardado)
    es_autoguardado: bool = True


class RevisionOut(BaseModel):
    id: int
    mensaje: Optional[str]
    es_autoguardado: bool
    tamaño_bytes: Optional[int]
    fecha: datetime
    usuario_id: Optional[int]

    class Config:
        from_attributes = True


# ── GET contenido editable ─────────────────────────────────────────────────────

@router.get("/{id}/contenido")
def get_contenido(id: int, db: Session = Depends(get_db)):
    """
    Devuelve el contenido editable del documento como HTML.
    Si tiene HTML guardado, lo retorna. Si no, convierte el archivo original.
    """
    doc = db.query(Documento).filter(Documento.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    # Primero intentar el HTML ya guardado
    if doc.contenido_html_actual:
        return {
            "documento_id": id,
            "nombre": doc.nombre,
            "tipo": doc.tipo,
            "contenido_html": doc.contenido_html_actual,
            "editable": True,
        }

    # Si no hay HTML guardado, convertir desde el archivo original
    if not doc.ruta_archivo:
        raise HTTPException(status_code=400, detail="El documento no tiene archivo adjunto")

    try:
        html = get_docx_as_html(doc.ruta_archivo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")

    # Guardar el HTML inicial
    doc.contenido_html_actual = html
    db.commit()

    return {
        "documento_id": id,
        "nombre": doc.nombre,
        "tipo": doc.tipo,
        "contenido_html": html,
        "editable": doc.tipo not in ("pdf",),  # PDFs son solo lectura
    }


# ── PUT auto-guardado ──────────────────────────────────────────────────────────

@router.put("/{id}/contenido")
def guardar_contenido(
    id: int,
    datos: ContenidoIn,
    db: Session = Depends(get_db),
    current_user: Optional[Usuario] = Depends(get_current_user),
):
    """
    Guarda el HTML editado del documento (llamado desde Flutter con debounce 2s).
    Crea automáticamente una Revision para historial.
    """
    doc = db.query(Documento).filter(Documento.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    html = datos.contenido_html

    # Si el contenido no cambió, no crear revisión
    if doc.contenido_html_actual == html:
        return {"mensaje": "Sin cambios", "documento_id": id}

    # Actualizar el HTML actual
    doc.contenido_html_actual = html

    # Crear revisión (historial)
    revision = Revision(
        documento_id=id,
        contenido_html=html,
        mensaje=datos.mensaje or ("Auto-guardado" if datos.es_autoguardado else "Guardado manual"),
        es_autoguardado=datos.es_autoguardado,
        tamaño_bytes=len(html.encode("utf-8")),
        usuario_id=current_user.id if current_user else None,
    )
    db.add(revision)
    db.commit()

    return {
        "mensaje": "Guardado correctamente",
        "documento_id": id,
        "revision_id": revision.id,
        "fecha": revision.fecha,
    }


# ── GET historial de revisiones ────────────────────────────────────────────────

@router.get("/{id}/revisiones", response_model=List[RevisionOut])
def listar_revisiones(id: int, db: Session = Depends(get_db), limite: int = 50):
    """Lista el historial de versiones de un documento."""
    doc = db.query(Documento).filter(Documento.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    return (
        db.query(Revision)
        .filter(Revision.documento_id == id)
        .order_by(Revision.fecha.desc())
        .limit(limite)
        .all()
    )


# ── POST restaurar versión ─────────────────────────────────────────────────────

@router.post("/{id}/revisiones/{revision_id}/restaurar")
def restaurar_revision(id: int, revision_id: int, db: Session = Depends(get_db)):
    """Restaura el documento a una versión anterior."""
    revision = db.query(Revision).filter(
        Revision.id == revision_id,
        Revision.documento_id == id
    ).first()
    if not revision:
        raise HTTPException(status_code=404, detail="Revisión no encontrada")

    doc = db.query(Documento).filter(Documento.id == id).first()
    doc.contenido_html_actual = revision.contenido_html

    # Registrar la restauración como nueva revisión
    nueva = Revision(
        documento_id=id,
        contenido_html=revision.contenido_html,
        mensaje=f"Restaurado desde revisión #{revision_id}",
        es_autoguardado=False,
        tamaño_bytes=len(revision.contenido_html.encode("utf-8")),
    )
    db.add(nueva)
    db.commit()

    return {"mensaje": f"Documento restaurado a revisión #{revision_id}", "nueva_revision_id": nueva.id}


# ── GET exportar como .docx ────────────────────────────────────────────────────

@router.get("/{id}/exportar-docx")
def exportar_docx(id: int, db: Session = Depends(get_db)):
    """Convierte el HTML actual del documento a .docx y lo descarga."""
    from fastapi.responses import FileResponse
    import tempfile, os

    doc = db.query(Documento).filter(Documento.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    if not doc.contenido_html_actual:
        raise HTTPException(status_code=400, detail="El documento no tiene contenido editable guardado")

    # Guardar en archivo temporal
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    tmp.close()
    html_to_docx(doc.contenido_html_actual, tmp.name)

    return FileResponse(
        path=tmp.name,
        filename=f"{doc.nombre or 'documento'}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
