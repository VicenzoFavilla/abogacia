from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.anotacion import Anotacion
from backend.models.documento import Documento
from backend.schemas.anotacion import AnotacionCreate, AnotacionOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/documentos/{documento_id}/anotaciones", response_model=AnotacionOut)
def crear_anotacion(documento_id: int, anotacion: AnotacionCreate, db: Session = Depends(get_db)):
    if not db.query(Documento).filter(Documento.id == documento_id).first():
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    nueva = Anotacion(documento_id=documento_id, **anotacion.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/documentos/{documento_id}/anotaciones", response_model=list[AnotacionOut])
def listar_anotaciones(documento_id: int, db: Session = Depends(get_db)):
    return db.query(Anotacion).filter(Anotacion.documento_id == documento_id).all()
