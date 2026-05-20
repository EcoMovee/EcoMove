from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from datetime import datetime
from app.core.constants import VehicleTypes, VehicleStatus, VehicleConfig, ErrorMessages

class TipoVehiculo(str, Enum):
    CARRO = VehicleTypes.CARRO
    MOTO = VehicleTypes.MOTO
    BICICLETA = VehicleTypes.BICICLETA

class EstadoVehiculo(str, Enum):
    DISPONIBLE = VehicleStatus.DISPONIBLE
    EN_USO = VehicleStatus.EN_USO
    MANTENIMIENTO = VehicleStatus.MANTENIMIENTO

class VehiculoBase(BaseModel):
    tipo: TipoVehiculo
    modelo: str = Field(..., min_length=VehicleConfig.MODELO_MIN_LENGTH)
    ubicacion: str = Field(..., min_length=VehicleConfig.UBICACION_MIN_LENGTH)
    tarifaPorHora: float = Field(..., gt=VehicleConfig.TARIFA_MINIMA)
    
    @validator('modelo')
    def validate_modelo(cls, v):
        if not v or not v.strip():
            raise ValueError(ErrorMessages.MODELO_REQUIRED)
        return v.strip()
    
    @validator('ubicacion')
    def validate_ubicacion(cls, v):
        if not v or not v.strip():
            raise ValueError(ErrorMessages.UBICACION_REQUIRED)
        return v.strip()

class VehiculoCreate(VehiculoBase):
    pass

class Vehiculo(VehiculoBase):
    id: int
    estado: EstadoVehiculo
    fecha_registro: Optional[datetime] = None
    nivel_bateria: Optional[int] = VehicleConfig.NIVEL_BATERIA_DEFAULT

    class Config:
        from_attributes = True