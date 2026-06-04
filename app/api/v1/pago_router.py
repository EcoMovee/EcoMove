from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.pago_domain import PagoRequest
from app.service.pago_service import PagoService
from app.repository.pago_repository import PagoRepository
from app.repository.reserva_repository import reserva_repo
from app.core.security import verify_token

router = APIRouter(prefix="/pagos", tags=["Pagos"])

pago_repo = PagoRepository()
service = PagoService(pago_repo, reserva_repo)


@router.post("/", status_code=status.HTTP_200_OK)
def procesar_pago(
    data: PagoRequest,
    token_payload: dict = Depends(verify_token)
):
    usuario_id = token_payload.get("id", 1)
    
    try:
        result = service.procesar_pago(usuario_id, data)
        return result
    
    except ValueError as e:
        error_msg = str(e)
        
        if error_msg == "RESERVATION_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": "Reserva no encontrada",
                    "error": {
                        "code": "RESERVATION_NOT_FOUND",
                        "details": f"La reserva con ID {data.reserva_id} no existe"
                    }
                }
            )
        
        if error_msg == "FORBIDDEN":
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "statusCode": 403,
                    "message": "Acceso denegado",
                    "error": {
                        "code": "FORBIDDEN",
                        "details": "No eres el propietario de esta reserva"
                    }
                }
            )
        
        if error_msg == "INVALID_RESERVATION_STATUS":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "La reserva no está pendiente de pago",
                    "error": {
                        "code": "INVALID_RESERVATION_STATUS",
                        "details": "La reserva ya fue pagada o cancelada"
                    }
                }
            )
        
        if error_msg.startswith("INVALID_AMOUNT"):
            partes = error_msg.split(":")
            esperado = float(partes[1]) if len(partes) > 1 else 0
            recibido = float(partes[2]) if len(partes) > 2 else 0
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Monto incorrecto",
                    "error": {
                        "code": "INVALID_AMOUNT",
                        "details": "El monto enviado no coincide con el costo estimado de la reserva",
                        "esperado": esperado,
                        "recibido": recibido
                    }
                }
            )
        
        if error_msg == "PAYMENT_ALREADY_EXISTS":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "La reserva ya ha sido pagada",
                    "error": {
                        "code": "PAYMENT_ALREADY_EXISTS",
                        "details": "Esta reserva ya tiene un pago aprobado"
                    }
                }
            )
        
        if error_msg == "PAYMENT_GATEWAY_ERROR":
            raise HTTPException(
                status_code=503,
                detail={
                    "success": False,
                    "statusCode": 503,
                    "message": "Error con la pasarela de pagos",
                    "error": {
                        "code": "PAYMENT_GATEWAY_ERROR",
                        "details": "La pasarela de pagos no está disponible"
                    }
                }
            )
        
        if error_msg.startswith("PAYMENT_REJECTED"):
            motivo = error_msg.split(":", 1)[1] if ":" in error_msg else "Transacción rechazada"
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Pago rechazado",
                    "error": {
                        "code": "PAYMENT_REJECTED",
                        "details": "La transacción fue rechazada por la pasarela de pagos",
                        "motivo": motivo
                    }
                }
            )
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "statusCode": 500,
                "message": "Error interno del servidor",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "details": error_msg
                }
            }
        )