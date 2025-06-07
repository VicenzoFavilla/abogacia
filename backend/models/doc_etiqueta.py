from sqlalchemy import Column, Integer, ForeignKey
from backend.database import Base

class DocumentoEtiqueta(Base):
    __tablename__ = "documento_etiqueta"
    Base.metadata,
    documento_id = Column(Integer, ForeignKey("documentos.id"), primary_key=True)
    etiqueta_id = Column(Integer, ForeignKey("etiquetas.id"), primary_key=True)
