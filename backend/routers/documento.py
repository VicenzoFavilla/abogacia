from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.documento import Documento
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
