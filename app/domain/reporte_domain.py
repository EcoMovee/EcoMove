from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class FiltrosReporteReservas(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estados: Optional[List[str]] = None
    usuario_id: Optional[int] = None
    vehiculo_id: Optional[int] = None
    formato: str = "json"


class FiltrosReportePagos(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    metodo_pago: Optional[str] = None
    estado: Optional[str] = None
    usuario_id: Optional[int] = None
    rango_monto_min: Optional[float] = None
    rango_monto_max: Optional[float] = None
    formato: str = "json"


class FiltrosVehiculosTop(BaseModel):
    periodo: str
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    tipo_vehiculo: Optional[str] = None
    ubicacion: Optional[str] = None
    limite: int = 10
    formato: str = "json"