from pydantic import BaseModel
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

# ── Modelo base: campos comunes ──
class VehiculoBase(BaseModel):
    tipo: TipoVehiculo
    modelo: str
    ubicacion: str
    tarifaPorHora: float

# ── Para CREAR un vehículo ──
class VehiculoCreate(VehiculoBase):
    pass

# ── Respuesta completa ──
class Vehiculo(VehiculoBase):
    id: int
    estado: EstadoVehiculo
    fecha_registro: Optional[datetime] = None
    nivel_bateria: Optional[int] = 100

    class Config:
        from_attributes = True