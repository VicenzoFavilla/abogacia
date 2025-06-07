from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.documento import Documento
from fastapi.responses import FileResponse
from backend.models.documento import Documento
from backend.schemas.documento import DocumentoOut
from backend.models.etiqueta import Etiqueta
from backend.models.doc_etiqueta import DocumentoEtiqueta
import shutil
import os
from uuid import uuid4

router = APIRouter()

UPLOAD_FOLDER = "uploads"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/documentos/")
def subir_documento(
    archivo: UploadFile = File(...),
    nombre: str = Form(...),
    tipo: str = Form(None),
    caso_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Crear nombre único para evitar conflictos
    extension = os.path.splitext(archivo.filename)[1]
    filename = f"{uuid4().hex}{extension}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Guardar archivo en carpeta /uploads
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(archivo.file, buffer)

    # Registrar en base de datos
    nuevo_doc = Documento(
        nombre=nombre,
        tipo=tipo,
        ruta_archivo=filepath,
        caso_id=caso_id
    )
    db.add(nuevo_doc)
    db.commit()
    db.refresh(nuevo_doc)

    return {"mensaje": "Documento subido", "documento_id": nuevo_doc.id}


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
    for etiqueta_id in etiquetas:
        existe = db.query(DocumentoEtiqueta).filter_by(documento_id=documento_id, etiqueta_id=etiqueta_id).first()
        if not existe:
            nueva_relacion = DocumentoEtiqueta(documento_id=documento_id, etiqueta_id=etiqueta_id)
            db.add(nueva_relacion)
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

    # Borrar archivo físico si existe
    if os.path.exists(documento.ruta_archivo):
        os.remove(documento.ruta_archivo)

    db.delete(documento)
    db.commit()

    return {"mensaje": "Documento eliminado"}
