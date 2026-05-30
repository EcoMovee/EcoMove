from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime, date
import re
from enum import Enum

class EstadoUsuario(str, Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"

class Usuario(BaseModel):
    id: Optional[int] = None
    nombre: str = Field(..., min_length=2, max_length=100)
    correo: EmailStr
    telefono: str = Field(..., min_length=8, max_length=20)
    contrasena: Optional[str] = None  # Solo para entrada, no se guarda
    contrasena_hash: str
    rol: str = "usuario"
    estado: bool = True
    fecha_registro: datetime = Field(default_factory=datetime.now)
    intentos_fallidos: int = 0
    bloqueado_hasta: Optional[datetime] = None
    fecha_nacimiento: Optional[date] = None
    
    @validator('nombre')
    def validar_nombre(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        return v.strip()
    
    @validator('telefono')
    def validar_telefono(cls, v):
        if not re.match(r'^\+\d{1,3}\d{7,15}$', v):
            raise ValueError('El teléfono debe tener código de país y entre 7 y 15 dígitos')
        return v