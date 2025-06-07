from pydantic import BaseModel
from datetime import datetime

class AnotacionBase(BaseModel):
    texto: str
    autor: str | None = None

class AnotacionCreate(AnotacionBase):
    pass

class AnotacionOut(AnotacionBase):
    id: int
    documento_id: int
    fecha: datetime

    model_config = {
        "from_attributes": True
    }
