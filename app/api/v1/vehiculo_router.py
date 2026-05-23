from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.domain.vehiculo_domain import Vehiculo, VehiculoCreate
from app.service.vehiculo_service import VehiculoService
from app.repository.vehiculo_repository import VehiculoRepository
from app.core.constants import ErrorMessages, ErrorCodes, SuccessMessages, HttpStatus

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])
security = HTTPBearer(auto_error=False)

# Instancias
repo = VehiculoRepository()
service = VehiculoService(repo)

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica que el usuario sea administrador"""
    if not credentials:
        raise HTTPException(
            status_code=HttpStatus.UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": HttpStatus.UNAUTHORIZED,
                "message": ErrorMessages.UNAUTHORIZED,
                "error": {
                    "code": ErrorCodes.UNAUTHORIZED,
                    "details": "Se requiere token de autenticación"
                }
            }
        )
    
    token = credentials.credentials
    
    # Simulación: solo token "token_admin_valido" es admin
    if token != "token_admin_valido":
        raise HTTPException(
            status_code=HttpStatus.FORBIDDEN,
            detail={
                "success": False,
                "statusCode": HttpStatus.FORBIDDEN,
                "message": ErrorMessages.FORBIDDEN,
                "error": {
                    "code": ErrorCodes.FORBIDDEN,
                    "details": "Solo administradores pueden realizar esta acción"
                }
            }
        )
    return {"rol": "admin", "user_id": 1}


# ── ENDPOINT POST (Registro de vehículo) ──
@router.post("/", status_code=HttpStatus.CREATED)
def create_vehiculo(
    data: VehiculoCreate,
    admin: dict = Depends(verify_admin)
):
    """
    Registra un nuevo vehículo en la plataforma.
    Solo administradores.
    """
    vehiculo = service.create_vehiculo(data)
    
    return {
        "success": True,
        "statusCode": HttpStatus.CREATED,
        "message": SuccessMessages.VEHICLE_CREATED,
        "data": {
            "id": vehiculo.id,
            "tipo": vehiculo.tipo,
            "modelo": vehiculo.modelo,
            "ubicacion": vehiculo.ubicacion,
            "tarifaPorHora": float(vehiculo.tarifaPorHora),
            "estado": vehiculo.estado
        }
    }