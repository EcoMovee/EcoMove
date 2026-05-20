from typing import Optional, List, Dict
from app.domain.vehiculo_domain import Vehiculo, VehiculoCreate, EstadoVehiculo
from app.core.constants import VehicleStatus, VehicleConfig
from datetime import datetime

class VehiculoRepository:
    
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
    
    def create(self, data: VehiculoCreate) -> Optional[Vehiculo]:
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
            nivel_bateria=VehicleConfig.NIVEL_BATERIA_DEFAULT
        )
        self._db[self._next_id] = vehiculo
        self._next_id += 1
        return vehiculo
    
    def delete(self, vehiculo_id: int) -> bool:
        if vehiculo_id in self._db:
            del self._db[vehiculo_id]
            return True
        return False
    
    def update_estado(self, vehiculo_id: int, nuevo_estado: EstadoVehiculo) -> Optional[Vehiculo]:
        vehiculo = self.get_by_id(vehiculo_id)
        if vehiculo:
            updated = Vehiculo(
                id=vehiculo.id,
                tipo=vehiculo.tipo,
                modelo=vehiculo.modelo,
                ubicacion=vehiculo.ubicacion,
                tarifaPorHora=vehiculo.tarifaPorHora,
                estado=nuevo_estado,
                fecha_registro=vehiculo.fecha_registro,
                nivel_bateria=vehiculo.nivel_bateria
            )
            self._db[vehiculo_id] = updated
            return updated
        return None