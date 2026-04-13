from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(300), nullable=False)
    ruta_archivo = Column(String(500))
    contenido_texto = Column(String)          # Texto extraído del archivo para FTS
    hash_sha256 = Column(String(64), index=True, nullable=True)  # Para detección de duplicados
    tamaño_bytes = Column(Integer, nullable=True)
    fecha_subida = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String(50))                  # pdf, docx, txt, etc.
    caso_id = Column(Integer, ForeignKey("casos.id"))

    # Etiquetas
    etiquetas = relationship(
        "Etiqueta",
        secondary="documento_etiqueta",
        back_populates="documentos"
    )

    # Editor / Revisiones
    contenido_html_actual = Column(String, nullable=True)  # HTML del contenido editable actual
    revisiones = relationship("Revision", back_populates="documento", cascade="all, delete-orphan")

    # Metadatos legales
    metadata_legal = relationship("MetadataLegal", back_populates="documento", uselist=False, cascade="all, delete-orphan")

    # Notas standalone ligadas al documento
    notas = relationship("Nota", back_populates="documento")

    # Anotaciones sobre el PDF
    anotaciones = relationship("Anotacion", back_populates="documento", cascade="all, delete-orphan")

    # Relaciones entre documentos
    relaciones_salientes = relationship("RelacionDocumento", foreign_keys="RelacionDocumento.documento_origen_id", back_populates="origen", cascade="all, delete-orphan")
    relaciones_entrantes = relationship("RelacionDocumento", foreign_keys="RelacionDocumento.documento_destino_id", back_populates="destino", cascade="all, delete-orphan")