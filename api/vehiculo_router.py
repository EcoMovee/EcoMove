from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from domain.models import Vehiculo, VehiculoCreate
from service.vehiculo_service import VehiculoService
from repository.vehiculo_repo import VehiculoRepository

# Instancias
repo = VehiculoRepository()
service = VehiculoService(repo)

# Router
router = APIRouter(prefix="/api/v1/vehiculos", tags=["vehiculos"])

# Autenticación
security = HTTPBearer(auto_error=False)

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica que el usuario sea administrador"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "statusCode": 401,
                "message": "Token no proporcionado",
                "error": {
                    "code": "UNAUTHORIZED",
                    "details": "Se requiere token de autenticación"
                }
            }
        )
    
    token = credentials.credentials
    
    # Simulación: solo token "token_admin_valido" es admin
    if token != "token_admin_valido":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "statusCode": 403,
                "message": "Acceso denegado. Se requieren privilegios de administrador",
                "error": {
                    "code": "FORBIDDEN",
                    "details": "Solo administradores pueden realizar esta acción"
                }
            }
        )
    return {"rol": "admin", "user_id": 1}

# ── Endpoints públicos ──
@router.get("/", response_model=list[Vehiculo])
def list_vehiculos():
    return service.get_all_vehiculos()

@router.get("/{vehiculo_id}", response_model=Vehiculo)
def get_vehiculo(vehiculo_id: int):
    return service.get_vehiculo(vehiculo_id)

# ── Endpoints protegidos (solo admin) ──
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vehiculo(data: VehiculoCreate, admin: dict = Depends(verify_admin)):
    vehiculo = service.create_vehiculo(data)
    
    return {
        "success": True,
        "statusCode": 201,
        "message": "Vehículo creado correctamente",
        "data": {
            "id": vehiculo.id,
            "tipo": vehiculo.tipo,
            "modelo": vehiculo.modelo,
            "ubicacion": vehiculo.ubicacion,
            "tarifaPorHora": float(vehiculo.tarifaPorHora),
            "estado": vehiculo.estado
        }
    }

@router.delete("/{vehiculo_id}", status_code=status.HTTP_200_OK)
def delete_vehiculo(vehiculo_id: int, admin: dict = Depends(verify_admin)):
    return service.delete_vehiculo(vehiculo_id)