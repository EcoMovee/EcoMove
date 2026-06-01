from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.domain.vehiculo_domain import Vehiculo, VehiculoCreate


class VehiculoRepository:
    
    def __init__(self):
        self._db: Dict[int, Vehiculo] = {}
        self._next_id: int = 1

    def get_by_modelo(self, modelo: str) -> Optional[Vehiculo]:
        """Buscar vehículo por modelo (único)"""
        for vehiculo in self._db.values():
            if vehiculo.modelo.lower() == modelo.lower():
                return vehiculo
        return None

    def create(self, data: VehiculoCreate) -> Vehiculo:
        """Crear un nuevo vehículo"""
        vehiculo = Vehiculo(
            id=self._next_id,
            tipo=data.tipo,
            modelo=data.modelo,
            ubicacion=data.ubicacion,
            tarifaPorHora=data.tarifaPorHora,
            estado="disponible",
            fecha_registro=datetime.now(),
            nivel_bateria=100
        )
        self._db[self._next_id] = vehiculo
        self._next_id += 1
        return vehiculo