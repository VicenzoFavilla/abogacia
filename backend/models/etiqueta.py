from sqlalchemy import Column, Integer, String
from backend.database import Base

class Etiqueta(Base):
    __tablename__ = "etiquetas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
