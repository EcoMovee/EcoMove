from datetime import datetime, date, time
from typing import Dict, Optional, List


class ReservaRepository:
    
    def __init__(self):
        self._db: Dict[int, dict] = {}
        self._next_id: int = 1

    def create(self, reserva) -> dict:
        """Crear una nueva reserva"""
        from app.domain.reserva_domain import Reserva, EstadoReserva
        
        reserva_dict = {
            "id": self._next_id,
            "usuario_id": reserva.usuario_id,
            "vehiculo_id": reserva.vehiculo_id,
            "fecha": reserva.fecha,
            "hora_inicio": reserva.hora_inicio,
            "hora_fin": reserva.hora_fin,
            "duracion_horas": reserva.duracion_horas,
            "costo_estimado": reserva.costo_estimado,
            "estado": reserva.estado,
            "fecha_creacion": reserva.fecha_creacion
        }
        self._db[self._next_id] = reserva_dict
        self._next_id += 1
        
        return Reserva(**reserva_dict)

    def get_by_id(self, reserva_id: int):
        """Obtener reserva por ID"""
        from app.domain.reserva_domain import Reserva
        
        reserva_dict = self._db.get(reserva_id)
        if reserva_dict:
            return Reserva(**reserva_dict)
        return None

    def update_estado(self, reserva_id: int, nuevo_estado: str):
        """Actualizar el estado de una reserva"""
        from app.domain.reserva_domain import Reserva
        
        reserva_dict = self._db.get(reserva_id)
        if reserva_dict:
            reserva_dict["estado"] = nuevo_estado
            return Reserva(**reserva_dict)
        return None

    def update(self, reserva_id: int, reserva):
        """Actualizar una reserva completa"""
        self._db[reserva_id] = {
            "id": reserva.id,
            "usuario_id": reserva.usuario_id,
            "vehiculo_id": reserva.vehiculo_id,
            "fecha": reserva.fecha,
            "hora_inicio": reserva.hora_inicio,
            "hora_fin": reserva.hora_fin,
            "duracion_horas": reserva.duracion_horas,
            "costo_estimado": reserva.costo_estimado,
            "estado": reserva.estado,
            "fecha_creacion": reserva.fecha_creacion,
            "fecha_cancelacion": getattr(reserva, 'fecha_cancelacion', None),
            "penalizacion_aplicada": getattr(reserva, 'penalizacion_aplicada', False),
            "penalizacion_monto": getattr(reserva, 'penalizacion_monto', 0),
            "reembolso_procesado": getattr(reserva, 'reembolso_procesado', 0)
        }
        return reserva

    def get_activas_by_vehiculo(self, vehiculo_id: int, fecha: date, 
                                 hora_inicio: time, hora_fin: time) -> List[dict]:
        """Obtener reservas activas para un vehículo en un horario"""
        from app.domain.reserva_domain import EstadoReserva
        
        activas = []
        for reserva in self._db.values():
            if (reserva["vehiculo_id"] == vehiculo_id and 
                reserva["fecha"] == fecha and
                reserva["estado"] in [EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA]):
                if not (hora_fin <= reserva["hora_inicio"] or hora_inicio >= reserva["hora_fin"]):
                    activas.append(reserva)
        return activas

    def get_activas_by_usuario(self, usuario_id: int) -> List[dict]:
        """Obtener reservas activas de un usuario"""
        from app.domain.reserva_domain import EstadoReserva
        
        activas = []
        for reserva in self._db.values():
            if (reserva["usuario_id"] == usuario_id and 
                reserva["estado"] in [EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA]):
                activas.append(reserva)
        return activas


# Instancia global ÚNICA
reserva_repo = ReservaRepository()