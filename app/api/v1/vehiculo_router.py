from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.vehiculo_domain import VehiculoCreate
from app.service.vehiculo_service import VehiculoService
from app.repository.vehiculo_repository import VehiculoRepository
from app.core.security import verify_admin

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