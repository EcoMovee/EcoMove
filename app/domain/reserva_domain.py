from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time
from enum import Enum

class EstadoReserva(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    EN_CURSO = "en_curso"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"

class Reserva(BaseModel):
    id: Optional[int] = None
    usuario_id: int
    vehiculo_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    duracion_horas: float
    costo_estimado: float
    estado: EstadoReserva = EstadoReserva.PENDIENTE
    fecha_creacion: datetime = Field(default_factory=datetime.now)