from typing import List
from fastapi import HTTPException
from app.domain.vehiculo_domain import Vehiculo, VehiculoCreate, EstadoVehiculo
from app.repository.vehiculo_repository import VehiculoRepository


class VehiculoService:
    
    def __init__(self, repo: VehiculoRepository):
        self.repo = repo
    
    def get_all_vehiculos(self) -> List[Vehiculo]:
        return self.repo.get_all()
    
    def get_vehiculo(self, vehiculo_id: int) -> Vehiculo:
        vehiculo = self.repo.get_by_id(vehiculo_id)
        
        if not vehiculo:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": "Vehículo no encontrado",
                    "error": {
                        "code": "VEHICLE_NOT_FOUND",
                        "details": f"Vehículo con ID {vehiculo_id} no existe"
                    }
                }
            )
        return vehiculo
    
    def create_vehiculo(self, data: VehiculoCreate) -> Vehiculo:
        # Validar tipo
        tipos_permitidos = ["carro", "moto", "bicicleta"]
        if data.tipo not in tipos_permitidos:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Datos inválidos",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": f"El tipo debe ser uno de: {', '.join(tipos_permitidos)}"
                    }
                }
            )
        
        # Validar tarifaPorHora > 0
        if data.tarifaPorHora <= 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Datos inválidos",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": "La tarifa por hora debe ser mayor a 0"
                    }
                }
            )
        
        # Verificar que el vehículo no exista
        existing = self.repo.get_by_modelo(data.modelo)
        if existing:
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
        
        # Crear el vehículo
        new_vehiculo = self.repo.create(data)
        
        if not new_vehiculo:
            raise HTTPException(
                status_code=503,
                detail={
                    "success": False,
                    "statusCode": 503,
                    "message": "Error de conexión a la base de datos",
                    "error": {
                        "code": "DB_CONNECTION_ERROR",
                        "details": "No se pudo completar la operación"
                    }
                }
            )
        
        return new_vehiculo
    
    def delete_vehiculo(self, vehiculo_id: int) -> dict:
        deleted = self.repo.delete(vehiculo_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": "Vehículo no encontrado",
                    "error": {
                        "code": "VEHICLE_NOT_FOUND",
                        "details": f"Vehículo con ID {vehiculo_id} no existe"
                    }
                }
            )
        
        return {"message": "Vehículo eliminado correctamente"}
    
    def update_estado(self, vehiculo_id: int, nuevo_estado: str) -> Vehiculo:
        estados_permitidos = ["disponible", "en_uso", "mantenimiento"]
        if nuevo_estado not in estados_permitidos:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "statusCode": 400,
                    "message": "Datos inválidos",
                    "error": {
                        "code": "INVALID_DATA",
                        "details": f"Estado inválido. Permitidos: {', '.join(estados_permitidos)}"
                    }
                }
            )
        
        updated = self.repo.update_estado(vehiculo_id, nuevo_estado)
        
        if not updated:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "statusCode": 404,
                    "message": "Vehículo no encontrado",
                    "error": {
                        "code": "VEHICLE_NOT_FOUND",
                        "details": f"Vehículo con ID {vehiculo_id} no existe"
                    }
                }
            )
        
        return updated