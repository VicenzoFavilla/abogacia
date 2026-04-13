"""
Router de Colecciones jerárquicas.
Equivalente a Zotero Collections (árbol de carpetas).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from backend.database import get_db
from backend.models.coleccion import Coleccion

router = APIRouter(prefix="/colecciones", tags=["Colecciones"])


class ColeccionIn(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    color: Optional[str] = "#4A90D9"
    icono: Optional[str] = "folder"
    padre_id: Optional[int] = None
    orden: Optional[int] = 0


class ColeccionOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    color: Optional[str]
    icono: Optional[str]
    padre_id: Optional[int]
    orden: int

    class Config:
        from_attributes = True



@router.post("/", response_model=ColeccionOut, status_code=201)
def crear_coleccion(datos: ColeccionIn, db: Session = Depends(get_db)):
    """Crea una nueva colección (o sub-colección si se provee padre_id)."""
    if datos.padre_id:
        padre = db.query(Coleccion).filter(Coleccion.id == datos.padre_id).first()
        if not padre:
            raise HTTPException(status_code=404, detail="Colección padre no encontrada")
    nueva = Coleccion(**datos.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.get("/", response_model=List[ColeccionOut])
def listar_colecciones(db: Session = Depends(get_db)):
    """Devuelve solo las colecciones raíz (sin padre). Los hijos vienen anidados."""
    return db.query(Coleccion).filter(Coleccion.padre_id == None).order_by(Coleccion.orden).all()


@router.get("/{id}", response_model=ColeccionOut)
def obtener_coleccion(id: int, db: Session = Depends(get_db)):
    col = db.query(Coleccion).filter(Coleccion.id == id).first()
    if not col:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return col


@router.put("/{id}", response_model=ColeccionOut)
def actualizar_coleccion(id: int, datos: ColeccionIn, db: Session = Depends(get_db)):
    col = db.query(Coleccion).filter(Coleccion.id == id).first()
    if not col:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    for k, v in datos.dict(exclude_unset=True).items():
        setattr(col, k, v)
    db.commit()
    db.refresh(col)
    return col


@router.delete("/{id}")
def eliminar_coleccion(id: int, db: Session = Depends(get_db)):
    col = db.query(Coleccion).filter(Coleccion.id == id).first()
    if not col:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    db.delete(col)
    db.commit()
    return {"mensaje": "Colección eliminada"}
