from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class DatosTarjeta(BaseModel):
    numero: str = Field(..., min_length=13, max_length=19)
    expiracion: str = Field(..., pattern=r'^(0[1-9]|1[0-2])\/\d{2}$')
    cvv: str = Field(..., min_length=3, max_length=4)


class PagoRequest(BaseModel):
    reserva_id: int
    monto: float = Field(..., gt=0)
    metodo_pago: str
    datos_tarjeta: Optional[DatosTarjeta] = None
    
    @validator('metodo_pago')
    def validate_metodo_pago(cls, v):
        metodos_validos = ["tarjeta_credito", "tarjeta_debito", "monedero_electronico"]
        if v not in metodos_validos:
            raise ValueError(f"Método debe ser: {', '.join(metodos_validos)}")
        return v


class PagoResponse(BaseModel):
    pago_id: int
    reserva_id: int
    monto: float
    metodo_pago: str
    estado: str
    fecha_pago: datetime
    transaccion_id: str
    reserva_confirmada: bool