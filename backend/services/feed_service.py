"""
Servicio de Feeds RSS — equivalente a Zotero Feeds.
Parsea fuentes legales: SAIJ, Infoleg, Boletín Oficial.
"""
import feedparser
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.models.feed import Feed, FeedItem

# Feeds legales argentinos predefinidos
FEEDS_PREDEFINIDOS = [
    {
        "nombre": "Boletín Oficial Argentina",
        "url": "https://www.boletinoficial.gob.ar/rss/boletinOficial.rss",
        "descripcion": "Publicaciones oficiales del Estado Nacional argentino"
    },
    {
        "nombre": "InfoLEG — Nuevas normas",
        "url": "http://www.infoleg.gob.ar/rss.php",
        "descripcion": "Centro de Documentación e Información del Ministerio de Justicia"
    },
]


def refrescar_feed(db: Session, feed: Feed) -> int:
    """
    Descarga los últimos ítems de un feed y los agrega a la BD.
    Retorna cantidad de nuevos ítems agregados.
    """
    try:
        parsed = feedparser.parse(feed.url)
    except Exception:
        return 0

    nuevos = 0
    for entry in parsed.entries:
        guid = getattr(entry, "id", None) or getattr(entry, "link", None)
        if not guid:
            continue

        # Evitar duplicados por GUID
        existente = db.query(FeedItem).filter(FeedItem.guid == guid).first()
        if existente:
            continue

        # Fecha de publicación
        fecha_pub = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            fecha_pub = datetime(*entry.published_parsed[:6])

        item = FeedItem(
            feed_id=feed.id,
            titulo=getattr(entry, "title", "Sin título")[:499],
            url=getattr(entry, "link", None),
            resumen=getattr(entry, "summary", None),
            fecha_publicacion=fecha_pub,
            guid=guid[:499],
        )
        db.add(item)
        nuevos += 1

    feed.ultima_actualizacion = datetime.utcnow()
    db.commit()
    return nuevos


def refrescar_todos_los_feeds(db: Session) -> dict:
    """Refresca todos los feeds activos. Retorna resumen."""
    feeds = db.query(Feed).filter(Feed.activo == True).all()
    resumen = {}
    for feed in feeds:
        nuevos = refrescar_feed(db, feed)
        resumen[feed.nombre] = nuevos
    return resumen


def agregar_feeds_predefinidos(db: Session):
    """Añade los feeds legales argentinos por defecto si no existen."""
    for f in FEEDS_PREDEFINIDOS:
        existe = db.query(Feed).filter(Feed.url == f["url"]).first()
        if not existe:
            nuevo = Feed(**f)
            db.add(nuevo)
    db.commit()
