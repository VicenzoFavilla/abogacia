from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, String, Float, JSON
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from backend.database import Base


class Anotacion(Base):
    __tablename__ = "anotaciones"

    id = Column(Integer, primary_key=True, index=True)

    # Tipo de anotación
    tipo = Column(String(30), default="comentario")
    # Valores: comentario | resaltado | subrayado | marcador | area

    # Contenido
    texto = Column(Text, nullable=True)
    contenido_html = Column(Text, nullable=True)   # Para notas con formato
    color = Column(String(7), nullable=True, default="#FFFF00")  # Color del resaltado

    # Autor
    autor = Column(String(100), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # Posición en el PDF / documento
    pagina = Column(Integer, nullable=True)              # Número de página
    posicion_pdf = Column(JSON, nullable=True)
    # Formato: {"x1": 0.1, "y1": 0.2, "x2": 0.5, "y2": 0.3, "rects": [...]}

    # Texto resaltado (el fragmento exacto seleccionado)
    texto_seleccionado = Column(Text, nullable=True)

    fecha = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # FK
    documento_id = Column(Integer, ForeignKey("documentos.id", ondelete="CASCADE"), nullable=False)
    documento = relationship("Documento", back_populates="anotaciones")
