from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from datetime import datetime

# ── Enums para valores permitidos ──
class TipoVehiculo(str, Enum):
    CARRO = "carro"
    MOTO = "moto"
    BICICLETA = "bicicleta"


class EstadoVehiculo(str, Enum):
    DISPONIBLE = "disponible"
    EN_USO = "en_uso"
    MANTENIMIENTO = "mantenimiento"


# ── Modelo base ──
class VehiculoBase(BaseModel):
    tipo: TipoVehiculo
    modelo: str = Field(..., min_length=3, max_length=100)
    ubicacion: str = Field(..., min_length=3, max_length=255)
    tarifaPorHora: float = Field(..., gt=0, description="Debe ser mayor a 0")
    
    @validator('modelo')
    def validate_modelo(cls, v):
        if not v or not v.strip():
            raise ValueError('El modelo es obligatorio')
        return v.strip()
    
    @validator('ubicacion')
    def validate_ubicacion(cls, v):
        if not v or not v.strip():
            raise ValueError('La ubicación es obligatoria')
        return v.strip()


# ── Para CREAR vehículo (request) ──
class VehiculoCreate(VehiculoBase):
    pass


# ── Respuesta completa (response) ──
class Vehiculo(VehiculoBase):
    id: int
    estado: EstadoVehiculo
    fecha_registro: Optional[datetime] = None
    nivel_bateria: Optional[int] = 100

    class Config:
        from_attributes = True