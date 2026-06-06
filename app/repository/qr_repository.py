from typing import List, Optional
from app.domain.qr_domain import QR, EstadoQR

class QRRepository:
    def __init__(self):
        self._qrs: List[QR] = []
        self._counter = 1
    
    def create(self, qr: QR) -> QR:
        qr.id = self._counter
        self._counter += 1
        self._qrs.append(qr)
        return qr
    
    def get_by_reserva_id(self, reserva_id: int) -> Optional[QR]:
        for qr in self._qrs:
            if qr.reserva_id == reserva_id:
                return qr
        return None
    
    def get_activo_by_reserva_id(self, reserva_id: int) -> Optional[QR]:
        for qr in self._qrs:
            if qr.reserva_id == reserva_id and qr.estado == EstadoQR.ACTIVO:
                return qr
        return None

# Instancia global única
qr_repo = QRRepository()