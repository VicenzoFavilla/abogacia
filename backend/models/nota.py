"""
Modelo de Nota standalone — equivalente a Zotero Notes.
Notas con rich text (HTML), ligadas a un documento y/o caso.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Nota(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(300), nullable=True, default="Nota sin título")
    contenido_html = Column(Text, nullable=True, default="")

    # Una nota puede estar ligada a un documento, a un caso, o a ambos (o a ninguno)
    documento_id = Column(Integer, ForeignKey("documentos.id", ondelete="SET NULL"), nullable=True)
    caso_id = Column(Integer, ForeignKey("casos.id", ondelete="SET NULL"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="notas")
    documento = relationship("Documento", back_populates="notas")
    caso = relationship("Caso", back_populates="notas")
