from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional
from app.service.reserva_service import ReservaService
from app.core.dependencies import get_current_user
from app.core.constants import HttpStatus, ErrorCodes
from app.repository.usuario_repository import UsuarioRepository
from app.repository.reserva_repository import reserva_repo
from app.service.reserva_service import ReservaService

router = APIRouter(prefix="/reservas", tags=["Reservas"])
service = ReservaService()
usuario_repo = UsuarioRepository()
service = ReservaService(reserva_repo)

# ========== HU-009: VALIDAR DISPONIBILIDAD ==========
@router.get("/disponibilidad")
async def validar_disponibilidad(
    vehiculo_id: int = Query(...),
    fecha: str = Query(...),
    hora_inicio: str = Query(...),
    hora_fin: str = Query(...),
    current_user_id: int = Depends(get_current_user)
):
    # ... (código existente de HU-009)
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_inicio_obj = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_fin_obj = datetime.strptime(hora_fin, "%H:%M").time()
        
        resultado = service.validar_disponibilidad(
            vehiculo_id=vehiculo_id,
            fecha=fecha_obj,
            hora_inicio=hora_inicio_obj,
            hora_fin=hora_fin_obj
        )
        
        if resultado.get("disponible"):
            return {
                "success": True,
                "statusCode": HttpStatus.OK,
                "message": "Vehículo disponible",
                "data": resultado
            }
        else:
            return JSONResponse(
                status_code=HttpStatus.CONFLICT,
                content={
                    "success": False,
                    "statusCode": HttpStatus.CONFLICT,
                    "message": "Vehículo no disponible en el horario solicitado",
                    "data": resultado
                }
            )
    except ValueError as e:
        error_msg = str(e)
        if error_msg == ErrorCodes.VEHICLE_NOT_FOUND:
            return JSONResponse(
                status_code=HttpStatus.NOT_FOUND,
                content={
                    "success": False,
                    "statusCode": HttpStatus.NOT_FOUND,
                    "message": "Vehículo no encontrado",
                    "error": {"code": "VEHICLE_NOT_FOUND"}
                }
            )
        if error_msg == "PAST_DATE":
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Fecha inválida",
                    "error": {"code": "INVALID_DATA", "details": "No se puede reservar en una fecha anterior a la actual"}
                }
            )
        if error_msg == "INVALID_HOURS":
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Horario inválido",
                    "error": {"code": "INVALID_DATA", "details": "La hora de inicio debe ser menor que la hora de fin"}
                }
            )
        if error_msg == "MIN_DURATION":
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Duración inválida",
                    "error": {"code": "INVALID_DATA", "details": "La duración mínima de reserva es de 30 minutos"}
                }
            )
        if error_msg == "VEHICLE_IN_MAINTENANCE":
            return JSONResponse(
                status_code=HttpStatus.CONFLICT,
                content={
                    "success": False,
                    "statusCode": HttpStatus.CONFLICT,
                    "message": "Vehículo en mantenimiento",
                    "error": {"code": "VEHICLE_IN_MAINTENANCE"}
                }
            )
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Error al validar disponibilidad",
                "error": {"code": ErrorCodes.INVALID_DATA, "details": error_msg}
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=HttpStatus.INTERNAL_ERROR,
            content={
                "success": False,
                "statusCode": HttpStatus.INTERNAL_ERROR,
                "message": "Error interno del servidor",
                "error": {"code": "INTERNAL_ERROR", "details": str(e)}
            }
        )


# ========== HU-010: CREAR RESERVA ==========
class CrearReservaRequest(BaseModel):
    vehiculo_id: int
    fecha: str
    hora_inicio: str
    hora_fin: str

@router.post("", status_code=201)
async def crear_reserva(
    request: CrearReservaRequest,
    current_user_id: int = Depends(get_current_user)
):
    try:
        # Verificar que el usuario está activo
        usuario = usuario_repo.get_by_id(current_user_id)
        if not usuario or not usuario.estado:
            return JSONResponse(
                status_code=HttpStatus.UNAUTHORIZED,
                content={
                    "success": False,
                    "statusCode": HttpStatus.UNAUTHORIZED,
                    "message": "Usuario desactivado",
                    "error": {"code": "USER_INACTIVE"}
                }
            )
        
        fecha_obj = datetime.strptime(request.fecha, "%Y-%m-%d").date()
        hora_inicio_obj = datetime.strptime(request.hora_inicio, "%H:%M").time()
        hora_fin_obj = datetime.strptime(request.hora_fin, "%H:%M").time()
        
        resultado = service.crear_reserva(
            usuario_id=current_user_id,
            vehiculo_id=request.vehiculo_id,
            fecha=fecha_obj,
            hora_inicio=hora_inicio_obj,
            hora_fin=hora_fin_obj
        )
        
        return {
            "success": True,
            "statusCode": HttpStatus.CREATED,
            "message": "Reserva creada exitosamente",
            "data": resultado
        }
    
    except ValueError as e:
        error_msg = str(e)
        
        if error_msg == ErrorCodes.VEHICLE_NOT_FOUND:
            return JSONResponse(
                status_code=HttpStatus.NOT_FOUND,
                content={
                    "success": False,
                    "statusCode": HttpStatus.NOT_FOUND,
                    "message": "Vehículo no encontrado",
                    "error": {"code": "VEHICLE_NOT_FOUND"}
                }
            )
        
        if error_msg == ErrorCodes.MAX_ACTIVE_RESERVATIONS:
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Límite de reservas activas alcanzado",
                    "error": {
                        "code": "MAX_ACTIVE_RESERVATIONS",
                        "details": "Has alcanzado el límite de 3 reservas activas. Cancela una reserva existente para continuar"
                    }
                }
            )
        
        if error_msg == "VEHICLE_UNAVAILABLE":
            return JSONResponse(
                status_code=HttpStatus.CONFLICT,
                content={
                    "success": False,
                    "statusCode": HttpStatus.CONFLICT,
                    "message": "Vehículo no disponible en el horario solicitado",
                    "error": {
                        "code": "VEHICLE_UNAVAILABLE",
                        "details": "El vehículo ya tiene una reserva en ese horario"
                    }
                }
            )
        
        if error_msg == "VEHICLE_IN_MAINTENANCE":
            return JSONResponse(
                status_code=HttpStatus.CONFLICT,
                content={
                    "success": False,
                    "statusCode": HttpStatus.CONFLICT,
                    "message": "Vehículo en mantenimiento",
                    "error": {
                        "code": "VEHICLE_IN_MAINTENANCE",
                        "details": "El vehículo seleccionado se encuentra en mantenimiento"
                    }
                }
            )
        
        if error_msg in ["PAST_DATE", "INVALID_HOURS", "MIN_DURATION"]:
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Datos inválidos",
                    "error": {"code": "INVALID_DATA", "details": error_msg}
                }
            )
        
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Error al crear reserva",
                "error": {"code": ErrorCodes.INVALID_DATA, "details": error_msg}
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=HttpStatus.INTERNAL_ERROR,
            content={
                "success": False,
                "statusCode": HttpStatus.INTERNAL_ERROR,
                "message": "Error interno del servidor",
                "error": {"code": "INTERNAL_ERROR", "details": str(e)}
            }
        )
        
# ========== HU-011: CANCELAR RESERVA ==========
@router.post("/{reserva_id}/cancelar")
async def cancelar_reserva(
    reserva_id: int,
    current_user_id: int = Depends(get_current_user)
):
    try:
        resultado = service.cancelar_reserva(
            usuario_id=current_user_id,
            reserva_id=reserva_id
        )
        
        return {
            "success": True,
            "statusCode": HttpStatus.OK,
            "message": resultado.pop("mensaje"),
            "data": resultado
        }
    
    except ValueError as e:
        error_msg = str(e)
        
        if error_msg == "RESERVATION_NOT_FOUND":
            return JSONResponse(
                status_code=HttpStatus.NOT_FOUND,
                content={
                    "success": False,
                    "statusCode": HttpStatus.NOT_FOUND,
                    "message": "Reserva no encontrada",
                    "error": {
                        "code": "RESERVATION_NOT_FOUND",
                        "details": "No existe una reserva con el ID proporcionado"
                    }
                }
            )
        
        if error_msg == "NOT_RESERVATION_OWNER":
            return JSONResponse(
                status_code=HttpStatus.FORBIDDEN,
                content={
                    "success": False,
                    "statusCode": HttpStatus.FORBIDDEN,
                    "message": "No autorizado",
                    "error": {
                        "code": "FORBIDDEN",
                        "details": "No tienes permiso para cancelar esta reserva"
                    }
                }
            )
        
        if error_msg == "INVALID_RESERVATION_STATUS":
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "No se puede cancelar la reserva",
                    "error": {
                        "code": "INVALID_RESERVATION_STATUS",
                        "details": "La reserva ya está finalizada o cancelada y no puede cancelarse nuevamente"
                    }
                }
            )
        
        if error_msg == "RESERVATION_ALREADY_STARTED":
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "No se puede cancelar la reserva",
                    "error": {
                        "code": "RESERVATION_ALREADY_STARTED",
                        "details": "La reserva ya ha comenzado o está en curso"
                    }
                }
            )
        
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Error al cancelar reserva",
                "error": {"code": "INVALID_DATA", "details": error_msg}
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=HttpStatus.INTERNAL_ERROR,
            content={
                "success": False,
                "statusCode": HttpStatus.INTERNAL_ERROR,
                "message": "Error interno del servidor",
                "error": {"code": "INTERNAL_ERROR", "details": str(e)}
            }
        )