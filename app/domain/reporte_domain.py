from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class FiltrosReporteReservas(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estados: Optional[List[str]] = None
    formato: str = "json"


class ReporteReservaItem(BaseModel):
    id: int
    usuario_nombre: str
    usuario_email: str
    vehiculo_tipo: str
    vehiculo_modelo: str
    fecha: str
    hora_inicio: str
    hora_fin: str
    duracion_horas: float
    costo_estimado: float
    estado: str
    fecha_creacion: str


class ReporteReservaResponse(BaseModel):
    success: bool
    statusCode: int
    message: str
    data: dict
    

class FiltrosReportePagos(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    metodo_pago: Optional[str] = None
    estado: Optional[str] = None
    formato: str = "json"
    
class FiltrosVehiculosTop(BaseModel):
    periodo: str  # dia, semana, mes, rango
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    formato: str = "json"


class VehiculoTopItem(BaseModel):
    posicion: int
    id: int
    tipo: str
    modelo: str
    ubicacion: str
    cantidad_reservas: int
    horas_totales_uso: float
    ingresos_generados: float


class VehiculosTopResponse(BaseModel):
    success: bool
    statusCode: int
    message: str
    data: dict