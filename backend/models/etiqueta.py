from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.doc_etiqueta import DocumentoEtiqueta

class Etiqueta(Base):
    __tablename__ = "etiquetas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True)

    documentos = relationship(
        "Documento",
        secondary="documento_etiqueta",
        back_populates="etiquetas"
    )
