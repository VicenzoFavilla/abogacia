from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.caso import Caso
from backend.schemas.caso import CasoCreate, CasoOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/casos/", response_model=CasoOut)
def crear_caso(caso : CasoCreate, db: Session = Depends(get_db)):
    nuevo_caso = Caso(**caso.dict())
    db.add(nuevo_caso)
    db.commit()
    db.refresh(nuevo_caso)
    return nuevo_caso


@router.get("/casos/", response_model=list[CasoOut])
def listar_casos(db:Session = Depends(get_db)):
    return db.query(Caso).all()