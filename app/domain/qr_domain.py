from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoQR(str, Enum):
    ACTIVO = "activo"
    USADO = "usado"
    EXPIRADO = "expirado"

class QR(BaseModel):
    id: Optional[int] = None
    reserva_id: int
    vehiculo_id: int
    codigo_hash: str
    codigo_qr_base64: str
    estado: EstadoQR = EstadoQR.ACTIVO
    fecha_generacion: datetime = datetime.now()
    fecha_expiracion: datetime
    fecha_uso: Optional[datetime] = None