from typing import Dict, Any
import uuid
import threading
from datetime import datetime
from service.notificacion_service import NotificacionService


class PagoService:
    
    def __init__(self, pago_repo, reserva_repo):
        self.pago_repo = pago_repo
        self.reserva_repo = reserva_repo
        self._locks = {}
        self._lock = threading.Lock()

    def _get_reserva_lock(self, reserva_id):
        """Obtener un bloqueo por reserva para prevenir concurrencia"""
        with self._lock:
            if reserva_id not in self._locks:
                self._locks[reserva_id] = threading.Lock()
            return self._locks[reserva_id]

    def _simular_pasarela_pagos(self, datos_tarjeta: dict = None) -> Dict[str, Any]:
        """Simula la integración con una pasarela de pagos externa - SIEMPRE EXITOSO"""
        return {
            "success": True,
            "transaccion_id": f"tx_{uuid.uuid4().hex[:12]}",
            "message": "Transacción aprobada"
        }

    def procesar_pago(self, usuario_id: int, data) -> Dict[str, Any]:
        """Procesa el pago de una reserva con control de concurrencia"""
        
        # Bloquear por reserva para evitar pagos duplicados simultáneos
        reserva_lock = self._get_reserva_lock(data.reserva_id)
        
        with reserva_lock:
            # 1. Obtener reserva
            reserva = self.reserva_repo.get_by_id(data.reserva_id)
            if not reserva:
                raise ValueError("RESERVATION_NOT_FOUND")
            
            # 2. Validar que el usuario sea el propietario
            if reserva.usuario_id != usuario_id:
                raise ValueError("FORBIDDEN")
            
            # 3. Validar que la reserva esté pendiente
            if reserva.estado != "pendiente":
                raise ValueError("INVALID_RESERVATION_STATUS")
            
            # 4. Validar que el monto coincida
            if data.monto != reserva.costo_estimado:
                raise ValueError(f"INVALID_AMOUNT:{reserva.costo_estimado}:{data.monto}")
            
            # 5. Verificar que no exista un pago previo aprobado
            pago_existente = self.pago_repo.get_pago_by_reserva_id(data.reserva_id)
            if pago_existente and pago_existente["estado"] == "aprobado":
                raise ValueError(f"PAYMENT_ALREADY_EXISTS:{pago_existente['id']}:{pago_existente['fecha_pago'].isoformat()}")
            
            # 6. Procesar con pasarela de pagos
            resultado_pasarela = self._simular_pasarela_pagos(data.datos_tarjeta)
            
            # 7. Registrar pago y actualizar reserva según resultado
            if resultado_pasarela["success"]:
                pago = self.pago_repo.create_pago(
                    reserva_id=data.reserva_id,
                    usuario_id=usuario_id,
                    monto=data.monto,
                    metodo_pago=data.metodo_pago,
                    estado="aprobado",
                    transaccion_id=resultado_pasarela["transaccion_id"]
                )
                self.reserva_repo.update_estado(data.reserva_id, "confirmada")
                
                # ==================== HU-016: NOTIFICACIÓN ====================
                # Generar notificación para respuesta
                notificacion = {
                    "enviada": True,
                    "mensaje": "Tu pago ha sido aprobado. Ya puedes acceder al vehículo."
                }
                
                # Enviar correo asíncrono
                asunto = f"EcoMove - Resultado de tu pago #{pago['id']}"
                cuerpo = f"""
Hola Usuario {usuario_id},

Tu pago ha sido procesado exitosamente.

Detalles de la transacción:
- Pago ID: {pago['id']}
- Reserva ID: {data.reserva_id}
- Monto: ${data.monto:,.2f}
- Fecha: {pago['fecha_pago'].strftime('%d/%m/%Y %H:%M:%S')}
- Método de pago: {data.metodo_pago}
- Estado: APROBADO

Ya puedes acceder al vehículo escaneando el código QR.

Gracias por usar EcoMove.
"""
                NotificacionService.enviar_correo_asincrono(
                    destinatario=f"usuario{usuario_id}@example.com",
                    asunto=asunto,
                    cuerpo=cuerpo
                )
                # ============================================================
                
                return {
                    "success": True,
                    "statusCode": 200,
                    "message": "Pago procesado exitosamente",
                    "data": {
                        "pago_id": pago["id"],
                        "reserva_id": data.reserva_id,
                        "monto": data.monto,
                        "metodo_pago": data.metodo_pago,
                        "estado": "aprobado",
                        "fecha_pago": pago["fecha_pago"],
                        "transaccion_id": resultado_pasarela["transaccion_id"],
                        "reserva_confirmada": True,
                        "notificacion": notificacion
                    }
                }
            else:
                pago = self.pago_repo.create_pago(
                    reserva_id=data.reserva_id,
                    usuario_id=usuario_id,
                    monto=data.monto,
                    metodo_pago=data.metodo_pago,
                    estado="rechazado",
                    transaccion_id=resultado_pasarela["transaccion_id"],
                    motivo_rechazo=resultado_pasarela["message"]
                )
                
                # ==================== HU-016: NOTIFICACIÓN PARA RECHAZO ====================
                # Enviar correo asíncrono de rechazo
                asunto = f"EcoMove - Resultado de tu pago #{pago['id']}"
                cuerpo = f"""
Hola Usuario {usuario_id},

Tu pago ha sido rechazado.

Detalles de la transacción:
- Pago ID: {pago['id']}
- Reserva ID: {data.reserva_id}
- Monto: ${data.monto:,.2f}
- Fecha: {pago['fecha_pago'].strftime('%d/%m/%Y %H:%M:%S')}
- Método de pago: {data.metodo_pago}
- Estado: RECHAZADO
- Motivo: {resultado_pasarela['message']}

Puedes reintentar el pago desde la aplicación.

Gracias por usar EcoMove.
"""
                NotificacionService.enviar_correo_asincrono(
                    destinatario=f"usuario{usuario_id}@example.com",
                    asunto=asunto,
                    cuerpo=cuerpo
                )
                # ============================================================
                
                raise ValueError(f"PAYMENT_REJECTED:{resultado_pasarela['message']}")

    # ==================== HU-014: Consulta de pagos ====================

    def get_pago_by_id(self, pago_id: int) -> dict:
        """Obtener un pago por ID"""
        pago = self.pago_repo.get_by_id(pago_id)
        if not pago:
            raise ValueError("PAYMENT_NOT_FOUND")
        return pago

    def get_pago_by_reserva_id(self, reserva_id: int) -> dict:
        """Obtener un pago por ID de reserva"""
        pago = self.pago_repo.get_by_reserva_id(reserva_id)
        if not pago:
            raise ValueError("PAYMENT_NOT_FOUND")
        return pago