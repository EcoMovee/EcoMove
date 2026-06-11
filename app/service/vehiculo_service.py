from domain.vehiculo_domain import Vehiculo, VehiculoCreate
from repository.vehiculo_repository import VehiculoRepository
from typing import Optional

class VehiculoService:
    
    def __init__(self, repo: VehiculoRepository):
        self.repo = repo

    def create(self, data: VehiculoCreate) -> Vehiculo:
        existing = self.repo.get_by_modelo(data.modelo)
        if existing:
            raise ValueError("VEHICLE_ALREADY_EXISTS")
        return self.repo.create(data)
    
    
    
    # ==================== HU-006: Consulta de vehículos disponibles ====================

    def calcular_distancia(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distancia usando fórmula de Haversine (km)"""
        import math
        R = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 2)

    def get_vehiculos_disponibles(self, tipo: Optional[str] = None,
                                   latitud: Optional[float] = None,
                                   longitud: Optional[float] = None,
                                   radio_km: Optional[float] = None):
        """Consulta vehículos disponibles con filtros"""
        from domain.vehiculo_domain import VehiculoDisponible
        
        filtros_aplicados = {
            "tipo": tipo if tipo else None,
            "latitud": latitud if latitud else None,
            "longitud": longitud if longitud else None,
            "radio_km": radio_km if radio_km else None
        }
        
        # Solo vehículos con estado "disponible"
        vehiculos_db = self.repo.get_disponibles(tipo)
        
        if radio_km is not None and radio_km <= 0:
            raise ValueError("INVALID_RADIUS")
        if tipo and tipo not in ["carro", "moto", "bicicleta"]:
            raise ValueError("INVALID_TYPE")
        
        if latitud is not None and longitud is not None and radio_km is not None:
            vehiculos_db = self.repo.get_disponibles_con_ubicacion(tipo)
            resultados = []
            for v in vehiculos_db:
                distancia = self.calcular_distancia(latitud, longitud, v.latitud, v.longitud)
                if distancia <= radio_km:
                    resultados.append({"vehiculo": v, "distancia": distancia})
            resultados.sort(key=lambda x: x["distancia"])
            vehiculos = [
                VehiculoDisponible(
                    id=r["vehiculo"].id,
                    tipo=r["vehiculo"].tipo,
                    modelo=r["vehiculo"].modelo,
                    ubicacion=r["vehiculo"].ubicacion,
                    tarifaPorHora=r["vehiculo"].tarifaPorHora,
                    distancia_km=r["distancia"],
                    nivel_bateria=r["vehiculo"].nivel_bateria
                )
                for r in resultados
            ]
        else:
            vehiculos_db = self.repo.get_disponibles(tipo)
            vehiculos = [
                VehiculoDisponible(
                    id=v.id,
                    tipo=v.tipo,
                    modelo=v.modelo,
                    ubicacion=v.ubicacion,
                    tarifaPorHora=v.tarifaPorHora,
                    distancia_km=None,
                    nivel_bateria=v.nivel_bateria
                )
                for v in vehiculos_db
            ]
        
        return vehiculos, filtros_aplicados
    
    
    
    # ==================== HU-007: Actualización de estado ====================

    def update_estado(self, vehiculo_id: int, nuevo_estado: str, 
                      admin_id: int, confirmar: bool = False):
        """Actualizar estado de un vehículo con validaciones"""
        
        # Transiciones permitidas
        transiciones_permitidas = {
            "disponible": ["en_uso", "mantenimiento"],
            "en_uso": ["disponible"],
            "mantenimiento": ["disponible"]
        }
        
        # Obtener vehículo
        vehiculo = self.repo.get_vehiculo_by_id(vehiculo_id)
        if not vehiculo:
            raise ValueError("VEHICLE_NOT_FOUND")
        
        estado_actual = vehiculo.estado
        
        # Validar transición
        if nuevo_estado not in transiciones_permitidas.get(estado_actual, []):
            raise ValueError(f"INVALID_TRANSITION:{estado_actual}:{nuevo_estado}")
        
        # Verificar reservas futuras si se cambia a mantenimiento
        reservas_afectadas = 0
        if nuevo_estado == "mantenimiento":
            reservas_afectadas = self.repo.get_reservas_futuras_count(vehiculo_id)
            if reservas_afectadas > 0 and not confirmar:
                raise ValueError(f"RESERVAS_FUTURAS:{reservas_afectadas}")
        
        # Actualizar estado
        vehiculo_actualizado, estado_anterior = self.repo.update_estado(vehiculo_id, nuevo_estado)
        
        # Registrar en historial
        self.repo.registrar_historial(vehiculo_id, estado_anterior, nuevo_estado, admin_id, reservas_afectadas)
        
        return vehiculo_actualizado, estado_anterior, reservas_afectadas

    def get_historial_cambios(self, vehiculo_id: int = None):
        """Obtener historial de cambios de estado"""
        return self.repo.get_historial(vehiculo_id)
    
    
    # ==================== HU-008: Bloqueo de vehículos en mantenimiento ====================

    def get_vehiculos_disponibles_excluyendo_mantenimiento(self, tipo: Optional[str] = None):
        """Obtener vehículos disponibles (excluye mantenimiento y en_uso)"""
        from domain.vehiculo_domain import VehiculoDisponible
        
        vehiculos_db = self.repo.get_disponibles_excluyendo_mantenimiento(tipo)
        return [
            VehiculoDisponible(
                id=v.id,
                tipo=v.tipo,
                modelo=v.modelo,
                ubicacion=v.ubicacion,
                tarifaPorHora=v.tarifaPorHora,
                distancia_km=None,
                nivel_bateria=v.nivel_bateria
            )
            for v in vehiculos_db
        ]

    def get_vehiculos_by_estado(self, estado: str, tipo: Optional[str] = None):
        """Obtener vehículos por estado (para administradores)"""
        from domain.vehiculo_domain import Vehiculo
        
        vehiculos_db = self.repo.get_by_estado(estado)
        if tipo:
            vehiculos_db = [v for v in vehiculos_db if v.tipo == tipo]
        
        return [
            Vehiculo(
                id=v.id,
                tipo=v.tipo,
                modelo=v.modelo,
                ubicacion=v.ubicacion,
                tarifaPorHora=v.tarifaPorHora,
                estado=v.estado,
                fecha_registro=v.fecha_registro,
                nivel_bateria=v.nivel_bateria
            )
            for v in vehiculos_db
        ]

    def verificar_disponibilidad_para_reserva(self, vehiculo_id: int) -> bool:
        """Verificar si un vehículo está disponible para reserva"""
        vehiculo = self.repo.get_vehiculo_by_id(vehiculo_id)
        if not vehiculo:
            return False
        return vehiculo.estado == "disponible"