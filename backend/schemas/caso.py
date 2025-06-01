from pydantic import BaseModel

class CasoBase(BaseModel):
    titulo : str
    descripcion : str | None = None
    tipo: str | None = None
    estado: str | None = "Activo"

class CasoCreate(CasoBase):
    pass

from pydantic import BaseModel

class CasoOut(BaseModel):
    id: int
    titulo: str
    descripcion: str | None = None
    tipo: str | None = None
    estado: str | None = None

    model_config = {
        "from_attributes": True
    }