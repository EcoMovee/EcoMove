from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from core.dependencies import get_current_user
from core.constants import HttpStatus, ErrorCodes
from service.qr_service import QRService
from repository.qr_repository import qr_repo  # ← instancia global
from repository.reserva_repository import reserva_repo  # ← instancia global
from domain.qr_domain import QR, EstadoQR
from domain.reserva_domain import EstadoReserva

router = APIRouter(prefix="/api/v1/qrs", tags=["QR"])
qr_service = QRService()

class GenerarQRRequest(BaseModel):
    reserva_id: int

@router.post("", status_code=201)
async def generar_qr(
    request: GenerarQRRequest,
    current_user_id: int = Depends(get_current_user)
):
    # Buscar la reserva
    reserva = reserva_repo.get_by_id(request.reserva_id)
    
    if not reserva:
        return JSONResponse(
            status_code=HttpStatus.NOT_FOUND,
            content={
                "success": False,
                "statusCode": HttpStatus.NOT_FOUND,
                "message": "No se puede generar el código QR",
                "error": {
                    "code": "RESERVATION_NOT_FOUND",
                    "details": f"La reserva con ID {request.reserva_id} no existe"
                }
            }
        )
    
    # Verificar que la reserva pertenezca al usuario autenticado
    if reserva.usuario_id != current_user_id:
        return JSONResponse(
            status_code=HttpStatus.FORBIDDEN,
            content={
                "success": False,
                "statusCode": HttpStatus.FORBIDDEN,
                "message": "No autorizado"
            }
        )
    
    # Verificar que la reserva esté pagada (estado confirmada)
    if reserva.estado != EstadoReserva.CONFIRMADA:
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "No se puede generar el código QR",
                "error": {
                    "code": "PAYMENT_NOT_CONFIRMED",
                    "details": "La reserva no ha sido pagada. Debes completar el pago para generar el QR"
                }
            }
        )
    
    # Verificar si ya existe un QR activo
    qr_existente = qr_repo.get_activo_by_reserva_id(request.reserva_id)
    if qr_existente:
        return {
            "success": True,
            "statusCode": HttpStatus.OK,
            "message": "Código QR ya existe",
            "data": {
                "id": qr_existente.id,
                "reserva_id": qr_existente.reserva_id,
                "vehiculo_id": qr_existente.vehiculo_id,
                "codigo_qr": qr_existente.codigo_qr_base64,
                "estado": qr_existente.estado,
                "fecha_expiracion": qr_existente.fecha_expiracion.isoformat(),
                "fecha_generacion": qr_existente.fecha_generacion.isoformat()
            }
        }
    
        # Generar nuevo QR
    contenido_firmado, firma, fecha_expiracion = qr_service.generar_contenido_firmado(
        reserva_id=reserva.id,
        vehiculo_id=reserva.vehiculo_id,
        fecha_inicio=datetime.combine(reserva.fecha, reserva.hora_inicio),
        fecha_fin=datetime.combine(reserva.fecha, reserva.hora_fin)
    )
    
    imagen_qr = qr_service.generar_imagen_qr(contenido_firmado)
    qr_hash = qr_service.generar_hash(contenido_firmado)
    
    nuevo_qr = QR(
        reserva_id=reserva.id,
        vehiculo_id=reserva.vehiculo_id,
        codigo_hash=qr_hash,
        codigo_qr_base64=imagen_qr,
        fecha_expiracion=fecha_expiracion,
        estado=EstadoQR.ACTIVO
    )
    
    qr_guardado = qr_repo.create(nuevo_qr)
    
    return {
        "success": True,
        "statusCode": HttpStatus.CREATED,
        "message": "Código QR generado exitosamente",
        "data": {
            "id": qr_guardado.id,
            "reserva_id": qr_guardado.reserva_id,
            "vehiculo_id": qr_guardado.vehiculo_id,
            "codigo_qr": imagen_qr,
            "estado": qr_guardado.estado,
            "fecha_expiracion": fecha_expiracion.isoformat(),
            "fecha_generacion": qr_guardado.fecha_generacion.isoformat()
        }
    }
    
    # ========== HU-018: VALIDACIÓN DE QR ==========

class ValidarQRRequest(BaseModel):
    codigo_qr: str
    tipo: str = "base64"

@router.post("/validar")
async def validar_qr(
    request: ValidarQRRequest,
    current_user_id: int = Depends(get_current_user)
):
    # Buscar el QR por su código Base64
    qr_encontrado = None
    for qr in qr_repo._qrs:
        if qr.codigo_qr_base64 == request.codigo_qr:
            qr_encontrado = qr
            break
    
    if not qr_encontrado:
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Código QR inválido",
                "error": {
                    "code": "INVALID_QR_CODE",
                    "details": "El código QR no ha sido generado por el sistema o ha sido alterado"
                }
            }
        )
    
    # Verificar si ya fue usado
    if qr_encontrado.estado == EstadoQR.USADO:
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Código QR ya utilizado",
                "error": {
                    "code": "QR_ALREADY_USED",
                    "details": "Este código QR ya fue utilizado para desbloquear el vehículo"
                }
            }
        )
    
    # Verificar expiración
    if qr_encontrado.fecha_expiracion < datetime.now():
        qr_encontrado.estado = EstadoQR.EXPIRADO
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Código QR expirado",
                "error": {
                    "code": "QR_EXPIRED",
                    "details": "El código QR ha expirado. Debes solicitar uno nuevo desde la aplicación"
                }
            }
        )
    
    # Buscar la reserva asociada
    reserva = reserva_repo.get_by_id(qr_encontrado.reserva_id)
    
    if not reserva:
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Reserva no activa",
                "error": {
                    "code": "RESERVATION_NOT_ACTIVE",
                    "details": "La reserva asociada no está activa. Verifica el estado de tu reserva"
                }
            }
        )
    
    # Verificar que la reserva esté activa
    if reserva.estado not in [EstadoReserva.CONFIRMADA, EstadoReserva.EN_CURSO]:
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Reserva no activa",
                "error": {
                    "code": "RESERVATION_NOT_ACTIVE",
                    "details": "La reserva asociada no está activa. Verifica el estado de tu reserva"
                }
            }
        )
    
    # Verificar que el usuario sea el titular
    if reserva.usuario_id != current_user_id:
        return JSONResponse(
            status_code=HttpStatus.FORBIDDEN,
            content={
                "success": False,
                "statusCode": HttpStatus.FORBIDDEN,
                "message": "No autorizado",
                "error": {
                    "code": "NOT_RESERVATION_OWNER",
                    "details": "Este código QR pertenece a otra reserva. No puedes desbloquear este vehículo"
                }
            }
        )
    
    # Marcar QR como usado
    qr_encontrado.estado = EstadoQR.USADO
    qr_encontrado.fecha_uso = datetime.now()
    
    # Obtener modelo del vehículo
    from repository.vehiculo_repository import vehiculo_repo as v_repo
    vehiculo = v_repo.get_by_id(reserva.vehiculo_id)
    vehiculo_modelo = vehiculo.modelo if vehiculo else f"Vehículo {reserva.vehiculo_id}"
    
    return {
        "success": True,
        "statusCode": HttpStatus.OK,
        "message": "Código QR válido. Vehículo desbloqueado",
        "data": {
            "reserva_id": reserva.id,
            "vehiculo_id": reserva.vehiculo_id,
            "vehiculo_modelo": vehiculo_modelo,
            "valido": True
        }
    }