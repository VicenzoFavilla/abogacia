"""Modelo de Colección jerárquica — equivalente a Zotero Collections."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from backend.database import Base


class Coleccion(Base):
    __tablename__ = "colecciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(String(500), nullable=True)
    color = Column(String(7), nullable=True, default="#4A90D9")   # hex color
    icono = Column(String(50), nullable=True, default="folder")
    orden = Column(Integer, default=0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Auto-referencial para anidamiento
    padre_id = Column(Integer, ForeignKey("colecciones.id"), nullable=True)
    hijos = relationship(
        "Coleccion",
        backref=backref("padre", remote_side=[id]),
        cascade="all, delete-orphan"
    )

    # FK a usuario
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario = relationship("Usuario", back_populates="colecciones")

    # Casos en esta colección
    casos = relationship("Caso", back_populates="coleccion")
