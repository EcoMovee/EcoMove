from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ResultadoEscaneo(str, Enum):
    EXITOSO = "exitoso"
    FALLIDO = "fallido"

class LogEscaneoQR(BaseModel):
    id: Optional[int] = None
    qr_id: int
    usuario_id: int
    fecha_intento: datetime = datetime.now()
    resultado: ResultadoEscaneo
    motivo: Optional[str] = None
    ip_origen: Optional[str] = None