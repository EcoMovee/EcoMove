from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

class Usuario(BaseModel):
    id: Optional[int] = None
    nombre: str = Field(..., min_length=2, max_length=100)
    correo: str
    telefono: str = Field(..., min_length=8, max_length=20)
    contrasena_hash: str
    rol: str = "usuario"
    estado: bool = True
    fecha_registro: datetime = Field(default_factory=datetime.now)
    intentos_fallidos: int = 0
    bloqueado_hasta: Optional[datetime] = None
    fecha_nacimiento: Optional[date] = None