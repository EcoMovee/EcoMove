from domain.reserva_domain import Reserva, EstadoReserva
from repository.reserva_repository import ReservaRepository
from repository.vehiculo_repository import VehiculoRepository
from datetime import datetime, date, time, timedelta
from core.constants import ErrorCodes

MAX_RESERVAS_ACTIVAS = 3

class ReservaService:
    def __init__(self):
        self.reserva_repo = ReservaRepository()
        self.vehiculo_repo = VehiculoRepository()
    
    def validar_disponibilidad(self, vehiculo_id: int, fecha: date, hora_inicio: time, hora_fin: time) -> dict:
        # ... (código existente de HU-009)
        vehiculo = self.vehiculo_repo.get_vehiculo_by_id(vehiculo_id)
        if not vehiculo:
            raise ValueError(ErrorCodes.VEHICLE_NOT_FOUND)
        
        if vehiculo.estado == "mantenimiento":
            raise ValueError("VEHICLE_IN_MAINTENANCE")
        
        if vehiculo.estado != "disponible":
            raise ValueError(ErrorCodes.VEHICLE_NOT_AVAILABLE)
        
        # Validar fecha (no anterior a hoy)
        if fecha < datetime.now().date():
            raise ValueError("PAST_DATE")
        
        # Validar hora_inicio < hora_fin
        if hora_inicio >= hora_fin:
            raise ValueError("INVALID_HOURS")
        
        # Validar duración mínima 30 minutos
        hora_inicio_dt = datetime.combine(fecha, hora_inicio)
        hora_fin_dt = datetime.combine(fecha, hora_fin)
        duracion_minutos = (hora_fin_dt - hora_inicio_dt).total_seconds() / 60
        
        if duracion_minutos < 30:
            raise ValueError("MIN_DURATION")
        
        reservas_activas = self.reserva_repo.get_activas_by_vehiculo(vehiculo_id, fecha, hora_inicio, hora_fin)
        
        if reservas_activas:
            return {
                "disponible": False,
                "vehiculo_id": vehiculo_id,
                "fecha": fecha.isoformat(),
                "hora_inicio": hora_inicio.strftime("%H:%M"),
                "hora_fin": hora_fin.strftime("%H:%M"),
                "horarios_alternativos": []  # Por simplificar
            }
        
        return {
            "disponible": True,
            "vehiculo_id": vehiculo_id,
            "fecha": fecha.isoformat(),
            "hora_inicio": hora_inicio.strftime("%H:%M"),
            "hora_fin": hora_fin.strftime("%H:%M")
        }
    
    # ========== HU-010: CREAR RESERVA ==========
    def crear_reserva(self, usuario_id: int, vehiculo_id: int, fecha: date, 
                      hora_inicio: time, hora_fin: time) -> dict:
        """Crea una nueva reserva"""
        
        # 1. Verificar reservas activas del usuario (límite 3)
        reservas_activas = self.reserva_repo.get_activas_by_usuario(usuario_id)
        if len(reservas_activas) >= MAX_RESERVAS_ACTIVAS:
            raise ValueError(ErrorCodes.MAX_ACTIVE_RESERVATIONS)
        
        # 2. Validar disponibilidad del vehículo
        disponibilidad = self.validar_disponibilidad(vehiculo_id, fecha, hora_inicio, hora_fin)
        if not disponibilidad.get("disponible"):
            raise ValueError("VEHICLE_UNAVAILABLE")
        
        # 3. Obtener vehículo para calcular costo
        vehiculo = self.vehiculo_repo.get_vehiculo_by_id(vehiculo_id)
        if not vehiculo:
            raise ValueError(ErrorCodes.VEHICLE_NOT_FOUND)
        
        if vehiculo.estado == "mantenimiento":
            raise ValueError("VEHICLE_IN_MAINTENANCE")
        
        # 4. Calcular duración y costo
        hora_inicio_dt = datetime.combine(fecha, hora_inicio)
        hora_fin_dt = datetime.combine(fecha, hora_fin)
        duracion_horas = round((hora_fin_dt - hora_inicio_dt).total_seconds() / 3600, 2)
        costo_estimado = round(duracion_horas * vehiculo.tarifaPorHora, 2)
        
        # 5. Crear reserva
        reserva = Reserva(
            usuario_id=usuario_id,
            vehiculo_id=vehiculo_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion_horas=duracion_horas,
            costo_estimado=costo_estimado,
            estado=EstadoReserva.PENDIENTE
        )
        
        reserva_creada = self.reserva_repo.create(reserva)
        
        return {
            "id": reserva_creada.id,
            "usuario_id": reserva_creada.usuario_id,
            "vehiculo_id": reserva_creada.vehiculo_id,
            "vehiculo": {
                "id": vehiculo.id,
                "tipo": vehiculo.tipo,
                "modelo": vehiculo.modelo,
                "tarifaPorHora": vehiculo.tarifaPorHora
            },
            "fecha": fecha.isoformat(),
            "hora_inicio": hora_inicio.strftime("%H:%M"),
            "hora_fin": hora_fin.strftime("%H:%M"),
            "duracion_horas": duracion_horas,
            "costo_estimado": costo_estimado,
            "estado": reserva_creada.estado.value,
            "fecha_creacion": reserva_creada.fecha_creacion.isoformat()
        }