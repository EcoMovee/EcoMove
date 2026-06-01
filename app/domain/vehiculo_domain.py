from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class VehiculoBase(BaseModel):
    tipo: str = Field(..., description="carro, moto o bicicleta")
    modelo: str = Field(..., min_length=3, max_length=100)
    ubicacion: str = Field(..., min_length=3, max_length=255)
    tarifaPorHora: float = Field(..., gt=0)
    
    @validator('tipo')
    def validate_tipo(cls, v):
        tipos_validos = ["carro", "moto", "bicicleta"]
        if v not in tipos_validos:
            raise ValueError(f"El tipo debe ser: {', '.join(tipos_validos)}")
        return v
    
    @validator('modelo')
    def validate_modelo(cls, v):
        if not v or not v.strip():
            raise ValueError("El modelo es obligatorio")
        return v.strip()
    
    @validator('ubicacion')
    def validate_ubicacion(cls, v):
        if not v or not v.strip():
            raise ValueError("La ubicación es obligatoria")
        return v.strip()


class VehiculoCreate(VehiculoBase):
    pass


class Vehiculo(VehiculoBase):
    id: int
    estado: str
    fecha_registro: Optional[datetime] = None
    nivel_bateria: int = 100

    class Config:
        from_attributes = True
        
        

# ==================== HU-006: Modelos para consulta de vehículos disponibles ====================

class FiltrosAplicados(BaseModel):
    tipo: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    radio_km: Optional[float] = None

class VehiculoDisponible(BaseModel):
    id: int
    tipo: str
    modelo: str
    ubicacion: str
    tarifaPorHora: float
    distancia_km: Optional[float] = None
    nivel_bateria: int