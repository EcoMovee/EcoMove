from typing import Dict, Any
from fastapi import HTTPException, status
from app.domain.pago_domain import PagoCreate
from app.repository.pago_repository import PagoRepository
import uuid
import random

class PagoService:
    
    def __init__(self, repo: PagoRepository):
        self.repo = repo

    def _simular_pasarela_pagos(self, datos_tarjeta: dict = None) -> Dict[str, Any]:
        """
        Simula la integración con una pasarela de pagos externa.
        En producción, esto llamaría a una API real como Stripe, MercadoPago, etc.
        """
        # Simular comportamiento de pasarela
        # 80% de éxito, 20% de rechazo para pruebas
        exito = random.random() > 0.2
        
        if exito:
            return {
                "success": True,
                "transaccion_id": f"tx_{uuid.uuid4().hex[:12]}",
                "message": "Transacción aprobada"
            }
        else:
            motivos = ["Fondos insuficientes", "Tarjeta inválida", "Límite excedido", "Transacción denegada"]
            return {
                "success": False,
                "transaccion_id": f"tx_{uuid.uuid4().hex[:12]}",
                "message": random.choice(motivos)
            }

    def procesar_pago(self, usuario_id: int, data: PagoCreate) -> Dict[str, Any]:
        """
        Procesa el pago de una reserva
        """
        # 1. Validar método de pago
        metodos_validos = ["tarjeta_credito", "tarjeta_debito", "monedero_electronico"]
        if data.metodo_pago not in metodos_validos:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Método de pago inválido",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": f"Método debe ser: {', '.join(metodos_validos)}"
                    }
                }
            )

        # 2. Obtener reserva
        reserva = self.repo.get_reserva_by_id(data.reserva_id)
        if not reserva:
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

        # 3. Validar que el usuario sea el propietario
        if reserva.usuario_id != usuario_id:
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

        # 4. Validar que la reserva esté pendiente
        if reserva.estado != "pendiente":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "La reserva no está pendiente de pago",
                    "error": {
                        "code": "INVALID_RESERVATION_STATUS",
                        "details": f"La reserva está en estado {reserva.estado}"
                    }
                }
            )

        # 5. Validar que el monto coincida
        if data.monto != reserva.costo_estimado:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Monto incorrecto",
                    "error": {
                        "code": "INVALID_AMOUNT",
                        "details": "El monto enviado no coincide con el costo estimado de la reserva",
                        "esperado": reserva.costo_estimado,
                        "recibido": data.monto
                    }
                }
            )

        # 6. Verificar que no exista un pago previo aprobado
        pago_existente = self.repo.get_pago_by_reserva_id(data.reserva_id)
        if pago_existente and pago_existente.estado == "aprobado":
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

        # 7. Procesar con pasarela de pagos
        try:
            resultado_pasarela = self._simular_pasarela_pagos(data.datos_tarjeta)
        except Exception as e:
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

        # 8. Registrar pago y actualizar reserva según resultado
        if resultado_pasarela["success"]:
            # Pago exitoso
            pago = self.repo.create_pago(
                reserva_id=data.reserva_id,
                usuario_id=usuario_id,
                monto=data.monto,
                metodo_pago=data.metodo_pago,
                estado="aprobado",
                transaccion_id=resultado_pasarela["transaccion_id"]
            )
            self.repo.update_reserva_estado(data.reserva_id, "confirmada")
            self.repo.commit()
            
            return {
                "success": True,
                "statusCode": 200,
                "message": "Pago procesado exitosamente",
                "data": {
                    "pago_id": pago.id,
                    "reserva_id": data.reserva_id,
                    "monto": data.monto,
                    "metodo_pago": data.metodo_pago,
                    "estado": "aprobado",
                    "fecha_pago": pago.fecha_pago,
                    "transaccion_id": resultado_pasarela["transaccion_id"],
                    "reserva_confirmada": True
                }
            }
        else:
            # Pago rechazado
            pago = self.repo.create_pago(
                reserva_id=data.reserva_id,
                usuario_id=usuario_id,
                monto=data.monto,
                metodo_pago=data.metodo_pago,
                estado="rechazado",
                transaccion_id=resultado_pasarela["transaccion_id"],
                motivo_rechazo=resultado_pasarela["message"]
            )
            self.repo.commit()
            
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Pago rechazado",
                    "error": {
                        "code": "PAYMENT_REJECTED",
                        "details": "La transacción fue rechazada por la pasarela de pagos",
                        "motivo": resultado_pasarela["message"]
                    }
                }
            )