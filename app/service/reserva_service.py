from app.domain.reserva_domain import Reserva, EstadoReserva
from app.repository.reserva_repository import ReservaRepository
from app.repository.vehiculo_repository import VehiculoRepository
from datetime import datetime, date, time, timedelta
from app.core.constants import ErrorCodes

MAX_RESERVAS_ACTIVAS = 3

class ReservaService:
    def __init__(self, reserva_repo: ReservaRepository = None):
        if reserva_repo is None:
            from app.repository.reserva_repository import reserva_repo as global_reserva_repo
            self.reserva_repo = global_reserva_repo
        else:
            self.reserva_repo = reserva_repo
        self.vehiculo_repo = VehiculoRepository()
    
    def validar_disponibilidad(self, vehiculo_id: int, fecha: date, hora_inicio: time, hora_fin: time) -> dict:
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
                "horarios_alternativos": []
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
        
    # ========== HU-011: CANCELAR RESERVA ==========
    def cancelar_reserva(self, usuario_id: int, reserva_id: int) -> dict:
        """Cancela una reserva existente"""
        from datetime import datetime
        
        # Buscar la reserva
        reserva = self.reserva_repo.get_by_id(reserva_id)
        if not reserva:
            raise ValueError("RESERVATION_NOT_FOUND")
        
        # Verificar que la reserva pertenezca al usuario
        if reserva.usuario_id != usuario_id:
            raise ValueError("NOT_RESERVATION_OWNER")
        
        # Verificar que la reserva esté activa
        if reserva.estado not in [EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA]:
            raise ValueError("INVALID_RESERVATION_STATUS")
        
        # Calcular anticipación en horas
        hora_inicio_dt = datetime.combine(reserva.fecha, reserva.hora_inicio)
        ahora = datetime.now()
        
        if hora_inicio_dt <= ahora:
            raise ValueError("RESERVATION_ALREADY_STARTED")
        
        anticipacion_horas = (hora_inicio_dt - ahora).total_seconds() / 3600
        
        # Calcular penalización
        penalizacion = False
        monto_penalizacion = 0.0
        reembolso = reserva.costo_estimado
        
        if anticipacion_horas < 2:
            penalizacion = True
            monto_penalizacion = round(reserva.costo_estimado * 0.20, 2)
            reembolso = round(reserva.costo_estimado - monto_penalizacion, 2)
        
        # Cambiar estado a cancelada
        reserva.estado = EstadoReserva.CANCELADA
        reserva.fecha_cancelacion = ahora
        reserva.penalizacion_aplicada = penalizacion
        reserva.penalizacion_monto = monto_penalizacion
        reserva.reembolso_procesado = reembolso
        
        # Guardar cambios
        self.reserva_repo.update(reserva_id, reserva)
        
        # Determinar mensaje
        if penalizacion:
            mensaje = f"Reserva cancelada con penalización del 20%"
        else:
            mensaje = "Reserva cancelada exitosamente"
        
        return {
            "reserva_id": reserva.id,
            "estado_anterior": "confirmada" if reserva.estado == EstadoReserva.CANCELADA else "pendiente",
            "estado_nuevo": reserva.estado.value,
            "fecha_cancelacion": reserva.fecha_cancelacion.isoformat(),
            "anticipacion_horas": round(anticipacion_horas, 2),
            "penalizacion_aplicada": penalizacion,
            "penalizacion_monto": monto_penalizacion,
            "reembolso_procesado": reembolso,
            "mensaje": mensaje
        }