from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, String
from datetime import datetime, timezone
from backend.database import Base

class Anotacion(Base):
    __tablename__ = "anotaciones"

    id = Column(Integer, primary_key=True, index=True)
    texto = Column(Text)
    autor = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)
    documento_id = Column(Integer, ForeignKey("documentos.id"))
