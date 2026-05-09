from pydantic import BaseModel
from typing import Optional

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str

class VehiculoBase(BaseModel):
    placa: str
    modelo: str
    año: int

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoResponse(VehiculoBase):
    id: int
    
    class Config:
        from_attributes = True