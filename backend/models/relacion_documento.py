"""
Modelo de Relación entre documentos — equivalente a Zotero Related Items.
Permite ligar sentencias, leyes que se citan, modifican o derogan entre sí.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base
import enum


class TipoRelacion(str, enum.Enum):
    cita = "cita"
    responde_a = "responde_a"
    modifica = "modifica"
    deroga = "deroga"
    complementa = "complementa"
    relacionado = "relacionado"


class RelacionDocumento(Base):
    __tablename__ = "relaciones_documentos"

    id = Column(Integer, primary_key=True, index=True)
    documento_origen_id = Column(Integer, ForeignKey("documentos.id", ondelete="CASCADE"), nullable=False)
    documento_destino_id = Column(Integer, ForeignKey("documentos.id", ondelete="CASCADE"), nullable=False)
    tipo_relacion = Column(Enum(TipoRelacion), default=TipoRelacion.relacionado)
    observacion = Column(String(500), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    origen = relationship("Documento", foreign_keys=[documento_origen_id], back_populates="relaciones_salientes")
    destino = relationship("Documento", foreign_keys=[documento_destino_id], back_populates="relaciones_entrantes")
