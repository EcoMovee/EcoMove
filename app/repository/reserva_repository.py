from typing import List, Optional
from domain.reserva_domain import Reserva, EstadoReserva
from datetime import date, time

class ReservaRepository:
    def __init__(self):
        self._reservas: List[Reserva] = []
        self._counter = 1
    
    def create(self, reserva: Reserva) -> Reserva:
        reserva.id = self._counter
        self._counter += 1
        self._reservas.append(reserva)
        return reserva
    
    def get_by_id(self, id: int) -> Optional[Reserva]:
        for reserva in self._reservas:
            if reserva.id == id:
                return reserva
        return None
    
    def get_activas_by_vehiculo(self, vehiculo_id: int, fecha: date, hora_inicio: time, hora_fin: time) -> List[Reserva]:
        """Obtiene reservas activas que se superponen con el horario solicitado"""
        activas = []
        for reserva in self._reservas:
            if reserva.vehiculo_id == vehiculo_id and reserva.fecha == fecha:
                # Solo reservas activas (no canceladas ni finalizadas)
                if reserva.estado in [EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA, EstadoReserva.EN_CURSO]:
                    # Verificar superposición de horarios
                    if not (hora_fin <= reserva.hora_inicio or hora_inicio >= reserva.hora_fin):
                        activas.append(reserva)
        return activas