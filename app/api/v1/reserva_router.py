from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from datetime import datetime, date, time
from service.reserva_service import ReservaService
from core.dependencies import get_current_user
from core.constants import HttpStatus, ErrorCodes

router = APIRouter(prefix="/api/v1/reservas", tags=["Reservas"])
service = ReservaService()

@router.get("/disponibilidad")
async def validar_disponibilidad(
    vehiculo_id: int = Query(..., description="ID del vehículo"),
    fecha: str = Query(..., description="Fecha (YYYY-MM-DD)"),
    hora_inicio: str = Query(..., description="Hora de inicio (HH:MM)"),
    hora_fin: str = Query(..., description="Hora de fin (HH:MM)"),
    current_user_id: int = Depends(get_current_user)
):
    try:
        # Convertir parámetros
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
                    "error": {
                        "code": "VEHICLE_NOT_FOUND",
                        "details": f"El vehículo con ID {vehiculo_id} no existe"
                    }
                }
            )
        
        if error_msg == "FECHA_PASADA":
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Fecha inválida",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": "No se puede reservar en una fecha anterior a la actual"
                    }
                }
            )
        
        if error_msg == "HORARIO_INVALIDO":
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Horario inválido",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": "La hora de inicio debe ser menor que la hora de fin"
                    }
                }
            )
        
        if error_msg == "DURACION_INSUFICIENTE":
            return JSONResponse(
                status_code=HttpStatus.BAD_REQUEST,
                content={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Duración inválida",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": "La duración mínima de reserva es de 30 minutos"
                    }
                }
            )
        
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Error al validar disponibilidad",
                "error": {
                    "code": ErrorCodes.INVALID_DATA,
                    "details": error_msg
                }
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=HttpStatus.INTERNAL_ERROR,
            content={
                "success": False,
                "statusCode": HttpStatus.INTERNAL_ERROR,
                "message": "Error interno del servidor",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "details": str(e)
                }
            }
        )