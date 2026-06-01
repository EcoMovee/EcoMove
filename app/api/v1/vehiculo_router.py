from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.vehiculo_domain import VehiculoCreate
from app.service.vehiculo_service import VehiculoService
from app.repository.vehiculo_repository import VehiculoRepository
from app.core.security import verify_admin
from typing import Optional

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])

repo = VehiculoRepository()
service = VehiculoService(repo)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vehiculo(
    data: VehiculoCreate,
    admin: dict = Depends(verify_admin)
):
    try:
        vehiculo = service.create(data)
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
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "VEHICLE_ALREADY_EXISTS":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "El vehículo ya está registrado",
                    "error": {
                        "code": "VEHICLE_ALREADY_EXISTS",
                        "details": f"El vehículo con modelo {data.modelo} ya existe en el sistema"
                    }
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Datos inválidos",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": error_msg
                    }
                }
            )
            
            
            
# ==================== HU-006: Consulta de vehículos disponibles ====================

@router.get("/disponibles", status_code=status.HTTP_200_OK)
def get_vehiculos_disponibles(
    tipo: Optional[str] = None,
    latitud: Optional[float] = None,
    longitud: Optional[float] = None,
    radio_km: Optional[float] = None,
    admin: dict = Depends(verify_admin)
):
    """Consulta vehículos disponibles. Requiere autenticación JWT."""
    try:
        vehiculos, filtros = service.get_vehiculos_disponibles(
            tipo=tipo, latitud=latitud, longitud=longitud, radio_km=radio_km
        )
        
        total = len(vehiculos)
        
        if total == 0:
            return {
                "success": True,
                "statusCode": 200,
                "message": "No hay vehículos disponibles con los filtros seleccionados",
                "data": {
                    "total": 0,
                    "filtros_aplicados": filtros if any(filtros.values()) else None,
                    "vehiculos": []
                }
            }
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "Vehículos disponibles encontrados",
            "data": {
                "total": total,
                "filtros_aplicados": filtros if any(filtros.values()) else None,
                "vehiculos": [v.model_dump() for v in vehiculos]
            }
        }
    
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "INVALID_RADIUS":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Parámetros de filtro inválidos",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": "El radio debe ser un número positivo"
                    }
                }
            )
        elif error_msg == "INVALID_TYPE":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Parámetros de filtro inválidos",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": "El tipo debe ser carro, moto o bicicleta"
                    }
                }
            )
        else:
            raise HTTPException(status_code=500, detail={"message": error_msg})