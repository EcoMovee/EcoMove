from typing import Optional, Dict
from datetime import datetime
from app.domain.vehiculo_domain import Vehiculo, VehiculoCreate

class VehiculoRepository:
    _instance = None
    _db = None
    _next_id = None
    _historial = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._db = {}
            cls._instance._next_id = 1
            cls._instance._historial = []
        return cls._instance
    
    def __init__(self):
        pass

    def get_by_id(self, id: int) -> Optional[Vehiculo]:
        return self._db.get(id)

    def get_by_modelo(self, modelo: str) -> Optional[Vehiculo]:
        for vehiculo in self._db.values():
            if vehiculo.modelo.lower() == modelo.lower():
                return vehiculo
        return None

    def create(self, data: VehiculoCreate) -> Vehiculo:
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
    
    def get_disponibles(self, tipo: Optional[str] = None) -> list:
        disponibles = []
        for vehiculo in self._db.values():
            if vehiculo.estado == "disponible":
                if tipo is None or vehiculo.tipo == tipo:
                    disponibles.append(vehiculo)
        return disponibles

    def get_disponibles_con_ubicacion(self, tipo: Optional[str] = None) -> list:
        disponibles = []
        for vehiculo in self._db.values():
            if vehiculo.estado == "disponible":
                if hasattr(vehiculo, 'latitud') and hasattr(vehiculo, 'longitud'):
                    if vehiculo.latitud and vehiculo.longitud:
                        if tipo is None or vehiculo.tipo == tipo:
                            disponibles.append(vehiculo)
        return disponibles
    
    def get_vehiculo_by_id(self, vehiculo_id: int):
        return self._db.get(vehiculo_id)

    def update_estado(self, vehiculo_id: int, nuevo_estado: str):
        vehiculo = self._db.get(vehiculo_id)
        if vehiculo:
            estado_anterior = vehiculo.estado
            vehiculo.estado = nuevo_estado
            return vehiculo, estado_anterior
        return None, None

    def registrar_historial(self, vehiculo_id: int, estado_anterior: str, 
                            estado_nuevo: str, admin_id: int, reservas_afectadas: int = 0):
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
        return 0

    def get_historial(self, vehiculo_id: int = None):
        if vehiculo_id:
            return [h for h in self._historial if h["vehiculo_id"] == vehiculo_id]
        return self._historial
    
    def get_by_estado(self, estado: str) -> list:
        resultado = []
        for vehiculo in self._db.values():
            if vehiculo.estado == estado:
                resultado.append(vehiculo)
        return resultado

    def get_disponibles_excluyendo_mantenimiento(self, tipo: Optional[str] = None) -> list:
        disponibles = []
        for vehiculo in self._db.values():
            if vehiculo.estado == "disponible":
                if tipo is None or vehiculo.tipo == tipo:
                    disponibles.append(vehiculo)
        return disponibles