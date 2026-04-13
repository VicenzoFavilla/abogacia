from sqlalchemy import Table, Column, Integer, ForeignKey
from backend.database import Base

documento_etiqueta = Table(
    "documento_etiqueta",
    Base.metadata,
    Column("documento_id", Integer, ForeignKey("documentos.id"), primary_key=True),
    Column("etiqueta_id", Integer, ForeignKey("etiquetas.id"), primary_key=True)
)
