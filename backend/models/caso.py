from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(300), nullable=False)
    descripcion = Column(String(1000), nullable=True)
    estado = Column(String(50), default="activo")   # activo, cerrado, archivado

    # Colección a la que pertenece (equivalente a Zotero Collection)
    coleccion_id = Column(Integer, ForeignKey("colecciones.id"), nullable=True)
    coleccion = relationship("Coleccion", back_populates="casos")

    # Documentos del caso
    documentos = relationship("Documento", backref="caso")

    # Notas del caso
    notas = relationship("Nota", back_populates="caso")