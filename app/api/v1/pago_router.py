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
    """Procesa el pago de una reserva. Requiere autenticación JWT."""
    
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
        
        if error_msg.startswith("PAYMENT_ALREADY_EXISTS"):
            partes = error_msg.split(":")
            pago_id = partes[1] if len(partes) > 1 else "desconocido"
            fecha_pago = partes[2] if len(partes) > 2 else "desconocida"
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Esta reserva ya ha sido pagada",
                    "error": {
                        "code": "PAYMENT_ALREADY_EXISTS",
                        "details": "La reserva ya tiene un pago aprobado asociado",
                        "pago_id": int(pago_id) if str(pago_id).isdigit() else pago_id,
                        "fecha_pago": fecha_pago
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


# ==================== HU-014: Consulta de pagos ====================

@router.get("/{pago_id}", status_code=status.HTTP_200_OK)
def get_pago_by_id(
    pago_id: int,
    token_payload: dict = Depends(verify_token)
):
    """Consultar un pago por su ID. Requiere autenticación JWT."""
    try:
        pago = service.get_pago_by_id(pago_id)
        return {
            "success": True,
            "statusCode": 200,
            "message": "Pago encontrado",
            "data": {
                "id": pago["id"],
                "reserva_id": pago["reserva_id"],
                "usuario_id": pago["usuario_id"],
                "monto": pago["monto"],
                "metodo_pago": pago["metodo_pago"],
                "estado": pago["estado"],
                "transaccion_id": pago["transaccion_id"],
                "fecha_pago": pago["fecha_pago"].isoformat(),
                "motivo_rechazo": pago.get("motivo_rechazo")
            }
        }
    except ValueError as e:
        if str(e) == "PAYMENT_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": "Pago no encontrado",
                    "error": {
                        "code": "PAYMENT_NOT_FOUND",
                        "details": "No existe un pago con el ID proporcionado"
                    }
                }
            )
        raise HTTPException(status_code=500, detail={"message": str(e)})


@router.get("/reserva/{reserva_id}", status_code=status.HTTP_200_OK)
def get_pago_by_reserva(
    reserva_id: int,
    token_payload: dict = Depends(verify_token)
):
    """Consultar un pago por ID de reserva. Requiere autenticación JWT."""
    try:
        pago = service.get_pago_by_reserva_id(reserva_id)
        return {
            "success": True,
            "statusCode": 200,
            "message": "Pago encontrado",
            "data": {
                "id": pago["id"],
                "reserva_id": pago["reserva_id"],
                "usuario_id": pago["usuario_id"],
                "monto": pago["monto"],
                "metodo_pago": pago["metodo_pago"],
                "estado": pago["estado"],
                "transaccion_id": pago["transaccion_id"],
                "fecha_pago": pago["fecha_pago"].isoformat(),
                "motivo_rechazo": pago.get("motivo_rechazo")
            }
        }
    except ValueError as e:
        if str(e) == "PAYMENT_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": "Pago no encontrado",
                    "error": {
                        "code": "PAYMENT_NOT_FOUND",
                        "details": "No existe un pago asociado a la reserva proporcionada"
                    }
                }
            )
        raise HTTPException(status_code=500, detail={"message": str(e)})