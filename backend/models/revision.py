"""
Modelo de Revisión — historial de versiones de documentos editables.
Equivalente al sistema de versiones de Google Docs.
"""
from sqlalchemy import Column, Integer, Text, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Revision(Base):
    __tablename__ = "revisiones"

    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, ForeignKey("documentos.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # Contenido completo como HTML (convertido desde docx con mammoth)
    contenido_html = Column(Text, nullable=False)

    # Metadatos de la revisión
    mensaje = Column(String(500), nullable=True)   # descripción del cambio
    es_autoguardado = Column(Boolean, default=True)
    tamaño_bytes = Column(Integer, nullable=True)

    fecha = Column(DateTime, default=datetime.utcnow, index=True)

    # Relaciones
    documento = relationship("Documento", back_populates="revisiones")
    usuario = relationship("Usuario", back_populates="revisiones")
