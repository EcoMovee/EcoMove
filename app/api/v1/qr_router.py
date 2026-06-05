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