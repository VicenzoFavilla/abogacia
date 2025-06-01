from pydantic import BaseModel

class EtiquetaBase(BaseModel):
    nombre: str

class EtiquetaCreate(EtiquetaBase):
    pass

class EtiquetaOut(EtiquetaBase):
    id: int

    model_config = {
        "from_attributes": True
    }
