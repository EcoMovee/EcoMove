import threading
import time
from datetime import datetime


class NotificacionService:
    
    @staticmethod
    def enviar_correo_asincrono(destinatario: str, asunto: str, cuerpo: str):
        """Envía un correo electrónico de forma asíncrona (simulado)"""
        def enviar():
            # Simular envío de correo
            time.sleep(0.5)  # Simula el tiempo de envío
            print(f"\n📧 CORREO ENVIADO (SIMULADO)")
            print(f"   Para: {destinatario}")
            print(f"   Asunto: {asunto}")
            print(f"   Cuerpo:\n{cuerpo}\n")
        
        # Ejecutar en un hilo separado (asíncrono)
        hilo = threading.Thread(target=enviar)
        hilo.start()
    
    @staticmethod
    def generar_notificacion(estado: str, monto: float, reserva_id: int, 
                             metodo_pago: str, fecha_pago: datetime, 
                             motivo_rechazo: str = None) -> dict:
        """Genera la notificación para la respuesta HTTP"""
        if estado == "aprobado":
            return {
                "enviada": True,
                "mensaje": "Tu pago ha sido aprobado. Ya puedes acceder al vehículo."
            }
        else:
            return {
                "enviada": True,
                "mensaje": "Tu pago fue rechazado. Puedes reintentar con otro método de pago."
            }
    
    @staticmethod
    def generar_correo(usuario_nombre: str, estado: str, pago_id: int, 
                       reserva_id: int, monto: float, fecha_pago: datetime,
                       metodo_pago: str, motivo_rechazo: str = None) -> tuple:
        """Genera el asunto y cuerpo del correo electrónico"""
        
        fecha_str = fecha_pago.strftime("%d/%m/%Y %H:%M:%S")
        
        if estado == "aprobado":
            asunto = f"EcoMove - Resultado de tu pago #{pago_id}"
            cuerpo = f"""
Hola {usuario_nombre},

Tu pago ha sido procesado exitosamente.

Detalles de la transacción:
- Pago ID: {pago_id}
- Reserva ID: {reserva_id}
- Monto: ${monto:,.2f}
- Fecha: {fecha_str}
- Método de pago: {metodo_pago}
- Estado: APROBADO

Ya puedes acceder al vehículo escaneando el código QR.

Gracias por usar EcoMove.
"""
        else:
            asunto = f"EcoMove - Resultado de tu pago #{pago_id}"
            cuerpo = f"""
Hola {usuario_nombre},

Tu pago ha sido rechazado.

Detalles de la transacción:
- Pago ID: {pago_id}
- Reserva ID: {reserva_id}
- Monto: ${monto:,.2f}
- Fecha: {fecha_str}
- Método de pago: {metodo_pago}
- Estado: RECHAZADO
- Motivo: {motivo_rechazo or "No especificado"}

Puedes reintentar el pago desde la aplicación.

Gracias por usar EcoMove.
"""
        return asunto, cuerpo