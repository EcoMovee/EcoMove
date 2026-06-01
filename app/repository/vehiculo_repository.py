from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.domain.vehiculo_domain import Vehiculo, VehiculoCreate
from typing import Optional



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
    
    
    
    
    # ==================== HU-006: Métodos para consulta ====================

    def get_disponibles(self, tipo: Optional[str] = None) -> list:
        """Obtener vehículos con estado 'disponible' (excluye en_uso y mantenimiento)"""
        disponibles = []
        for vehiculo in self._db.values():
            if vehiculo.estado == "disponible":
                if tipo is None or vehiculo.tipo == tipo:
                    disponibles.append(vehiculo)
        return disponibles

    def get_disponibles_con_ubicacion(self, tipo: Optional[str] = None) -> list:
        """Obtener vehículos disponibles que tienen coordenadas"""
        disponibles = []
        for vehiculo in self._db.values():
            if vehiculo.estado == "disponible":
                if hasattr(vehiculo, 'latitud') and hasattr(vehiculo, 'longitud'):
                    if vehiculo.latitud and vehiculo.longitud:
                        if tipo is None or vehiculo.tipo == tipo:
                            disponibles.append(vehiculo)
        return disponibles