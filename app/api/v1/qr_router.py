from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from core.dependencies import get_current_user
from core.constants import HttpStatus, ErrorCodes
from service.qr_service import QRService
from repository.qr_repository import qr_repo
from repository.reserva_repository import reserva_repo
from domain.qr_domain import QR, EstadoQR
from domain.reserva_domain import EstadoReserva
from domain.log_escaneo_domain import LogEscaneoQR, ResultadoEscaneo
from repository.log_escaneo_repository import log_repo

router = APIRouter(prefix="/api/v1/qrs", tags=["QR"])
qr_service = QRService()

class GenerarQRRequest(BaseModel):
    reserva_id: int

@router.post("", status_code=201)
async def generar_qr(
    request: GenerarQRRequest,
    current_user_id: int = Depends(get_current_user)
):
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
    
    if reserva.usuario_id != current_user_id:
        return JSONResponse(
            status_code=HttpStatus.FORBIDDEN,
            content={
                "success": False,
                "statusCode": HttpStatus.FORBIDDEN,
                "message": "No autorizado"
            }
        )
    
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


class ValidarQRRequest(BaseModel):
    codigo_qr: str
    tipo: str = "base64"

@router.post("/validar")
async def validar_qr(
    request: ValidarQRRequest,
    current_user_id: int = Depends(get_current_user),
    ip_origen: str = None
):
    # Buscar el QR por su código Base64
    qr_encontrado = None
    for qr in qr_repo._qrs:
        if qr.codigo_qr_base64 == request.codigo_qr:
            qr_encontrado = qr
            break
    
    if not qr_encontrado:
        log_repo.create(LogEscaneoQR(
            qr_id=0,
            usuario_id=current_user_id,
            resultado=ResultadoEscaneo.FALLIDO,
            motivo="QR_NOT_FOUND",
            ip_origen=ip_origen
        ))
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Código QR inválido o expirado",
                "error": {
                    "code": "QR_INVALID_OR_EXPIRED",
                    "details": "El código QR no es válido o ya no está activo"
                }
            }
        )
    
    # Verificar si ya fue usado
    if qr_encontrado.estado == EstadoQR.USADO:
        log_repo.create(LogEscaneoQR(
            qr_id=qr_encontrado.id,
            usuario_id=current_user_id,
            resultado=ResultadoEscaneo.FALLIDO,
            motivo="QR_ALREADY_USED",
            ip_origen=ip_origen
        ))
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Código QR inválido o expirado",
                "error": {
                    "code": "QR_INVALID_OR_EXPIRED",
                    "details": "El código QR ya fue utilizado"
                }
            }
        )
    
    # Verificar expiración por tiempo
    if qr_encontrado.fecha_expiracion < datetime.now():
        qr_encontrado.estado = EstadoQR.EXPIRADO
        log_repo.create(LogEscaneoQR(
            qr_id=qr_encontrado.id,
            usuario_id=current_user_id,
            resultado=ResultadoEscaneo.FALLIDO,
            motivo="QR_EXPIRED_BY_TIME",
            ip_origen=ip_origen
        ))
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Código QR inválido o expirado",
                "error": {
                    "code": "QR_INVALID_OR_EXPIRED",
                    "details": "El código QR ha expirado"
                }
            }
        )
    
    # Buscar la reserva asociada
    reserva = reserva_repo.get_by_id(qr_encontrado.reserva_id)
    
    if not reserva:
        log_repo.create(LogEscaneoQR(
            qr_id=qr_encontrado.id,
            usuario_id=current_user_id,
            resultado=ResultadoEscaneo.FALLIDO,
            motivo="RESERVATION_NOT_FOUND",
            ip_origen=ip_origen
        ))
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Código QR inválido o expirado",
                "error": {
                    "code": "QR_INVALID_OR_EXPIRED",
                    "details": "La reserva asociada no existe"
                }
            }
        )
    
    # Verificar expiración por fin de reserva (HU-019)
    hora_inicio_dt = datetime.combine(reserva.fecha, reserva.hora_inicio)
    hora_fin_dt = datetime.combine(reserva.fecha, reserva.hora_fin)
    
    if hora_fin_dt < datetime.now():
        qr_encontrado.estado = EstadoQR.EXPIRADO
        log_repo.create(LogEscaneoQR(
            qr_id=qr_encontrado.id,
            usuario_id=current_user_id,
            resultado=ResultadoEscaneo.FALLIDO,
            motivo="RESERVATION_ENDED",
            ip_origen=ip_origen
        ))
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Código QR inválido o expirado",
                "error": {
                    "code": "QR_INVALID_OR_EXPIRED",
                    "details": "La reserva ya ha finalizado"
                }
            }
        )
    
    # ========== HU-020: VERIFICACIONES ==========
    
    # 1. Verificar que la reserva esté activa
    if reserva.estado not in [EstadoReserva.CONFIRMADA, EstadoReserva.EN_CURSO]:
        log_repo.create(LogEscaneoQR(
            qr_id=qr_encontrado.id,
            usuario_id=current_user_id,
            resultado=ResultadoEscaneo.FALLIDO,
            motivo="RESERVATION_NOT_ACTIVE",
            ip_origen=ip_origen
        ))
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Código QR inválido o expirado",
                "error": {
                    "code": "QR_INVALID_OR_EXPIRED",
                    "details": "La reserva no está activa"
                }
            }
        )
    
    # 2. Verificar que el usuario sea el titular
    if reserva.usuario_id != current_user_id:
        log_repo.create(LogEscaneoQR(
            qr_id=qr_encontrado.id,
            usuario_id=current_user_id,
            resultado=ResultadoEscaneo.FALLIDO,
            motivo="NOT_RESERVATION_OWNER",
            ip_origen=ip_origen
        ))
        return JSONResponse(
            status_code=HttpStatus.FORBIDDEN,
            content={
                "success": False,
                "statusCode": HttpStatus.FORBIDDEN,
                "message": "No autorizado",
                "error": {
                    "code": "NOT_RESERVATION_OWNER",
                    "details": "Este código QR pertenece a otra reserva"
                }
            }
        )
    
    # 3. Verificar que el vehículo coincida (HU-020)
    if reserva.vehiculo_id != qr_encontrado.vehiculo_id:
        log_repo.create(LogEscaneoQR(
            qr_id=qr_encontrado.id,
            usuario_id=current_user_id,
            resultado=ResultadoEscaneo.FALLIDO,
            motivo="VEHICLE_MISMATCH",
            ip_origen=ip_origen
        ))
        return JSONResponse(
            status_code=HttpStatus.BAD_REQUEST,
            content={
                "success": False,
                "statusCode": HttpStatus.BAD_REQUEST,
                "message": "Vehículo incorrecto",
                "error": {
                    "code": "VEHICLE_MISMATCH",
                    "details": "El código QR no corresponde al vehículo que estás intentando desbloquear"
                }
            }
        )
    
    # 4. Si la reserva está confirmada, actualizar a en_curso (HU-020)
    if reserva.estado == EstadoReserva.CONFIRMADA:
        reserva.estado = EstadoReserva.EN_CURSO
        reserva.fecha_inicio_viaje = datetime.now()
        reserva_repo.update(reserva.id, reserva)
    
    # ========== VALIDACIÓN EXITOSA ==========
    
    # Marcar QR como usado
    qr_encontrado.estado = EstadoQR.USADO
    qr_encontrado.fecha_uso = datetime.now()
    
    # Registrar intento exitoso
    log_repo.create(LogEscaneoQR(
        qr_id=qr_encontrado.id,
        usuario_id=current_user_id,
        resultado=ResultadoEscaneo.EXITOSO,
        motivo=None,
        ip_origen=ip_origen
    ))
    
    # Obtener modelo del vehículo
    from repository.vehiculo_repository import vehiculo_repo as v_repo
    vehiculo = v_repo.get_by_id(reserva.vehiculo_id)
    vehiculo_modelo = vehiculo.modelo if vehiculo else f"Vehículo {reserva.vehiculo_id}"
    
    return {
        "success": True,
        "statusCode": HttpStatus.OK,
        "message": "Reserva activa. Vehículo desbloqueado",
        "data": {
            "reserva_id": reserva.id,
            "vehiculo_id": reserva.vehiculo_id,
            "vehiculo_modelo": vehiculo_modelo,
            "estado_reserva": reserva.estado.value,
            "inicio_reserva": hora_inicio_dt.isoformat(),
            "fin_reserva": hora_fin_dt.isoformat()
        }
    }