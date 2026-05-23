from pydantic import BaseModel, Field, validator
from app.core.constants import VehicleTypes, VehicleConfig, ErrorMessages

class VehiculoBase(BaseModel):
    tipo: str
    modelo: str = Field(..., min_length=VehicleConfig.MODELO_MIN_LENGTH)
    ubicacion: str = Field(..., min_length=VehicleConfig.UBICACION_MIN_LENGTH)
    tarifaPorHora: float = Field(..., gt=VehicleConfig.TARIFA_MINIMA)
    
    @validator('tipo')
    def validate_tipo(cls, v):
        if v not in VehicleTypes.ALLOWED:
            raise ValueError(ErrorMessages.INVALID_VEHICLE_TYPE)
        return v
    
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