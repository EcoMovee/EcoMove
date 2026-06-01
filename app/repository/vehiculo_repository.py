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
    
    # ==================== HU-007: Actualización de estado ====================

    def get_vehiculo_by_id(self, vehiculo_id: int):
        """Obtener vehículo por ID"""
        return self._db.get(vehiculo_id)

    def update_estado(self, vehiculo_id: int, nuevo_estado: str):
        """Actualizar estado del vehículo"""
        vehiculo = self._db.get(vehiculo_id)
        if vehiculo:
            estado_anterior = vehiculo.estado
            vehiculo.estado = nuevo_estado
            return vehiculo, estado_anterior
        return None, None

    def registrar_historial(self, vehiculo_id: int, estado_anterior: str, 
                            estado_nuevo: str, admin_id: int, reservas_afectadas: int = 0):
        """Registrar cambio de estado en el historial (en memoria)"""
        if not hasattr(self, '_historial'):
            self._historial = []
        from datetime import datetime
        self._historial.append({
            "id": len(self._historial) + 1,
            "vehiculo_id": vehiculo_id,
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_nuevo,
            "administrador_id": admin_id,
            "fecha_cambio": datetime.now(),
            "reservas_afectadas": reservas_afectadas
        })
        return True

    def get_reservas_futuras_count(self, vehiculo_id: int) -> int:
        """Contar reservas futuras de un vehículo (simulado - sin BD)"""
        # Por ahora retorna 0 (implementar cuando exista el módulo de reservas)
        return 0

    def get_historial(self, vehiculo_id: int = None):
        """Obtener historial de cambios"""
        if not hasattr(self, '_historial'):
            return []
        if vehiculo_id:
            return [h for h in self._historial if h["vehiculo_id"] == vehiculo_id]
        return self._historial
    
    
    
    # ==================== HU-008: Bloqueo de vehículos en mantenimiento ====================

    def get_by_estado(self, estado: str) -> list:
        """Obtener vehículos por estado"""
        resultado = []
        for vehiculo in self._db.values():
            if vehiculo.estado == estado:
                resultado.append(vehiculo)
        return resultado

    def get_disponibles_excluyendo_mantenimiento(self, tipo: Optional[str] = None) -> list:
        """Obtener vehículos disponibles (excluye mantenimiento y en_uso)"""
        disponibles = []
        for vehiculo in self._db.values():
            if vehiculo.estado == "disponible":
                if tipo is None or vehiculo.tipo == tipo:
                    disponibles.append(vehiculo)
        return disponibles