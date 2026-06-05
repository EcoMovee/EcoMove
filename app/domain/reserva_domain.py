from pydantic import BaseModel, Field, validator
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
    duracion_horas: float = Field(..., gt=0)
    costo_estimado: float = Field(..., gt=0)
    estado: EstadoReserva = EstadoReserva.PENDIENTE
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_cancelacion: Optional[datetime] = None
    penalizacion_aplicada: bool = False
    penalizacion_monto: float = 0.0
    reembolso_procesado: float = 0.0
    # NUEVOS CAMPOS PARA HU-020
    fecha_inicio_viaje: Optional[datetime] = None
    fecha_fin_viaje: Optional[datetime] = None
    
    @validator('hora_fin')
    def validar_horario(cls, v, values):
        if 'hora_inicio' in values:
            if v <= values['hora_inicio']:
                raise ValueError("La hora de fin debe ser mayor a la hora de inicio")
        return v