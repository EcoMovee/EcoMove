from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.domain.vehiculo_domain import Vehiculo, VehiculoCreate
from app.service.vehiculo_service import VehiculoService
from app.repository.vehiculo_repository import VehiculoRepository
from app.core.constants import ErrorMessages, ErrorCodes, SuccessMessages, HttpStatus

repo = VehiculoRepository()
service = VehiculoService(repo)

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])

security = HTTPBearer(auto_error=False)

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
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

@router.get("/", response_model=list[Vehiculo])
def list_vehiculos():
    return service.get_all_vehiculos()

@router.get("/{vehiculo_id}", response_model=Vehiculo)
def get_vehiculo(vehiculo_id: int):
    return service.get_vehiculo(vehiculo_id)

@router.post("/", status_code=HttpStatus.CREATED)
def create_vehiculo(data: VehiculoCreate, admin: dict = Depends(verify_admin)):
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

@router.delete("/{vehiculo_id}", status_code=HttpStatus.OK)
def delete_vehiculo(vehiculo_id: int, admin: dict = Depends(verify_admin)):
    return service.delete_vehiculo(vehiculo_id)

@router.patch("/{vehiculo_id}/estado", response_model=Vehiculo)
def update_estado_vehiculo(vehiculo_id: int, estado: str, admin: dict = Depends(verify_admin)):
    return service.update_estado(vehiculo_id, estado)