from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base
from backend.models.doc_etiqueta import DocumentoEtiqueta  # ✅ Correcto

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    ruta_archivo = Column(String)
    fecha_subida = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String)
    caso_id = Column(Integer, ForeignKey("casos.id"))

    etiquetas = relationship(
        "Etiqueta",
        secondary=DocumentoEtiqueta,
        back_populates="documentos"
    )