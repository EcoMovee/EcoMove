from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.pago_domain import PagoCreate
from app.service.pago_service import PagoService
from app.repository.pago_repository import PagoRepository
from app.database.database import get_db
from app.core.security import verify_token
from sqlalchemy.orm import Session

router = APIRouter(prefix="/pagos", tags=["Pagos"])

def get_service(db: Session = Depends(get_db)):
    repo = PagoRepository(db)
    return PagoService(repo)


@router.post("/", status_code=status.HTTP_200_OK)
def procesar_pago(
    data: PagoCreate,
    service: PagoService = Depends(get_service),
    token_payload: dict = Depends(verify_token)
):
    """
    Procesa el pago de una reserva.
    - Requiere autenticación JWT
    - Valida que el usuario sea propietario de la reserva
    - Valida que la reserva esté pendiente
    - Valida que el monto coincida
    - Integra con pasarela de pagos
    """
    # Obtener el ID del usuario desde el token
    # Si tu token tiene 'user_id' úsalo, si no, usa el email o un ID temporal
    usuario_id = token_payload.get("user_id")
    if not usuario_id:
        # Por ahora, asignamos un ID de prueba
        # TODO: Implementar consulta real por email
        usuario_id = 1
    
    return service.procesar_pago(usuario_id, data)