from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.etiqueta import Etiqueta
from backend.schemas.etiqueta import EtiquetaCreate, EtiquetaOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/etiquetas/", response_model=EtiquetaOut)
def crear_etiqueta(etiqueta: EtiquetaCreate, db: Session = Depends(get_db)):
    existente = db.query(Etiqueta).filter(Etiqueta.nombre == etiqueta.nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="Etiqueta ya existe")
    nueva = Etiqueta(**etiqueta.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/etiquetas/", response_model=list[EtiquetaOut])
def listar_etiquetas(db: Session = Depends(get_db)):
    return db.query(Etiqueta).all()
