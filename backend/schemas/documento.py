from pydantic import BaseModel
from datetime import datetime

class DocumentoOut(BaseModel):
    id: int
    nombre: str
    tipo: str | None = None
    ruta_archivo: str
    caso_id: int
    fecha_subida: datetime

    model_config = {
        "from_attributes": True
    }
