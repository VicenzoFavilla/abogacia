"""
Feed RSS — suscripciones a boletines oficiales y fuentes legales.
Equivalente a Zotero Feeds.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    descripcion = Column(String(500), nullable=True)
    activo = Column(Boolean, default=True)
    ultima_actualizacion = Column(DateTime, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # Ítems del feed
    items = relationship("FeedItem", back_populates="feed", cascade="all, delete-orphan")


class FeedItem(Base):
    __tablename__ = "feed_items"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id", ondelete="CASCADE"), nullable=False)

    titulo = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=True)
    resumen = Column(Text, nullable=True)
    fecha_publicacion = Column(DateTime, nullable=True)
    guid = Column(String(500), unique=True, nullable=True)   # ID único del feed

    leido = Column(Boolean, default=False)
    importado = Column(Boolean, default=False)   # Si ya fue importado a la biblioteca
    documento_id = Column(Integer, ForeignKey("documentos.id"), nullable=True)

    fecha_descubierto = Column(DateTime, default=datetime.utcnow)

    feed = relationship("Feed", back_populates="items")
