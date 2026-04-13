"""
Router de Notas standalone — rich text notes.
Equivalente a Zotero Notes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from backend.database import get_db
from backend.models.nota import Nota

router = APIRouter(prefix="/notas", tags=["Notas"])


class NotaIn(BaseModel):
    titulo: Optional[str] = "Nota sin título"
    contenido_html: Optional[str] = ""
    documento_id: Optional[int] = None
    caso_id: Optional[int] = None


class NotaOut(BaseModel):
    id: int
    titulo: Optional[str]
    contenido_html: Optional[str]
    documento_id: Optional[int]
    caso_id: Optional[int]
    fecha_creacion: datetime
    fecha_modificacion: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=NotaOut, status_code=201)
def crear_nota(datos: NotaIn, db: Session = Depends(get_db)):
    nota = Nota(**datos.dict())
    db.add(nota)
    db.commit()
    db.refresh(nota)
    return nota


@router.get("/", response_model=List[NotaOut])
def listar_notas(
    documento_id: Optional[int] = None,
    caso_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Nota)
    if documento_id:
        q = q.filter(Nota.documento_id == documento_id)
    if caso_id:
        q = q.filter(Nota.caso_id == caso_id)
    return q.order_by(Nota.fecha_modificacion.desc()).all()


@router.get("/{id}", response_model=NotaOut)
def obtener_nota(id: int, db: Session = Depends(get_db)):
    nota = db.query(Nota).filter(Nota.id == id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return nota


@router.put("/{id}", response_model=NotaOut)
def actualizar_nota(id: int, datos: NotaIn, db: Session = Depends(get_db)):
    nota = db.query(Nota).filter(Nota.id == id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    for k, v in datos.dict(exclude_unset=True).items():
        setattr(nota, k, v)
    nota.fecha_modificacion = datetime.utcnow()
    db.commit()
    db.refresh(nota)
    return nota


@router.delete("/{id}")
def eliminar_nota(id: int, db: Session = Depends(get_db)):
    nota = db.query(Nota).filter(Nota.id == id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    db.delete(nota)
    db.commit()
    return {"mensaje": "Nota eliminada"}
