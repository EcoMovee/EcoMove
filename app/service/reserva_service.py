from domain.reserva_domain import Reserva
from repository.reserva_repository import ReservaRepository
from repository.vehiculo_repository import VehiculoRepository
from datetime import datetime, date, time, timedelta
from core.constants import ErrorCodes

class ReservaService:
    def __init__(self):
        self.reserva_repo = ReservaRepository()
        self.vehiculo_repo = VehiculoRepository()
    
    def validar_disponibilidad(self, vehiculo_id: int, fecha: date, hora_inicio: time, hora_fin: time) -> dict:
        """Valida si un vehículo está disponible en el horario solicitado"""
        
        # 1. Verificar que el vehículo existe
        vehiculo = self.vehiculo_repo.get_vehiculo_by_id(vehiculo_id)
        if not vehiculo:
            raise ValueError(ErrorCodes.VEHICLE_NOT_FOUND)
        
        # 2. Verificar que la fecha no sea anterior a hoy
        if fecha < datetime.now().date():
            raise ValueError("FECHA_PASADA")
        
        # 3. Verificar que hora_inicio < hora_fin
        if hora_inicio >= hora_fin:
            raise ValueError("HORARIO_INVALIDO")
        
        # 4. Verificar duración mínima de 30 minutos
        hora_inicio_dt = datetime.combine(fecha, hora_inicio)
        hora_fin_dt = datetime.combine(fecha, hora_fin)
        duracion_minutos = (hora_fin_dt - hora_inicio_dt).total_seconds() / 60
        
        if duracion_minutos < 30:
            raise ValueError("DURACION_INSUFICIENTE")
        
        # 5. Verificar reservas superpuestas
        reservas_activas = self.reserva_repo.get_activas_by_vehiculo(
            vehiculo_id, fecha, hora_inicio, hora_fin
        )
        
        if reservas_activas:
            # Calcular horarios alternativos
            horarios_alternativos = self._calcular_horarios_alternativos(
                vehiculo_id, fecha, hora_inicio, hora_fin, reservas_activas
            )
            return {
                "disponible": False,
                "vehiculo_id": vehiculo_id,
                "fecha": fecha.isoformat(),
                "hora_inicio": hora_inicio.strftime("%H:%M"),
                "hora_fin": hora_fin.strftime("%H:%M"),
                "horarios_alternativos": horarios_alternativos
            }
        
        return {
            "disponible": True,
            "vehiculo_id": vehiculo_id,
            "fecha": fecha.isoformat(),
            "hora_inicio": hora_inicio.strftime("%H:%M"),
            "hora_fin": hora_fin.strftime("%H:%M")
        }
    
    def _calcular_horarios_alternativos(self, vehiculo_id: int, fecha: date, hora_inicio: time, hora_fin: time, reservas_activas: list) -> list:
        """Calcula los próximos 3 horarios disponibles después del horario solicitado"""
        alternativas = []
        
        # Convertir horas a minutos desde medianoche para facilitar cálculos
        inicio_minutos = hora_inicio.hour * 60 + hora_inicio.minute
        fin_minutos = hora_fin.hour * 60 + hora_fin.minute
        duracion = fin_minutos - inicio_minutos
        
        # Buscar la próxima hora disponible después de que termine la última reserva
        # Ordenar reservas por hora de inicio
        reservas_ordenadas = sorted(reservas_activas, key=lambda r: (r.hora_inicio.hour * 60 + r.hora_inicio.minute))
        
        # Última hora de fin de las reservas conflictivas
        ultima_hora_fin = max([(r.hora_fin.hour * 60 + r.hora_fin.minute) for r in reservas_activas])
        
        # Proponer horarios después de la última reserva
        for i in range(3):
            nueva_inicio = ultima_hora_fin + (i * 30)  # Espacio de 30 minutos entre alternativas
            nueva_fin = nueva_inicio + duracion
            
            # No pasar de las 23:00
            if nueva_fin > 23 * 60:
                break
            
            alternativas.append({
                "hora_inicio": f"{nueva_inicio // 60:02d}:{nueva_inicio % 60:02d}",
                "hora_fin": f"{nueva_fin // 60:02d}:{nueva_fin % 60:02d}"
            })
        
        return alternativas[:3]