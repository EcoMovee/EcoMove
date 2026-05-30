from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ─── Esquemas para Pago ───

class PagoBase(BaseModel):
    reserva_id: int
    monto: float = Field(..., gt=0)
    metodo_pago: str

class PagoCreate(PagoBase):
    datos_tarjeta: Optional[dict] = None

class PagoResponse(BaseModel):
    pago_id: int
    reserva_id: int
    monto: float
    metodo_pago: str
    estado: str
    fecha_pago: datetime
    transaccion_id: str
    reserva_confirmada: bool

class PagoDB(BaseModel):
    id: int
    reserva_id: int
    usuario_id: int
    monto: float
    metodo_pago: str
    estado: str
    transaccion_id: str
    fecha_pago: datetime
    motivo_rechazo: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Esquemas para Reserva ───

class ReservaBase(BaseModel):
    id: int
    usuario_id: int
    vehiculo_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    costo_estimado: float
    estado: str

    class Config:
        from_attributes = True