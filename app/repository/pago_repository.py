from datetime import datetime
from typing import Dict, Optional


class PagoRepository:
    
    def __init__(self):
        self._db: Dict[int, dict] = {}
        self._next_id: int = 1

    def get_pago_by_reserva_id(self, reserva_id: int) -> Optional[dict]:
        """Obtener pago por ID de reserva"""
        for pago in self._db.values():
            if pago["reserva_id"] == reserva_id:
                return pago
        return None

    def create_pago(self, reserva_id: int, usuario_id: int, monto: float,
                    metodo_pago: str, estado: str, transaccion_id: str,
                    motivo_rechazo: str = None) -> dict:
        """Crear un nuevo registro de pago"""
        pago = {
            "id": self._next_id,
            "reserva_id": reserva_id,
            "usuario_id": usuario_id,
            "monto": monto,
            "metodo_pago": metodo_pago,
            "estado": estado,
            "transaccion_id": transaccion_id,
            "fecha_pago": datetime.now(),
            "motivo_rechazo": motivo_rechazo
        }
        self._db[self._next_id] = pago
        self._next_id += 1
        return pago
    

