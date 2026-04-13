"""Modelo de Usuario para autenticación JWT."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)
    es_admin = Column(Boolean, default=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    colecciones = relationship("Coleccion", back_populates="usuario", cascade="all, delete-orphan")
    notas = relationship("Nota", back_populates="usuario", cascade="all, delete-orphan")
    revisiones = relationship("Revision", back_populates="usuario")
