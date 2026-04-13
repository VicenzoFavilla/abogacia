from pydantic import BaseModel
from typing import Optional


class CasoBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    estado: Optional[str] = "activo"
    coleccion_id: Optional[int] = None


class CasoCreate(CasoBase):
    pass


class CasoOut(CasoBase):
    id: int

    model_config = {"from_attributes": True}