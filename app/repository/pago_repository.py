from sqlalchemy.orm import Session
from typing import Optional
from app.database.database import PagoDB, ReservaDB, EstadoPagoDB, EstadoReservaDB
from app.domain.pago_domain import PagoCreate

class PagoRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_reserva_by_id(self, reserva_id: int):
        """Obtener reserva por ID"""
        return self.db.query(ReservaDB).filter(ReservaDB.id == reserva_id).first()

    def get_pago_by_reserva_id(self, reserva_id: int):
        """Obtener pago por ID de reserva"""
        return self.db.query(PagoDB).filter(PagoDB.reserva_id == reserva_id).first()

    def create_pago(self, reserva_id: int, usuario_id: int, monto: float, metodo_pago: str, 
                    estado: str, transaccion_id: str, motivo_rechazo: str = None) -> PagoDB:
        """Crear un nuevo registro de pago"""
        pago = PagoDB(
            reserva_id=reserva_id,
            usuario_id=usuario_id,
            monto=monto,
            metodo_pago=metodo_pago,
            estado=estado,
            transaccion_id=transaccion_id,
            motivo_rechazo=motivo_rechazo
        )
        self.db.add(pago)
        self.db.flush()
        return pago

    def update_reserva_estado(self, reserva_id: int, nuevo_estado: str):
        """Actualizar el estado de una reserva"""
        reserva = self.db.query(ReservaDB).filter(ReservaDB.id == reserva_id).first()
        if reserva:
            reserva.estado = nuevo_estado
            self.db.flush()
            return reserva
        return None

    def commit(self):
        """Confirmar transacción"""
        self.db.commit()