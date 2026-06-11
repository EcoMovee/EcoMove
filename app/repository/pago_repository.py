from datetime import datetime
from typing import Dict, Optional


class PagoRepository:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._db = {}
            cls._instance._next_id = 1
        return cls._instance
    
    def __init__(self):
        pass

    def get_pago_by_reserva_id(self, reserva_id: int) -> Optional[dict]:
        for pago in self._db.values():
            if pago["reserva_id"] == reserva_id:
                return pago
        return None

    def create_pago(self, reserva_id: int, usuario_id: int, monto: float,
                    metodo_pago: str, estado: str, transaccion_id: str,
                    motivo_rechazo: str = None) -> dict:
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

    def get_by_id(self, pago_id: int) -> Optional[dict]:
        return self._db.get(pago_id)

    def get_by_reserva_id(self, reserva_id: int) -> Optional[dict]:
        for pago in self._db.values():
            if pago["reserva_id"] == reserva_id:
                return pago
        return None