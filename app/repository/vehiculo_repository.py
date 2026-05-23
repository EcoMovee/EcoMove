from typing import List, Optional, Dict
from app.database.database import (
    get_all_vehiculos,
    get_vehiculo_by_id,
    get_vehiculo_by_modelo,
    create_vehiculo,
    delete_vehiculo,
    update_vehiculo_estado
)
from app.domain.vehiculo_domain import Vehiculo, VehiculoCreate, EstadoVehiculo


class VehiculoRepository:
    """Repositorio para vehículos usando SQLite"""
    
    def get_all(self) -> List[Vehiculo]:
        """Devuelve todos los vehículos"""
        rows = get_all_vehiculos()
        return [self._row_to_vehiculo(row) for row in rows]
    
    def get_by_id(self, vehiculo_id: int) -> Optional[Vehiculo]:
        """Busca vehículo por ID"""
        row = get_vehiculo_by_id(vehiculo_id)
        return self._row_to_vehiculo(row) if row else None
    
    def get_by_modelo(self, modelo: str) -> Optional[Vehiculo]:
        """Busca vehículo por modelo"""
        row = get_vehiculo_by_modelo(modelo)
        return self._row_to_vehiculo(row) if row else None
    
    def create(self, data: VehiculoCreate) -> Optional[Vehiculo]:
        """Crea un nuevo vehículo"""
        # Verificar si ya existe
        existing = self.get_by_modelo(data.modelo)
        if existing:
            return None
        
        # Crear vehículo
        row = create_vehiculo(
            tipo=data.tipo,
            modelo=data.modelo,
            ubicacion=data.ubicacion,
            tarifaPorHora=data.tarifaPorHora
        )
        return self._row_to_vehiculo(row) if row else None
    
    def delete(self, vehiculo_id: int) -> bool:
        """Elimina un vehículo por ID"""
        return delete_vehiculo(vehiculo_id)
    
    def update_estado(self, vehiculo_id: int, nuevo_estado: EstadoVehiculo) -> Optional[Vehiculo]:
        """Actualiza el estado de un vehículo"""
        updated = update_vehiculo_estado(vehiculo_id, nuevo_estado)
        if updated:
            return self.get_by_id(vehiculo_id)
        return None
    
    def _row_to_vehiculo(self, row: dict) -> Vehiculo:
        """Convierte una fila de la BD en un objeto Vehiculo"""
        from app.domain.vehiculo_domain import Vehiculo, EstadoVehiculo, TipoVehiculo
        
        return Vehiculo(
            id=row['id'],
            tipo=row['tipo'],
            modelo=row['modelo'],
            ubicacion=row['ubicacion'],
            tarifaPorHora=float(row['tarifaPorHora']),
            estado=row['estado'],
            fecha_registro=row['fecha_registro'],
            nivel_bateria=row['nivel_bateria']
        )