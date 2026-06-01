from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.vehiculo_domain import VehiculoCreate
from app.service.vehiculo_service import VehiculoService
from app.repository.vehiculo_repository import VehiculoRepository
from app.core.security import verify_admin
from typing import Optional
from app.domain.vehiculo_domain import VehiculoCreate, EstadoUpdateRequest
from app.core.security import verify_admin, verify_token

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
        
# ==================== HU-007: Actualización de estado ====================

@router.patch("/estado/{vehiculo_id}", status_code=status.HTTP_200_OK)
def update_vehiculo_estado(
    vehiculo_id: int,
    request: EstadoUpdateRequest,
    admin: dict = Depends(verify_admin)
):
    """
    Actualiza el estado de un vehículo.
    Solo administradores.
    """
    from datetime import datetime
    
    try:
        admin_id = admin.get("id", 1)
        vehiculo, estado_anterior, reservas_afectadas = service.update_estado(
            vehiculo_id=vehiculo_id,
            nuevo_estado=request.nuevo_estado,
            admin_id=admin_id,
            confirmar=request.confirmar_reservas_futuras
        )
        
        mensaje = "Estado del vehículo actualizado correctamente"
        if reservas_afectadas > 0:
            mensaje = f"Estado actualizado con advertencia: El vehículo tiene {reservas_afectadas} reservas futuras que serán afectadas"
        
        return {
            "success": True,
            "statusCode": 200,
            "message": mensaje,
            "data": {
                "id": vehiculo.id,
                "tipo": vehiculo.tipo,
                "modelo": vehiculo.modelo,
                "estado_anterior": estado_anterior,
                "estado_nuevo": vehiculo.estado,
                "fecha_cambio": datetime.now().isoformat(),
                "reservas_afectadas": reservas_afectadas
            }
        }
    
    except ValueError as e:
        error_msg = str(e)
        
        if error_msg == "VEHICLE_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": "Vehículo no encontrado",
                    "error": {
                        "code": "VEHICLE_NOT_FOUND",
                        "details": "No existe un vehículo con el ID proporcionado"
                    }
                }
            )
        
        if error_msg.startswith("INVALID_TRANSITION"):
            partes = error_msg.split(":")
            estado_actual = partes[1] if len(partes) > 1 else "desconocido"
            estado_nuevo = partes[2] if len(partes) > 2 else "desconocido"
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Transición de estado no permitida",
                    "error": {
                        "code": "INVALID_STATE_TRANSITION",
                        "details": f"No se puede cambiar de '{estado_actual}' a '{estado_nuevo}'. Debe pasar primero a 'disponible'"
                    }
                }
            )
        
        if error_msg.startswith("RESERVAS_FUTURAS"):
            cantidad = error_msg.split(":")[1]
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "El vehículo tiene reservas futuras",
                    "error": {
                        "code": "RESERVAS_FUTURAS",
                        "details": f"El vehículo tiene {cantidad} reservas futuras. Confirme para continuar"
                    }
                }
            )
        
        raise HTTPException(status_code=500, detail={"message": error_msg})
    
# ==================== HU-006 + HU-008: Consulta de vehículos disponibles (excluye mantenimiento) ====================

@router.get("/disponibles", status_code=status.HTTP_200_OK)
def get_vehiculos_disponibles(
    tipo: Optional[str] = None,
    latitud: Optional[float] = None,
    longitud: Optional[float] = None,
    radio_km: Optional[float] = None,
    token: dict = Depends(verify_token)
):
    """Consulta vehículos disponibles. Excluye vehículos en mantenimiento y en_uso."""
    try:
        # Por ahora, solo devuelve disponibles (sin distancia)
        vehiculos = service.get_vehiculos_disponibles_excluyendo_mantenimiento(tipo)
        
        total = len(vehiculos)
        
        if total == 0:
            return {
                "success": True,
                "statusCode": 200,
                "message": "No hay vehículos disponibles con los filtros seleccionados",
                "data": {
                    "total": 0,
                    "filtros_aplicados": {"tipo": tipo} if tipo else None,
                    "vehiculos": []
                }
            }
        
        return {
            "success": True,
            "statusCode": 200,
            "message": "Vehículos disponibles encontrados",
            "data": {
                "total": total,
                "filtros_aplicados": {"tipo": tipo} if tipo else None,
                "vehiculos": [v.model_dump() for v in vehiculos]
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "statusCode": 503,
                "message": "Error de conexión con la base de datos",
                "error": {
                    "code": "DATABASE_ERROR",
                    "details": "Intente nuevamente más tarde"
                }
            }
        )
        
        
# ==================== HU-008: Panel de administración (vehículos en mantenimiento) ====================

@router.get("/", status_code=status.HTTP_200_OK)
def get_vehiculos_by_estado(
    estado: str,
    tipo: Optional[str] = None,
    admin: dict = Depends(verify_admin)
):
    """Panel de administración: consulta vehículos por estado. Solo administradores."""
    try:
        vehiculos = service.get_vehiculos_by_estado(estado, tipo)
        total = len(vehiculos)
        
        mensaje = f"Vehículos en {estado} encontrados"
        
        return {
            "success": True,
            "statusCode": 200,
            "message": mensaje,
            "data": {
                "total": total,
                "vehiculos": [
                    {
                        "id": v.id,
                        "tipo": v.tipo,
                        "modelo": v.modelo,
                        "ubicacion": v.ubicacion,
                        "tarifaPorHora": v.tarifaPorHora,
                        "estado": v.estado
                    }
                    for v in vehiculos
                ]
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "statusCode": 503,
                "message": "Error de conexión con la base de datos",
                "error": {
                    "code": "DATABASE_ERROR",
                    "details": "Intente nuevamente más tarde"
                }
            }
        )