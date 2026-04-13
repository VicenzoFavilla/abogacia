"""
Router de Feeds RSS — boletines oficiales y fuentes legales.
Equivalente a Zotero Feeds.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.models.feed import Feed, FeedItem
from backend.services.feed_service import refrescar_feed, refrescar_todos_los_feeds, agregar_feeds_predefinidos

router = APIRouter(prefix="/feeds", tags=["Feeds RSS"])


class FeedIn(BaseModel):
    nombre: str
    url: str
    descripcion: Optional[str] = None


class FeedOut(BaseModel):
    id: int
    nombre: str
    url: str
    descripcion: Optional[str]
    activo: bool
    ultima_actualizacion: Optional[datetime]

    class Config:
        from_attributes = True


class FeedItemOut(BaseModel):
    id: int
    feed_id: int
    titulo: str
    url: Optional[str]
    resumen: Optional[str]
    fecha_publicacion: Optional[datetime]
    leido: bool
    importado: bool

    class Config:
        from_attributes = True


@router.post("/predefinidos")
def cargar_feeds_predefinidos(db: Session = Depends(get_db)):
    """Carga feeds legales argentinos predefinidos (Boletín Oficial, InfoLEG)."""
    agregar_feeds_predefinidos(db)
    return {"mensaje": "Feeds predefinidos cargados correctamente"}


@router.post("/", response_model=FeedOut, status_code=201)
def agregar_feed(datos: FeedIn, db: Session = Depends(get_db)):
    """Suscribirse a un nuevo feed RSS."""
    if db.query(Feed).filter(Feed.url == datos.url).first():
        raise HTTPException(status_code=400, detail="Ya estás suscripto a ese feed")
    feed = Feed(**datos.dict())
    db.add(feed)
    db.commit()
    db.refresh(feed)
    return feed


@router.get("/", response_model=List[FeedOut])
def listar_feeds(db: Session = Depends(get_db)):
    return db.query(Feed).all()


@router.post("/{id}/refrescar")
def refrescar_feed_endpoint(id: int, db: Session = Depends(get_db)):
    """Descarga ítems nuevos de un feed específico."""
    feed = db.query(Feed).filter(Feed.id == id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed no encontrado")
    nuevos = refrescar_feed(db, feed)
    return {"mensaje": f"{nuevos} nuevos ítems agregados", "feed_id": id}


@router.post("/refrescar-todos")
def refrescar_todos(db: Session = Depends(get_db)):
    """Refresca todos los feeds activos."""
    resumen = refrescar_todos_los_feeds(db)
    return {"resumen": resumen}


@router.get("/items", response_model=List[FeedItemOut])
def listar_items(
    feed_id: Optional[int] = None,
    solo_no_leidos: bool = False,
    db: Session = Depends(get_db)
):
    """Lista ítems de feeds, con filtros opcionales."""
    q = db.query(FeedItem)
    if feed_id:
        q = q.filter(FeedItem.feed_id == feed_id)
    if solo_no_leidos:
        q = q.filter(FeedItem.leido == False)
    return q.order_by(FeedItem.fecha_publicacion.desc()).limit(100).all()


@router.post("/items/{id}/marcar-leido")
def marcar_leido(id: int, db: Session = Depends(get_db)):
    item = db.query(FeedItem).filter(FeedItem.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    item.leido = True
    db.commit()
    return {"mensaje": "Marcado como leído"}


@router.delete("/{id}")
def eliminar_feed(id: int, db: Session = Depends(get_db)):
    feed = db.query(Feed).filter(Feed.id == id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed no encontrado")
    db.delete(feed)
    db.commit()
    return {"mensaje": "Feed eliminado"}
