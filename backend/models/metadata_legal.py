"""
Metadatos legales ricos — equivalente a los Item Types de Zotero.
Cubre: sentencia, resolución, contrato, ley, decreto, expediente, doctrina.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

import enum


class TipoDocumentoLegal(str, enum.Enum):
    sentencia = "sentencia"
    resolucion = "resolución"
    contrato = "contrato"
    ley = "ley"
    decreto = "decreto"
    expediente = "expediente"
    jurisprudencia = "jurisprudencia"
    doctrina = "doctrina"
    dictamen = "dictamen"
    acuerdo = "acuerdo"
    otro = "otro"


class MetadataLegal(Base):
    __tablename__ = "metadata_legal"

    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, ForeignKey("documentos.id", ondelete="CASCADE"), unique=True)

    tipo_documento = Column(Enum(TipoDocumentoLegal), nullable=True)

    # Identificadores
    numero_expediente = Column(String(200), nullable=True, index=True)
    numero_ley = Column(String(50), nullable=True)           # Para leyes / decretos
    boletin_oficial = Column(String(100), nullable=True)
    doi_url = Column(String(500), nullable=True)

    # Jurisdicción y tribunal
    jurisdiccion = Column(String(200), nullable=True)
    tribunal = Column(String(300), nullable=True)
    camara = Column(String(300), nullable=True)
    sala = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True, default="Argentina")

    # Fechas relevantes
    fecha_resolucion = Column(DateTime, nullable=True)
    fecha_publicacion = Column(DateTime, nullable=True)
    fecha_vigencia = Column(DateTime, nullable=True)

    # Partes del proceso
    partes = Column(JSON, nullable=True)
    # Formato esperado: [{"rol": "actor", "nombre": "..."}, {"rol": "demandado", "nombre": "..."}]

    # Clasificación
    materia = Column(String(200), nullable=True)
    submateria = Column(String(200), nullable=True)
    palabras_clave = Column(JSON, nullable=True)   # ["laboral", "indemnización", ...]

    # Contenido
    resumen = Column(Text, nullable=True)
    doctrina_aplicable = Column(Text, nullable=True)

    # Resultado legal
    resultado = Column(String(200), nullable=True)   # "Hace lugar", "No hace lugar", etc.
    votos = Column(JSON, nullable=True)               # [{"juez": "...", "voto": "mayoría"}]

    fecha_carga = Column(DateTime, default=datetime.utcnow)

    # Relación con documento
    documento = relationship("Documento", back_populates="metadata_legal")
