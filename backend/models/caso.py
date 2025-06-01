from sqlalchemy import Column, Integer, String, Text, ForeignKey
from backend.database import Base

class Caso(Base):
    __tablename__= "casos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text)
    tipo = Column(String)
    estado = Column(String)