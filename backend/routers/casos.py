from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.caso import Caso
from backend.schemas.caso import CasoCreate, CasoOut
from typing import Optional

router = APIRouter(tags=["Casos"])


@router.post("/casos/", response_model=CasoOut, status_code=201)
def crear_caso(caso: CasoCreate, db: Session = Depends(get_db)):
    nuevo_caso = Caso(**caso.dict())
    db.add(nuevo_caso)
    db.commit()
    db.refresh(nuevo_caso)
    return nuevo_caso


@router.get("/casos/", response_model=list[CasoOut])
def listar_casos(
    coleccion_id: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Caso)
    if coleccion_id:
        q = q.filter(Caso.coleccion_id == coleccion_id)
    if estado:
        q = q.filter(Caso.estado == estado)
    return q.all()


@router.get("/casos/{id}", response_model=CasoOut)
def obtener_caso(id: int, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return caso


@router.put("/casos/{id}")
def actualizar_caso(id: int, datos: CasoCreate, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    for k, v in datos.dict(exclude_unset=True).items():
        setattr(caso, k, v)
    db.commit()
    db.refresh(caso)
    return caso


@router.delete("/casos/{id}")
def eliminar_caso(id: int, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    db.delete(caso)
    db.commit()
    return {"mensaje": "Caso eliminado"}