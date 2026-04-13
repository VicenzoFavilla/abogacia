from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend.models.documento import Documento
from fastapi.responses import FileResponse
from backend.schemas.documento import DocumentoOut
from backend.models.etiqueta import Etiqueta
from backend.services.editor_service import extract_text, compute_sha256, get_docx_as_html
import shutil
import os
from uuid import uuid4

router = APIRouter(tags=["Documentos"])

UPLOAD_FOLDER = "uploads"


@router.post("/documentos/")
def subir_documento(
    archivo: UploadFile = File(...),
    nombre: str = Form(...),
    tipo: str = Form(None),
    caso_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Sube un archivo (PDF, Word, TXT) y lo indexa para búsqueda."""
    extension = os.path.splitext(archivo.filename)[1]
    filename = f"{uuid4().hex}{extension}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(archivo.file, buffer)

    # Extraer texto para búsqueda full-text
    tipo_detectado = tipo or extension.lstrip(".").lower()
    contenido_texto = extract_text(filepath, tipo_detectado)

    # Hash SHA-256 para detección de duplicados
    hash_sha256 = compute_sha256(filepath)

    # Tamaño del archivo
    tamaño_bytes = os.path.getsize(filepath)

    # HTML inicial para el editor (si es Word o TXT)
    try:
        contenido_html_actual = get_docx_as_html(filepath) if tipo_detectado in ("docx", "doc", "txt") else None
    except Exception:
        contenido_html_actual = None

    nuevo_doc = Documento(
        nombre=nombre,
        tipo=tipo_detectado,
        ruta_archivo=filepath,
        contenido_texto=contenido_texto,
        hash_sha256=hash_sha256,
        tamaño_bytes=tamaño_bytes,
        contenido_html_actual=contenido_html_actual,
        caso_id=caso_id
    )
    db.add(nuevo_doc)
    db.commit()
    db.refresh(nuevo_doc)

    return {
        "mensaje": "Documento subido",
        "documento_id": nuevo_doc.id,
        "hash": hash_sha256,
        "tiene_contenido_editable": contenido_html_actual is not None,
    }


@router.get("/documentos/", response_model=list[DocumentoOut])
def listar_documentos(db: Session = Depends(get_db)):
    return db.query(Documento).all()


@router.get("/casos/{caso_id}/documentos", response_model=list[DocumentoOut])
def listar_documentos_de_caso(caso_id: int, db: Session = Depends(get_db)):
    return db.query(Documento).filter(Documento.caso_id == caso_id).all()


@router.get("/documentos/{id}/descargar")
def descargar_documento(id: int, db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return FileResponse(path=doc.ruta_archivo, filename=doc.nombre)


@router.post("/documentos/{documento_id}/etiquetas/{etiqueta_id}")
def asignar_etiqueta_a_documento(documento_id: int, etiqueta_id: int, db: Session = Depends(get_db)):
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    etiqueta = db.query(Etiqueta).filter(Etiqueta.id == etiqueta_id).first()
    if not etiqueta:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    if etiqueta in documento.etiquetas:
        raise HTTPException(status_code=400, detail="Etiqueta ya asignada al documento")
    documento.etiquetas.append(etiqueta)
    db.commit()
    return {"mensaje": "Etiqueta asignada exitosamente"}


@router.post("/documentos/{documento_id}/etiquetas")
def asociar_etiquetas(documento_id: int, etiquetas: list[int] = Body(...), db: Session = Depends(get_db)):
    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    etiquetas_obj = db.query(Etiqueta).filter(Etiqueta.id.in_(etiquetas)).all()
    for etiq in etiquetas_obj:
        if etiq not in doc.etiquetas:
            doc.etiquetas.append(etiq)
            
    db.commit()
    return {"mensaje": "Etiquetas asociadas correctamente"}


@router.put("/documentos/{id}")
def actualizar_documento(
    id: int,
    nombre: str = Form(None),
    tipo: str = Form(None),
    caso_id: int = Form(None),
    db: Session = Depends(get_db)
):
    documento = db.query(Documento).filter(Documento.id == id).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    if nombre is not None:
        documento.nombre = nombre
    if tipo is not None:
        documento.tipo = tipo
    if caso_id is not None:
        documento.caso_id = caso_id
    db.commit()
    db.refresh(documento)
    return {"mensaje": "Documento actualizado", "documento": documento.id}


@router.delete("/documentos/{id}")
def eliminar_documento(id: int, db: Session = Depends(get_db)):
    documento = db.query(Documento).filter(Documento.id == id).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    if os.path.exists(documento.ruta_archivo):
        os.remove(documento.ruta_archivo)
    db.delete(documento)
    db.commit()
    return {"mensaje": "Documento eliminado"}
