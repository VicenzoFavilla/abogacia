from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from backend.database import Base
from datetime import datetime

class Documento(Base):
    __tablename__ = "documento"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"))
    nombre = Column(String, nullable=False)
    tipo = Column(String)
    ruta_archivo = Column(String, nullable=False)
    fecha_subida = Column(DateTime, default=datetime.utcnow)
