from typing import Optional, List, Dict
from domain.models import Vehiculo, VehiculoCreate, EstadoVehiculo
from datetime import datetime

class VehiculoRepository:
    """Simulamos una base de datos con un dict."""
    
    def __init__(self):
        self._db: Dict[int, Vehiculo] = {}
        self._next_id: int = 1
    
    def get_all(self) -> List[Vehiculo]:
        return list(self._db.values())
    
    def get_by_id(self, vehiculo_id: int) -> Optional[Vehiculo]:
        return self._db.get(vehiculo_id)
    
    def get_by_modelo(self, modelo: str) -> Optional[Vehiculo]:
        for vehiculo in self._db.values():
            if vehiculo.modelo.lower() == modelo.lower():
                return vehiculo
        return None
    
    def create(self, data: VehiculoCreate) -> Vehiculo:
        # Verificar si ya existe un vehículo con el mismo modelo
        existing = self.get_by_modelo(data.modelo)
        if existing:
            return None
        
        vehiculo = Vehiculo(
            id=self._next_id,
            tipo=data.tipo,
            modelo=data.modelo,
            ubicacion=data.ubicacion,
            tarifaPorHora=data.tarifaPorHora,
            estado=EstadoVehiculo.DISPONIBLE,
            fecha_registro=datetime.now(),
            nivel_bateria=100
        )
        self._db[self._next_id] = vehiculo
        self._next_id += 1
        return vehiculo
    
    def delete(self, vehiculo_id: int) -> bool:
        if vehiculo_id in self._db:
            del self._db[vehiculo_id]
            return True
        return False