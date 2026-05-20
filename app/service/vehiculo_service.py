from typing import List
from fastapi import HTTPException

from app.domain.vehiculo_domain import Vehiculo, VehiculoCreate, EstadoVehiculo
from app.repository.vehiculo_repository import VehiculoRepository
from app.core.constants import (
    VehicleTypes, VehicleConfig, ErrorMessages, ErrorCodes, 
    SuccessMessages, HttpStatus, VehicleStatus
)


class VehiculoService:
    
    def __init__(self, repo: VehiculoRepository):
        self.repo = repo
    
    def get_all_vehiculos(self) -> List[Vehiculo]:
        return self.repo.get_all()
    
    def get_vehiculo(self, vehiculo_id: int) -> Vehiculo:
        vehiculo = self.repo.get_by_id(vehiculo_id)
        
        if not vehiculo:
            raise HTTPException(
                status_code=HttpStatus.NOT_FOUND,
                detail={
                    "success": False,
                    "statusCode": HttpStatus.NOT_FOUND,
                    "message": ErrorMessages.VEHICLE_NOT_FOUND,
                    "error": {
                        "code": ErrorCodes.VEHICLE_NOT_FOUND,
                        "details": f"Vehículo con ID {vehiculo_id} no existe"
                    }
                }
            )
        return vehiculo
    
    def create_vehiculo(self, data: VehiculoCreate) -> Vehiculo:
        if data.tipo not in VehicleTypes.ALLOWED:
            raise HTTPException(
                status_code=HttpStatus.BAD_REQUEST,
                detail={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Datos inválidos",
                    "error": {
                        "code": ErrorCodes.INVALID_DATA,
                        "details": ErrorMessages.INVALID_VEHICLE_TYPE
                    }
                }
            )
        
        if data.tarifaPorHora <= 0:
            raise HTTPException(
                status_code=HttpStatus.BAD_REQUEST,
                detail={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Datos inválidos",
                    "error": {
                        "code": ErrorCodes.INVALID_DATA,
                        "details": ErrorMessages.INVALID_TARIFA
                    }
                }
            )
        
        existing = self.repo.get_by_modelo(data.modelo)
        if existing:
            raise HTTPException(
                status_code=HttpStatus.BAD_REQUEST,
                detail={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": ErrorMessages.VEHICLE_ALREADY_EXISTS,
                    "error": {
                        "code": ErrorCodes.VEHICLE_ALREADY_EXISTS,
                        "details": f"El vehículo con modelo {data.modelo} ya existe en el sistema"
                    }
                }
            )
        
        new_vehiculo = self.repo.create(data)
        
        if not new_vehiculo:
            raise HTTPException(
                status_code=HttpStatus.SERVICE_UNAVAILABLE,
                detail={
                    "success": False,
                    "statusCode": HttpStatus.SERVICE_UNAVAILABLE,
                    "message": ErrorMessages.DB_CONNECTION_ERROR,
                    "error": {
                        "code": ErrorCodes.DB_CONNECTION_ERROR,
                        "details": "No se pudo completar la operación"
                    }
                }
            )
        
        return new_vehiculo
    
    def delete_vehiculo(self, vehiculo_id: int) -> dict:
        deleted = self.repo.delete(vehiculo_id)
        
        if not deleted:
            raise HTTPException(
                status_code=HttpStatus.NOT_FOUND,
                detail={
                    "success": False,
                    "statusCode": HttpStatus.NOT_FOUND,
                    "message": ErrorMessages.VEHICLE_NOT_FOUND,
                    "error": {
                        "code": ErrorCodes.VEHICLE_NOT_FOUND,
                        "details": f"Vehículo con ID {vehiculo_id} no existe"
                    }
                }
            )
        
        return {"message": SuccessMessages.VEHICLE_DELETED}
    
    def update_estado(self, vehiculo_id: int, nuevo_estado: str) -> Vehiculo:
        if nuevo_estado not in VehicleStatus.ALLOWED:
            raise HTTPException(
                status_code=HttpStatus.BAD_REQUEST,
                detail={
                    "success": False,
                    "statusCode": HttpStatus.BAD_REQUEST,
                    "message": "Datos inválidos",
                    "error": {
                        "code": ErrorCodes.INVALID_DATA,
                        "details": ErrorMessages.INVALID_STATUS
                    }
                }
            )
        
        estado_enum = EstadoVehiculo(nuevo_estado)
        updated = self.repo.update_estado(vehiculo_id, estado_enum)
        
        if not updated:
            raise HTTPException(
                status_code=HttpStatus.NOT_FOUND,
                detail={
                    "success": False,
                    "statusCode": HttpStatus.NOT_FOUND,
                    "message": ErrorMessages.VEHICLE_NOT_FOUND,
                    "error": {
                        "code": ErrorCodes.VEHICLE_NOT_FOUND,
                        "details": f"Vehículo con ID {vehiculo_id} no existe"
                    }
                }
            )
        
        return updated